# encoding: utf-8

import time
import typing as tp

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class Driver4(object):
    """

    """
    COMMON_INTERVAL = 1
    COMMON_IMPLICITLY_TIMEOUT = 30

    def __init__(self):
        self._: tp.Optional[webdriver.Chrome] = None
        self.action: tp.Optional[ActionChains] = None

    def open(self, url: str, chromedriver_path: str):
        """
        打开浏览器，定位到url
        :param url:
        :param chromedriver_path: 对标的chromedriver.exe的绝对路径
        :return:
        """
        self._ = webdriver.Chrome(
            service=Service(chromedriver_path)
        )
        self.action = ActionChains(self._)
        self._.get(url)
        # 默认最大化
        self._.maximize_window()
        time.sleep(self.COMMON_INTERVAL)
        return self._

    def quit(self):
        self._.quit()

    def find_element(self, identity: str, timeout: float = 3, ) -> WebElement:
        """
        寻找控件，若没找到，则抛出异常（还是返回None）
        :param identity: 控件标识（目前只支持xpath，如果后续要支持其他标识的话，可在该函数以及所有调用本函数的本类函数中，添加by参数）
        :param timeout: 超时时间，如果超过该时间还没找到控件，则抛出异常（还是返回None）
        :return:
        """
        element = WebDriverWait(self._, timeout).until(
            expected_conditions.visibility_of_element_located(
                (By.XPATH, identity)
            )
        )
        return element

    def find_elements(self, identity: str, timeout: float = 3, ) -> tp.List[WebElement]:
        """
        寻找所有符合条件的控件，若没找到，则抛出异常（还是返回None）
        :param identity:
        :param timeout: 这个参数其实没有什么用，代码合并的时候考虑去掉。有超时时间的函数必须要有明确的结束条件，但寻找所有的函数没有这个条件。
        :return:
        """
        return self._.find_elements(By.XPATH, identity)

    def is_element_exist(self, identity: str, timeout: float = 3):
        """检查元素是否存在（支持多个元素匹配）
        :param identity: 元素定位表达式
        :param timeout: 等待超时时间
        :return: 存在至少一个元素返回True，否则False
        """
        try:
            # 使用 presence_of_all_elements_located 代替 visibility_of_element_located
            elements = WebDriverWait(self._, timeout).until(
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, identity)
                )
            )
            return len(elements) > 0
        except Exception as e:
            return False

    def click(self, identity: str, timeout: float = 3, ):
        """
        鼠标左键单击控件
        :param identity:
        :param timeout:
        :return:
        """
        self.find_element(identity, timeout).click()
        time.sleep(self.COMMON_INTERVAL)

    def set_value(self, identity: str, val: str, timeout: float = 3):
        """
        给input textarea等可输入控件输入值
        这里加了一个不合适的操作（就是如果这个input里有一个×的话，会去点一下这个×，这个是给组态树用的，免得输入的内容变成追加输入）
        这个写法不应该再基础驱动模块，应该在产品驱动模块或控件驱动模块，之前实习生写冒烟的时候加上的，在很多地方都有使用，暂时我也懒得去改了。
        这里标记一下
        :param identity: 控件的定位符，xpath
        :param val: 要输入的值
        :param timeout: 超时时间
        :return:
        """
        # self.find_element(identity, timeout).send_keys(val)
        # time.sleep(0.5)

        # 如果有内容就先清空
        # if self.is_element_exist(
        #         identity + '/..//span[contains(@class, "input-clear-icon") and not(contains(@class, "hidden"))]', 2):
        #     self.click(identity + '/..//span[contains(@class, "input-clear-icon") and not(contains(@class, "hidden"))]')
        # if not self.is_element_exist(identity + '/..//span[contains(@class, "input-clear-icon-hidden")]', 1):
        #     if self.is_element_exist(identity + '/..//span[contains(@class, "input-clear-icon")]'):
        #         self.click(identity + '/..//span[contains(@class, "input-clear-icon")]')

        input_element = self.find_element(identity, timeout)
        self.action.click(input_element) \
            .key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL) \
            .send_keys(Keys.BACKSPACE) \
            .perform()
        input_element.send_keys(val)
        time.sleep(self.COMMON_INTERVAL)

    def set_value_by_select_all(self, identity: str, val: str, timeout: float = 3):
        """
        另一种非追加输入的方式
        双击全选，输入。这个时候大部分标准控件都会覆盖掉原来的值。
        （我见过有些控件双击是没有用的，遇到再说吧）
        """
        input_element = self.find_element(identity, timeout)
        self.double_click(identity)
        input_element.send_keys(val)
        time.sleep(self.COMMON_INTERVAL)

    def set_multiple_value(self, identity: str, val: str, timeout: float = 3):
        """
        在指定的输入框中设置多行值。（还没验证过，因为没用到了）

        :param identity: 输入框的定位符
        :param val: 要输入的值，可以是多行字符串
        :param timeout: 查找元素的超时时间
        :return: None
        """
        input_element = self.find_element(identity, timeout)
        input_element.clear()

        # 将多行字符串分割成行，并逐行输入
        for line in val.splitlines():
            input_element.send_keys(line)
            input_element.send_keys(Keys.ENTER)  # 使用 Enter 键来输入换行符

            time.sleep(self.COMMON_INTERVAL)

        time.sleep(self.COMMON_INTERVAL)

    def double_click(self, identity: str, timeout: float = 3, ):
        """
        左键双击
        [设计理念] 按上一个版本的设计，所有的点击会设计成click(button_type, click_time)，一个函数搞定左右键、单双三击
        改动的理由是：驱动是给测试用例用的，测试用例是给人看的，double_click和right_click的观感要好于click(1, 2)和click(2, 1)
        :param identity:
        :param timeout:
        :return:
        """
        element = self.find_element(identity, timeout)
        actions = ActionChains(self._)
        actions.double_click(element)
        actions.perform()
        time.sleep(self.COMMON_INTERVAL)

    def right_click(self, identity: str, timeout: float = 3, ):
        """
        右键单击
        :param identity:
        :param timeout:
        :return:
        """
        element = self.find_element(identity, timeout)
        actions = ActionChains(self._)
        actions.context_click(element)
        actions.perform()
        time.sleep(self.COMMON_INTERVAL)

    def click_xy(self, identity: str, x: int, y: int, mode: int = 0, timeout: float = 3):
        """
        鼠标点击距离该控件的相对坐标(x, y)的位置
        可以看到这里右保留了mode参数，一个函数搞定不动的点击操作了，是因为这个函数不是常用函数(目前应该只有canvas会用到)
        :param identity:
        :param x:
        :param y:
        :param mode: 0鼠标左键单击|1鼠标右键单击|2鼠标左键双击
        :param timeout:
        :return:
        """
        element = self.find_element(identity, timeout)
        actions = ActionChains(self._)
        if mode == 0:
            actions.move_to_element_with_offset(element, x, y).click().perform()
        elif mode == 1:
            actions.move_to_element_with_offset(element, x, y).context_click().perform()
        elif mode == 2:
            actions.move_to_element_with_offset(element, x, y).double_click().perform()
        else:
            raise NotImplementedError
        time.sleep(self.COMMON_INTERVAL)

    def switch_to_iframe(self,
                         s=None,
                         to_default_content=False
                         ):
        """
        切换到指定iframe 或切换回默认主iframe
        :param s: 支持对象实例、xpath路径字符串，是iframe的
        :param to_default_content: 是否为切换回默认主iframe
        """
        if to_default_content:
            self._.switch_to.default_content()
        else:
            if type(s) == WebElement:
                elem = s
            else:
                elem = self.find_element(s)
            self._.switch_to.frame(elem)

        time.sleep(self.COMMON_INTERVAL)

    def move_to_target_with_offset(self, element, x, y):
        self.action.move_to_element_with_offset(element, x, y)
        return self.action

    def scroll_to_target_element(self, start: WebElement, end: WebElement):
        self.action.move_to_element(start).click().scroll_to_element(end).move_to_element(end).perform()



if __name__ == "__main__":
    d = Driver4()
    driver_path = "f:\\chrome144\\chromedriver.exe"
    d.open("http://10.16.11.45:31501/tpt-app/#/home/chat/main", driver_path)
    input()