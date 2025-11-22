# encoding: utf-8

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class EasySelenium4:
    """Selenium 二次封装类，简化常用操作"""
    
    # 操作函数的等待超时时间（秒）
    OPERATION_TIMEOUT = 5
    
    def __init__(self, driver_path=None, wait_timeout=10):
        """
        初始化 Selenium 助手类
        
        Args:
            driver_path: ChromeDriver 路径，如果为 None 则使用系统 PATH 中的驱动
            wait_timeout: 默认等待超时时间（秒）
        """
        self.driver = None
        self.wait_timeout = wait_timeout
        self.driver_path = driver_path
    
    def open_browser(self, maximize=True):
        """
        打开浏览器
        
        Args:
            maximize: 是否最大化窗口，默认 True
        
        Returns:
            self: 返回自身，支持链式调用
        """
        if self.driver_path:
            service = Service(executable_path=self.driver_path)
            self.driver = webdriver.Chrome(service=service)
        else:
            self.driver = webdriver.Chrome()
        
        if maximize:
            self.driver.maximize_window()
        
        return self
    
    def open_url(self, url):
        """
        打开指定 URL
        
        Args:
            url: 要打开的网页地址
        
        Returns:
            self: 返回自身，支持链式调用
        """
        if not self.driver:
            raise Exception("请先调用 open_browser() 打开浏览器")
        self.driver.get(url)
        return self
    
    def find_element(self, value, wait_clickable=False, wait_visible=False, timeout=None):
        """
        查找单个元素（通过 XPath）
        
        Args:
            value: XPath 表达式
            wait_clickable: 是否等待元素可点击，默认 False
            wait_visible: 是否等待元素可见，默认 False
            timeout: 等待超时时间（秒），如果为 None 则使用默认超时时间
        
        Returns:
            WebElement: 找到的元素对象
        """
        if not self.driver:
            raise Exception("请先调用 open_browser() 打开浏览器")
        
        wait_time = timeout if timeout is not None else self.wait_timeout
        wait = WebDriverWait(self.driver, wait_time)
        
        if wait_clickable:
            return wait.until(EC.element_to_be_clickable((By.XPATH, value)))
        elif wait_visible:
            return wait.until(EC.visibility_of_element_located((By.XPATH, value)))
        else:
            return wait.until(EC.presence_of_element_located((By.XPATH, value)))
    
    def find_elements(self, value):
        """
        查找多个元素（通过 XPath）
        
        Args:
            value: XPath 表达式
        
        Returns:
            list: 找到的元素列表
        """
        if not self.driver:
            raise Exception("请先调用 open_browser() 打开浏览器")
        
        wait = WebDriverWait(self.driver, self.wait_timeout)
        return wait.until(EC.presence_of_all_elements_located((By.XPATH, value)))
    
    def click(self, value, wait_clickable=False):
        """
        点击元素（通过 XPath）
        如果元素不存在，会等待最多 5 秒直到元素出现
        
        Args:
            value: XPath 表达式
            wait_clickable: 是否等待元素可点击，默认 False（如果为 False，则等待元素可见）
        
        Returns:
            self: 返回自身，支持链式调用
        """
        if wait_clickable:
            elem = self.find_element(value, wait_clickable=True, timeout=self.OPERATION_TIMEOUT)
        else:
            elem = self.find_element(value, wait_visible=True, timeout=self.OPERATION_TIMEOUT)
        elem.click()
        return self
    
    def double_click(self, value):
        """
        双击元素（通过 XPath）
        如果元素不存在，会等待最多 5 秒直到元素出现
        
        Args:
            value: XPath 表达式
        
        Returns:
            self: 返回自身，支持链式调用
        """
        elem = self.find_element(value, wait_visible=True, timeout=self.OPERATION_TIMEOUT)
        ActionChains(self.driver).double_click(elem).perform()
        return self
    
    def right_click(self, value):
        """
        右键点击元素（通过 XPath）
        如果元素不存在，会等待最多 5 秒直到元素出现
        
        Args:
            value: XPath 表达式
        
        Returns:
            self: 返回自身，支持链式调用
        """
        elem = self.find_element(value, wait_visible=True, timeout=self.OPERATION_TIMEOUT)
        ActionChains(self.driver).context_click(elem).perform()
        return self
    
    def set_text(self, value, text="", clear_first=True):
        """
        设置元素文本（通过 XPath）
        如果元素不存在，会等待最多 5 秒直到元素出现
        
        Args:
            value: XPath 表达式
            text: 要输入的文本
            clear_first: 是否先清空输入框，默认 True
        
        Returns:
            self: 返回自身，支持链式调用
        """
        elem = self.find_element(value, wait_visible=True, timeout=self.OPERATION_TIMEOUT)
        if clear_first:
            elem.clear()
        elem.send_keys(text)
        return self
    
    def quit(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句，自动关闭浏览器"""
        self.quit()

