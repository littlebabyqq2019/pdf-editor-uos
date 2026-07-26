"""将PNG图片转换为ICO图标"""
from PIL import Image
import os

# 读取PNG图片
png_path = '1.png'
ico_path = 'app_icon.ico'

try:
    # 打开PNG图片
    img = Image.open(png_path)
    
    # 转换为RGBA模式
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # 创建多个尺寸的图标（Windows标准）
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    # 保存为ICO格式
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    
    print(f"[SUCCESS] Created icon file: {ico_path}")
    print(f"  Sizes: {', '.join([f'{s[0]}x{s[1]}' for s in icon_sizes])}")
    
except Exception as e:
    print(f"[ERROR] Failed to create icon: {e}")

