import mss
import mss.tools
import os
from datetime import datetime

def screenshot_with_mss(
    save_path: str = None,
    region: tuple = None  # 可选：指定截图区域 (left, top, width, height)
):
    """
    使用 mss 库实现屏幕截图
    :param save_path: 保存路径（默认：当前目录/截图_时间戳.png）
    :param region: 截图区域（left, top, width, height），None 表示全屏
    """
    # 初始化截图对象
    with mss.mss() as sct:
        # 配置截图参数
        monitor = sct.monitors[1]  # 1 = 主显示器（0 = 所有显示器合并）
        if region:
            # 若指定区域，覆盖默认显示器参数（left, top, width, height）
            monitor["left"] = region[0]
            monitor["top"] = region[1]
            monitor["width"] = region[2]
            monitor["height"] = region[3]

        # 执行截图
        sct_img = sct.grab(monitor)

        # 生成默认保存路径（避免覆盖）
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(os.getcwd(), f"截图_{timestamp}.png")

        # 保存截图（两种方式）
        # 方式1：直接保存为 PNG（推荐，无压缩）
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=save_path)

        # 方式2：若需保存为 JPG，用 pillow 转换（需安装 pillow）
        # from PIL import Image
        # img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
        # img.save(save_path.replace(".png", ".jpg"), quality=95)

        print(f"截图已保存到：{save_path}")
        return save_path

# ------------------- 调用示例 -------------------
if __name__ == "__main__":
    # 示例1：全屏截图（保存到默认路径）
    # screenshot_with_mss()

    # 示例2：指定区域截图（left=100, top=100, width=800, height=600）
    # screenshot_with_mss(region=(100, 100, 800, 600))

    # 示例3：自定义保存路径（保存为 D:\test\my_screenshot.png）
    screenshot_with_mss(region=(2300, 500, 1400, 1400), save_path=r"D:\my_screenshot.png")