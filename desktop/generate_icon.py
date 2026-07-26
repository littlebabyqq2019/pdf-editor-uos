#!/usr/bin/env python3
import argparse
from pathlib import Path
from PIL import Image, ImageDraw


def create_icon(output_png: Path, output_ico: Path | None = None) -> None:
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 深蓝色背景圆角矩形
    margin = 24
    draw.rounded_rectangle((margin, margin, size - margin, size - margin), radius=48, fill=(18, 97, 191, 255))

    # 白色文档图标
    draw.rounded_rectangle((70, 58, 186, 198), radius=18, fill=(255, 255, 255, 255))
    draw.rectangle((92, 86, 164, 176), fill=(18, 97, 191, 255))
    draw.rectangle((96, 92, 160, 100), fill=(255, 255, 255, 255))
    draw.rectangle((96, 114, 160, 122), fill=(255, 255, 255, 255))
    draw.rectangle((96, 136, 160, 144), fill=(255, 255, 255, 255))

    output_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_png, format='PNG')
    if output_ico is not None:
        output_ico.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_ico, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate desktop icon files for PDF editor')
    parser.add_argument('--png', default='desktop/icons/pdf-editor.png')
    parser.add_argument('--ico', default='desktop/icons/pdf-editor.ico')
    args = parser.parse_args()

    create_icon(Path(args.png), Path(args.ico) if args.ico else None)
    print(f'Generated icon: {args.png}')
    if args.ico:
        print(f'Generated icon: {args.ico}')
