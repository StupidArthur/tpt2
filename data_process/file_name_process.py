# encoding: utf-8

import re

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除Windows不允许的字符"""
    # Windows不允许的字符: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    # 替换为下划线
    sanitized = re.sub(invalid_chars, '_', filename)
    # 移除首尾空格和点号
    sanitized = sanitized.strip(' .')
    return sanitized