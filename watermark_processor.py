"""PDF 水印处理器

支持在 PDF 文件的每一页添加自定义水印。
水印支持：文字内容、字号、颜色、透明度、旋转角度、密度（平铺）。
"""

import os
import io
from typing import List, Dict, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import PyPDF2
from PIL import Image, ImageDraw, ImageFont


class WatermarkProcessor:
    """PDF 水印处理器"""

    def __init__(self):
        # 注册中文字体（微软雅黑）
        self._register_chinese_fonts()

    def _register_chinese_fonts(self):
        """注册中文字体"""
        import platform

        font_paths = []
        if platform.system() == 'Windows':
            font_paths = [
                r'C:\Windows\Fonts\msyh.ttc',      # 微软雅黑
                r'C:\Windows\Fonts\simhei.ttf',    # 黑体
                r'C:\Windows\Fonts\simsun.ttc',    # 宋体
            ]
        elif platform.system() == 'Darwin':  # macOS
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Medium.ttc',
            ]
        else:  # Linux
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
            ]

        # 保存字体路径列表供PIL使用
        self.chinese_fonts = font_paths

        # 尝试注册第一个可用的字体（供ReportLab使用）
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # TTF 格式直接注册
                    if font_path.endswith('.ttf'):
                        pdfmetrics.registerFont(TTFont('CustomChinese', font_path))
                        print(f'[INFO] 成功注册中文字体: {font_path}')
                        return
                    # TTC 格式需要指定字体索引
                    elif font_path.endswith('.ttc'):
                        # 尝试索引 0（通常是 Regular 字体）
                        pdfmetrics.registerFont(TTFont('CustomChinese', font_path, subfontIndex=0))
                        print(f'[INFO] 成功注册中文字体: {font_path}')
                        return
                except Exception as e:
                    print(f'[WARN] 注册字体失败 ({font_path}): {e}')
                    continue

        print('[WARN] 未找到可用的中文字体，水印可能无法显示中文')

    def create_watermark_image(
        self,
        text: str,
        font_size: int = 40,
        color: str = '#CCCCCC',
        opacity: float = 0.3,
        rotation: int = 45
    ):
        """
        创建单个水印文字的PIL图片（透明背景，不可复制）

        Args:
            text: 水印文字
            font_size: 字号
            color: 颜色（十六进制，如 #FF0000）
            opacity: 透明度（0-1）
            rotation: 旋转角度（0-360）

        Returns:
            PIL Image对象
        """
        # 解析颜色
        try:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            alpha = int(opacity * 255)
            rgba_color = (r, g, b, alpha)
        except:
            rgba_color = (204, 204, 204, int(opacity * 255))

        # 加载字体
        font = None
        for font_path in self.chinese_fonts:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue

        if font is None:
            try:
                font = ImageFont.truetype('arial.ttf', font_size)
            except:
                font = ImageFont.load_default()

        # 创建临时图片计算文字尺寸
        temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 计算旋转后的画布尺寸（需要更大的空间容纳旋转后的文字）
        import math
        angle_rad = math.radians(rotation)
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))
        canvas_width = int(text_width * cos_a + text_height * sin_a) + 40
        canvas_height = int(text_width * sin_a + text_height * cos_a) + 40

        # 创建透明背景图片
        img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 在中心绘制文字
        text_x = (canvas_width - text_width) // 2
        text_y = (canvas_height - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=rgba_color)

        # 旋转图片
        # 注意：PIL 的 rotate() 是按视觉逆时针旋转（与 PDF 画布坐标系方向一致）
        # 由于 drawImage 会保持图片的正常视觉朝向嵌入 PDF，这里直接使用 rotation
        # （不能取反，否则会导致镜像翻转，出现 90 度偏差等异常）
        if rotation != 0:
            img = img.rotate(rotation, expand=False, fillcolor=(0, 0, 0, 0))

        return img

    def create_watermark_page(
        self,
        page_width: float,
        page_height: float,
        text: str,
        font_size: int = 40,
        color: str = '#CCCCCC',
        opacity: float = 0.3,
        rotation: int = 45,
        density: int = 3
    ) -> bytes:
        """
        创建水印页（使用图片方式，防止文字被复制）

        Args:
            page_width: 页面宽度（点）
            page_height: 页面高度（点）
            text: 水印文字
            font_size: 字号
            color: 颜色（十六进制，如 #FF0000）
            opacity: 透明度（0-1）
            rotation: 旋转角度（0-360）
            density: 密度（1-10，数字越大水印越密集）

        Returns:
            水印 PDF 的字节数据
        """
        # 创建单个水印图片
        watermark_img = self.create_watermark_image(text, font_size, color, opacity, rotation)

        # 创建PDF画布
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=(page_width, page_height))

        # 计算水印间距
        x_spacing = page_width / (density + 1)
        y_spacing = page_height / (density + 1)

        # 将PIL图片转为ReportLab可用的ImageReader
        img_buffer = io.BytesIO()
        watermark_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_reader = ImageReader(img_buffer)

        img_width, img_height = watermark_img.size

        # 平铺水印图片
        for i in range(density + 1):
            for j in range(density + 1):
                x = x_spacing * (i + 0.5) - img_width / 2
                y = y_spacing * (j + 0.5) - img_height / 2

                # 绘制图片（mask='auto'保留透明度）
                c.drawImage(img_reader, x, y, width=img_width, height=img_height,
                           mask='auto', preserveAspectRatio=True)

        c.save()
        packet.seek(0)
        return packet.getvalue()

    def add_watermark(
        self,
        input_pdf_path: str,
        output_pdf_path: str,
        watermark_config: Dict[str, Any]
    ) -> bool:
        """
        为 PDF 添加水印

        Args:
            input_pdf_path: 输入 PDF 路径
            output_pdf_path: 输出 PDF 路径
            watermark_config: 水印配置，包含：
                - text: 水印文字
                - font_size: 字号（默认 40）
                - color: 颜色（默认 #CCCCCC）
                - opacity: 透明度（默认 0.3）
                - rotation: 旋转角度（默认 45）
                - density: 密度（默认 3）

        Returns:
            是否成功
        """
        try:
            # 读取原始 PDF
            with open(input_pdf_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()

                # 为每一页添加水印
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)

                    # 创建水印页
                    watermark_bytes = self.create_watermark_page(
                        page_width,
                        page_height,
                        watermark_config.get('text', '水印'),
                        watermark_config.get('font_size', 40),
                        watermark_config.get('color', '#CCCCCC'),
                        watermark_config.get('opacity', 0.3),
                        watermark_config.get('rotation', 45),
                        watermark_config.get('density', 3)
                    )

                    # 将水印叠加到原页面
                    watermark_pdf = PyPDF2.PdfReader(io.BytesIO(watermark_bytes))
                    watermark_page = watermark_pdf.pages[0]
                    page.merge_page(watermark_page)

                    pdf_writer.add_page(page)

                # 写入输出文件
                with open(output_pdf_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

            return True

        except Exception as e:
            print(f'[ERROR] 添加水印失败: {e}')
            import traceback
            traceback.print_exc()
            return False

    def batch_add_watermarks(
        self,
        input_pdf_path: str,
        output_dir: str,
        watermark_presets: List[Dict[str, Any]]
    ) -> List[str]:
        """
        批量添加多个水印，每个水印生成一份独立 PDF

        Args:
            input_pdf_path: 输入 PDF 路径
            output_dir: 输出目录
            watermark_presets: 水印预设列表，每个预设包含：
                - name: 水印名称（用于文件名）
                - text: 水印文字
                - font_size, color, opacity, rotation, density

        Returns:
            成功生成的文件名列表
        """
        os.makedirs(output_dir, exist_ok=True)

        original_filename = os.path.basename(input_pdf_path)
        name_without_ext = os.path.splitext(original_filename)[0]

        generated_files = []

        for preset in watermark_presets:
            watermark_name = preset.get('name', '水印')
            output_filename = f'{watermark_name}-{original_filename}'
            output_path = os.path.join(output_dir, output_filename)

            success = self.add_watermark(input_pdf_path, output_path, preset)

            if success:
                generated_files.append(output_filename)
                print(f'[INFO] 已生成水印文件: {output_filename}')
            else:
                print(f'[ERROR] 生成水印文件失败: {output_filename}')

        return generated_files

    def add_single_watermark(
        self,
        input_pdf_path: str,
        output_pdf_path: str,
        watermark_preset: Dict[str, Any]
    ) -> bool:
        """
        添加单个水印到PDF文件

        Args:
            input_pdf_path: 输入 PDF 路径
            output_pdf_path: 输出 PDF 路径（完整路径，包含文件名）
            watermark_preset: 水印预设配置

        Returns:
            成功返回True，失败返回False
        """
        return self.add_watermark(input_pdf_path, output_pdf_path, watermark_preset)

    def add_watermark_to_image(
        self,
        input_image_path: str,
        output_image_path: str,
        watermark_preset: Dict[str, Any]
    ) -> bool:
        """
        为图片添加水印并保持原格式输出

        Args:
            input_image_path: 输入图片路径（jpg、png等）
            output_image_path: 输出图片路径（完整路径，包含文件名，保持原格式）
            watermark_preset: 水印预设配置

        Returns:
            成功返回True，失败返回False
        """
        try:
            # 读取原始图片
            img = Image.open(input_image_path)
            original_mode = img.mode
            original_format = img.format or 'PNG'

            # 转换为RGBA模式以支持透明度
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 获取图片尺寸
            img_width, img_height = img.size

            # 提取水印参数
            text = watermark_preset.get('text', '水印')
            font_size = watermark_preset.get('font_size', 40)
            color = watermark_preset.get('color', '#CCCCCC')
            opacity = watermark_preset.get('opacity', 0.3)
            rotation = watermark_preset.get('rotation', 45)
            density = watermark_preset.get('density', 3)

            # 创建单个水印文字图片
            watermark_img = self.create_watermark_image(text, font_size, color, opacity, rotation)
            wm_width, wm_height = watermark_img.size

            # 图片水印缩放系数：让图片水印与PDF水印大小一致
            # PDF使用72 DPI基准，而大多数图片是150-300 DPI
            # 通过计算图片与A4纸（595x842点）的比例来动态调整
            # 假设典型A4扫描图片约为 1754x2480 像素（210x297mm @ 200 DPI）
            scale_factor = max(img_width / 595, img_height / 842)

            # 缩放水印图片
            scaled_wm_width = int(wm_width * scale_factor)
            scaled_wm_height = int(wm_height * scale_factor)
            watermark_img_scaled = watermark_img.resize(
                (scaled_wm_width, scaled_wm_height),
                Image.Resampling.LANCZOS
            )

            # 创建透明图层用于放置水印
            watermark_layer = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))

            # 使用与PDF相同的密度计算方式
            x_spacing = img_width / (density + 1)
            y_spacing = img_height / (density + 1)

            # 平铺水印（与PDF逻辑一致）
            for i in range(density + 1):
                for j in range(density + 1):
                    x = int(x_spacing * (i + 0.5) - scaled_wm_width / 2)
                    y = int(y_spacing * (j + 0.5) - scaled_wm_height / 2)
                    watermark_layer.paste(watermark_img_scaled, (x, y), watermark_img_scaled)

            # 合成原图和水印层
            watermarked_img = Image.alpha_composite(img, watermark_layer)

            # 根据输出文件扩展名决定保存格式
            output_ext = os.path.splitext(output_image_path)[1].lower()

            # 如果输出格式是JPEG，需要转换为RGB（JPEG不支持透明度）
            if output_ext in ['.jpg', '.jpeg']:
                # 创建白色背景
                rgb_img = Image.new('RGB', watermarked_img.size, (255, 255, 255))
                rgb_img.paste(watermarked_img, mask=watermarked_img.split()[3])  # 使用alpha通道作为mask
                rgb_img.save(output_image_path, 'JPEG', quality=95)
            elif output_ext == '.png':
                watermarked_img.save(output_image_path, 'PNG')
            elif output_ext in ['.bmp', '.tiff', '.tif']:
                # BMP和TIFF也需要转RGB
                rgb_img = Image.new('RGB', watermarked_img.size, (255, 255, 255))
                rgb_img.paste(watermarked_img, mask=watermarked_img.split()[3])
                if output_ext == '.bmp':
                    rgb_img.save(output_image_path, 'BMP')
                else:
                    rgb_img.save(output_image_path, 'TIFF')
            else:
                # 默认保存为PNG
                watermarked_img.save(output_image_path, 'PNG')

            print(f'[INFO] 图片水印添加成功: {output_image_path}')
            print(f'[INFO] 图片尺寸: {img_width}x{img_height}, 水印缩放: {scale_factor:.2f}x')
            return True

        except Exception as e:
            print(f'[ERROR] 图片水印添加失败: {e}')
            import traceback
            traceback.print_exc()
            return False

