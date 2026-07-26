import os
import cv2
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import zipfile
from datetime import datetime
import io
import fitz  # PyMuPDF
from skimage.filters import threshold_sauvola
from skimage.morphology import thin

class ImageProcessor:
    def __init__(self, upload_folder='uploads', processed_folder='processed'):
        self.upload_folder = upload_folder
        self.processed_folder = processed_folder
    
    def remove_background(self, session_id, files):
        """去背景处理"""
        try:
            processed_files = []
            processed_dir = os.path.join(self.processed_folder, session_id)
            os.makedirs(processed_dir, exist_ok=True)
            
            for file_info in files:
                if file_info['type'] == '扫描型PDF':
                    input_path = os.path.join(self.upload_folder, session_id, file_info['filename'])
                    output_filename = f"去背景-{file_info['filename']}"
                    output_path = os.path.join(processed_dir, output_filename)
                    
                    self._remove_background_from_pdf(input_path, output_path)
                    processed_files.append(output_filename)
            
            if len(processed_files) == 1:
                return {'success': True, 'download_file': processed_files[0]}
            elif len(processed_files) > 1:
                zip_filename = '去背景.zip'
                zip_path = os.path.join(processed_dir, zip_filename)
                self._create_zip(processed_dir, processed_files, zip_path)
                return {'success': True, 'download_file': zip_filename}
            else:
                return {'error': '没有可处理的扫描型PDF文件'}
                
        except Exception as e:
            return {'error': f'处理失败: {str(e)}'}
    
    def images_to_pdf(self, session_id, files):
        """图片转PDF"""
        try:
            processed_dir = os.path.join(self.processed_folder, session_id)
            os.makedirs(processed_dir, exist_ok=True)
            
            # 筛选图片文件
            image_files = [f for f in files if f['type'] == 'image']
            
            if not image_files:
                return {'error': '没有图片文件需要转换'}
            
            # 生成文件名
            today = datetime.now().strftime('%Y%m%d')
            counter = 1
            
            # 检查当天已有的文件数量
            while True:
                filename = f"{today}{counter:02d}.pdf"
                output_path = os.path.join(processed_dir, filename)
                if not os.path.exists(output_path):
                    break
                counter += 1
            
            # 转换图片为PDF
            self._convert_images_to_pdf(session_id, image_files, output_path)
            
            return {'success': True, 'download_file': filename}
            
        except Exception as e:
            return {'error': f'处理失败: {str(e)}'}
    
    def _remove_background_from_pdf(self, input_path, output_path):
        """从PDF中去除背景并进行优化处理"""
        doc = fitz.open(input_path)
        new_doc = fitz.open()
        
        print(f"[INFO] 开始处理PDF: {input_path}, 共 {len(doc)} 页")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"[INFO] 处理第 {page_num + 1}/{len(doc)} 页...")
            
            # 使用更高分辨率进行处理，提升输出质量
            # 使用3.0倍缩放以获得更好的细节，适合文档扫描
            mat = fitz.Matrix(3.0, 3.0)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # 使用OpenCV处理图片
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                print(f"[WARNING] 第 {page_num + 1} 页图像解码失败，跳过")
                continue
            
            print(f"[DEBUG] 原始图像尺寸: {img.shape}")
            
            # 去除背景并进行优化处理
            img_processed = self._clean_background(img)
            
            print(f"[DEBUG] 处理后图像尺寸: {img_processed.shape}")
            
            # ========== 将处理后的图片居中放置到白色A4背景 ==========
            # A4尺寸（300 DPI）：2480 x 3508 像素
            a4_width_px = 2480
            a4_height_px = 3508
            
            # 获取处理后图片的尺寸
            proc_h, proc_w = img_processed.shape[:2]
            
            # 计算缩放比例，使图片充分利用A4页面（保留边距）
            # 留出上下左右各1cm边距（300DPI下约118像素）
            margin_px = 118
            available_width = a4_width_px - 2 * margin_px
            available_height = a4_height_px - 2 * margin_px
            
            # 计算缩放比例（保持宽高比）
            # 自动放大或缩小以充分利用A4空间
            scale_w = available_width / proc_w
            scale_h = available_height / proc_h
            scale = min(scale_w, scale_h)  # 取较小的缩放比例，确保不超出边界
            
            # 缩放图片以充分利用A4空间
            new_w = int(proc_w * scale)
            new_h = int(proc_h * scale)
            
            if abs(scale - 1.0) > 0.01:  # 只有缩放超过1%才执行
                if scale > 1.0:
                    # 放大使用INTER_CUBIC（高质量插值）
                    img_processed = cv2.resize(img_processed, (new_w, new_h), 
                                              interpolation=cv2.INTER_CUBIC)
                    print(f"[DEBUG] 放大图片以充分利用A4: {proc_w}x{proc_h} -> {new_w}x{new_h} (放大{scale:.1%})")
                else:
                    # 缩小使用INTER_AREA（最佳缩小算法）
                    img_processed = cv2.resize(img_processed, (new_w, new_h), 
                                              interpolation=cv2.INTER_AREA)
                    print(f"[DEBUG] 缩小图片以适应A4: {proc_w}x{proc_h} -> {new_w}x{new_h} (缩小到{scale:.1%})")
            else:
                print(f"[DEBUG] 图片尺寸已适合A4，无需缩放")
            
            # 创建白色A4背景
            a4_background = np.ones((a4_height_px, a4_width_px, 3), dtype=np.uint8) * 255
            
            # 计算居中位置
            x_offset = (a4_width_px - new_w) // 2
            y_offset = (a4_height_px - new_h) // 2
            
            # 将处理后的图片放置到A4背景中心
            a4_background[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = img_processed
            
            print(f"[DEBUG] 图片已居中放置到A4页面: 位置({x_offset}, {y_offset})")
            
            # 转换回PDF页面，使用高质量JPEG编码
            _, img_encoded = cv2.imencode('.jpg', a4_background, 
                                          [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            img_bytes = img_encoded.tobytes()
            
            # 创建A4页面（72 DPI标准）
            # 将像素转换为点（points）：300 DPI -> 72 DPI
            page_width_pt = a4_width_px * 72 / 300
            page_height_pt = a4_height_px * 72 / 300
            img_rect = fitz.Rect(0, 0, page_width_pt, page_height_pt)
            new_page = new_doc.new_page(width=page_width_pt, height=page_height_pt)
            new_page.insert_image(img_rect, stream=img_bytes)
            
            print(f"[INFO] 第 {page_num + 1} 页处理完成，已居中放置到A4页面")
        
        # 保存处理后的PDF
        print(f"[INFO] 保存处理后的PDF: {output_path}")
        new_doc.save(output_path, garbage=4, deflate=True)
        new_doc.close()
        doc.close()
        print(f"[INFO] PDF处理完成！")
    
    def _clean_background(self, img):
        """优化的文档扫描处理：透视矫正→背景去除→自适应二值化→去噪"""
        
        # ========== 辅助函数定义 ==========
        def order_points(pts):
            """对四个点排序：左上、右上、右下、左下"""
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]  # 左上（和最小）
            rect[2] = pts[np.argmax(s)]  # 右下（和最大）
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]  # 右上（差最小）
            rect[3] = pts[np.argmax(diff)]  # 左下（差最大）
            return rect

        def four_point_transform(image, pts, margin_cm=1.0):
            """四点透视变换，保留指定边距（单位：厘米）
            
            Args:
                image: 输入图像
                pts: 检测到的四个角点
                margin_cm: 边距（厘米），默认1cm
            """
            rect = order_points(pts)
            (tl, tr, br, bl) = rect
            
            # 计算原始宽度和高度
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            
            # 计算边距像素值
            # 假设当前分辨率约为300DPI（1cm ≈ 118像素）
            # 根据图像实际尺寸动态估算DPI
            img_h, img_w = image.shape[:2]
            # A4纸实际尺寸：210mm x 297mm
            # 估算DPI：按较长边估算
            estimated_dpi = max(img_w / 8.27, img_h / 11.69)  # 8.27" = 210mm, 11.69" = 297mm
            margin_pixels = int(margin_cm * estimated_dpi / 2.54)  # 1cm = 2.54英寸的一部分
            print(f"[DEBUG] 估算DPI: {estimated_dpi:.0f}, 边距像素: {margin_pixels}px ({margin_cm}cm)")
            
            # 扩展检测到的边界，向外延伸margin_pixels
            # 计算每个角点向外延伸的方向向量
            img_h, img_w = image.shape[:2]
            
            # 计算中心点
            center = np.mean(rect, axis=0)
            
            # 每个角点向外延伸
            expanded_rect = np.zeros_like(rect)
            for i in range(4):
                # 从中心指向角点的向量
                direction = rect[i] - center
                direction_norm = direction / (np.linalg.norm(direction) + 1e-6)
                # 向外延伸margin_pixels
                expanded_rect[i] = rect[i] + direction_norm * margin_pixels
                # 限制在图像边界内
                expanded_rect[i, 0] = np.clip(expanded_rect[i, 0], 0, img_w - 1)
                expanded_rect[i, 1] = np.clip(expanded_rect[i, 1], 0, img_h - 1)
            
            # 使用扩展后的边界进行透视变换
            # 重新计算宽度和高度
            (tl, tr, br, bl) = expanded_rect
            widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
            widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
            maxWidth = max(int(widthA), int(widthB))
            
            heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
            heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
            maxHeight = max(int(heightA), int(heightB))
            
            # 定义目标点
            dst = np.array([
                [0, 0],
                [maxWidth - 1, 0],
                [maxWidth - 1, maxHeight - 1],
                [0, maxHeight - 1]], dtype="float32")
            
            # 计算透视变换矩阵
            M = cv2.getPerspectiveTransform(expanded_rect, dst)
            warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
            print(f"[DEBUG] 透视变换完成，保留了{margin_cm}cm边距")
            return warped
        
        # ========== 步骤1：增强的文档边缘检测和透视矫正 ==========
        original_img = img.copy()
        img_h, img_w = img.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 多尺度边缘检测，提高检测成功率
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 尝试多个Canny阈值组合
        edged1 = cv2.Canny(blurred, 50, 150)
        edged2 = cv2.Canny(blurred, 75, 200)
        edged = cv2.bitwise_or(edged1, edged2)
        
        # 膨胀操作连接断开的边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edged = cv2.dilate(edged, kernel, iterations=1)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        
        # 查找最大的四边形轮廓
        quad = None
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            if len(approx) == 4:
                # 验证四边形的合理性
                quad_temp = approx.reshape(4, 2).astype("float32")
                img_area = float(img_h * img_w)
                quad_area = cv2.contourArea(approx)
                area_ratio = quad_area / img_area if img_area > 0 else 0.0
                
                # 检查长宽比是否合理
                rect = order_points(quad_temp)
                (tl, tr, br, bl) = rect
                widthA = np.hypot(br[0] - bl[0], br[1] - bl[1])
                widthB = np.hypot(tr[0] - tl[0], tr[1] - tl[1])
                heightA = np.hypot(tr[0] - br[0], tr[1] - br[1])
                heightB = np.hypot(tl[0] - bl[0], tl[1] - bl[1])
                
                avg_width = (widthA + widthB) / 2.0
                avg_height = (heightA + heightB) / 2.0
                aspect = avg_width / (avg_height + 1e-6)
                
                # ========== 关键改进：区分页面边界 vs 表格边框 ==========
                # 检查四个角点是否都非常接近图像边缘
                # 如果检测到的是表格，角点会距离边缘较远
                edge_threshold = min(img_w, img_h) * 0.08  # 8%的边缘容差
                
                min_x = np.min(rect[:, 0])
                max_x = np.max(rect[:, 0])
                min_y = np.min(rect[:, 1])
                max_y = np.max(rect[:, 1])
                
                # 检查是否接近边缘（四条边都要接近）
                near_left = min_x < edge_threshold
                near_right = max_x > (img_w - edge_threshold)
                near_top = min_y < edge_threshold
                near_bottom = max_y > (img_h - edge_threshold)
                
                is_page_boundary = near_left and near_right and near_top and near_bottom
                
                # 只有面积占比≥85%、长宽比合理、且接近边缘，才认为是页面边界
                if area_ratio >= 0.85 and 0.2 <= aspect <= 5.0 and is_page_boundary:
                    quad = quad_temp
                    print(f"[DEBUG] 检测到页面边界（非表格），面积占比: {area_ratio:.2%}, 长宽比: {aspect:.2f}")
                    break
                elif area_ratio >= 0.55 and 0.2 <= aspect <= 5.0:
                    # 面积较大但不是页面边界，可能是表格
                    print(f"[DEBUG] 检测到大型矩形区域（可能是表格），面积占比: {area_ratio:.2%}，跳过裁切以保留全部内容")
                    # 不设置quad，跳过透视变换
        
        # 执行透视变换（仅当确认是页面边界时）
        if quad is not None:
            warped = four_point_transform(img, quad, margin_cm=1.0)
            print(f"[DEBUG] 已执行透视矫正（保留1cm边距）")
        else:
            # 未检测到页面边界，或检测到的是表格
            # 直接使用原图，保留所有内容（包括表格上下的文字）
            warped = img
            print(f"[DEBUG] 跳过透视裁切，保留完整页面内容")
        
        # ========== 步骤2：强化背景去除和对比度增强 ==========
        # 转换为灰度
        gray_warped = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # 使用自适应直方图均衡化增强对比度
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray_warped)
        
        # 背景归一化：使用大高斯核估计背景
        background = cv2.GaussianBlur(enhanced, (0, 0), sigmaX=25, sigmaY=25)
        
        # 归一化：去除背景影响
        normalized = cv2.divide(enhanced, background, scale=255)
        
        # 再次增强对比度
        normalized = cv2.normalize(normalized, None, 0, 255, cv2.NORM_MINMAX)
        
        # ========== 步骤3：自适应二值化 ==========
        # 使用Sauvola自适应阈值，适合处理不均匀光照
        try:
            # window_size必须是奇数
            window_size = 51
            # k值控制阈值的敏感度，0.15-0.25是文档扫描的常用范围
            k = 0.2
            thresh = threshold_sauvola(normalized, window_size=window_size, k=k)
            binary = (normalized > thresh).astype(np.uint8) * 255
            print(f"[DEBUG] Sauvola二值化完成 (window_size={window_size}, k={k})")
        except Exception as e:
            # 如果Sauvola失败，使用Otsu二值化作为后备
            print(f"[DEBUG] Sauvola失败，使用Otsu: {e}")
            _, binary = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # ========== 步骤4：去噪处理 ==========
        # 形态学操作去除小噪点
        kernel_denoise = np.ones((2, 2), np.uint8)
        
        # 开运算：去除小的白色噪点
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_denoise, iterations=1)
        
        # 闭运算：填充文字中的小孔
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_denoise, iterations=1)
        
        # 可选：中值滤波进一步去噪（保持边缘）
        binary = cv2.medianBlur(binary, 3)
        
        # ========== 步骤5：质量检查和后备方案 ==========
        # 检查二值化结果的有效性
        black_ratio = np.sum(binary == 0) / binary.size
        white_ratio = np.sum(binary == 255) / binary.size
        
        print(f"[DEBUG] 二值化结果 - 黑色占比: {black_ratio:.2%}, 白色占比: {white_ratio:.2%}")
        
        # 如果结果过于极端（几乎全黑或全白），使用增强的灰度图
        if black_ratio < 0.01 or white_ratio < 0.01:
            print(f"[DEBUG] 二值化结果异常，使用增强灰度图")
            result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        else:
            # 转换为BGR格式以匹配输入格式
            result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        # ========== 步骤6：边缘锐化（可选，提升清晰度）==========
        # 轻微锐化以提升文字清晰度
        kernel_sharpen = np.array([[-0.5, -0.5, -0.5],
                                   [-0.5,  5.0, -0.5],
                                   [-0.5, -0.5, -0.5]])
        result = cv2.filter2D(result, -1, kernel_sharpen)
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        print(f"[DEBUG] 处理完成，输出尺寸: {result.shape}")
        return result
    
    def _perspective_correction(self, img):
        """保守裁掉黑边，避免过度裁剪内容"""
        h, w = img.shape[:2]
        def strip_black_borders(img_gray, thresh=10, max_ratio=0.95):
            hh, ww = img_gray.shape
            top, bottom, left, right = 0, hh, 0, ww
            # 顶部
            while top < bottom:
                if (img_gray[top, :] < thresh).mean() > max_ratio:
                    top += 1
                else:
                    break
            # 底部
            while bottom - 1 > top:
                if (img_gray[bottom - 1, :] < thresh).mean() > max_ratio:
                    bottom -= 1
                else:
                    break
            # 左侧
            while left < right:
                if (img_gray[:, left] < thresh).mean() > max_ratio:
                    left += 1
                else:
                    break
            # 右侧
            while right - 1 > left:
                if (img_gray[:, right - 1] < thresh).mean() > max_ratio:
                    right -= 1
                else:
                    break
            return img_gray[top:bottom, left:right]
        cropped = strip_black_borders(img)
        # 保底检查：若裁剪后面积过小，则回退为原图
        if cropped.size == 0:
            return img
        area_ratio = (cropped.shape[0] * cropped.shape[1]) / float(h * w)
        if area_ratio < 0.6:  # 保守阈值，避免过度裁剪
            return img
        return cropped
    
    def _convert_images_to_pdf(self, session_id, image_files, output_path):
        """将多个图片转换为PDF，优化文件大小"""
        # A4尺寸 (210mm x 297mm) 在300dpi下的像素尺寸
        a4_width = 2480  # 210mm * 300dpi / 25.4
        a4_height = 3508  # 297mm * 300dpi / 25.4
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        for file_info in image_files:
            image_path = os.path.join(self.upload_folder, session_id, file_info['filename'])
            
            try:
                # 打开图片
                with Image.open(image_path) as img:
                    # 转换为RGB模式
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 计算缩放比例以适应A4页面
                    img_width, img_height = img.size
                    scale_w = a4_width / img_width
                    scale_h = a4_height / img_height
                    scale = min(scale_w, scale_h)
                    
                    # 计算新尺寸
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    # 调整图片大小，使用更高效的重采样方法
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # 计算居中位置
                    x = (A4[0] - new_width * 72 / 300) / 2  # 转换为点单位
                    y = (A4[1] - new_height * 72 / 300) / 2
                    
                    # 将PIL图片转换为ReportLab可用的格式，使用JPEG压缩
                    img_buffer = io.BytesIO()
                    # 使用JPEG格式和85%质量以减少文件大小
                    img_resized.save(img_buffer, format='JPEG', quality=85, optimize=True, dpi=(300, 300))
                    img_buffer.seek(0)
                    
                    # 添加图片到PDF
                    c.drawImage(ImageReader(img_buffer), x, y, 
                              width=new_width * 72 / 300, 
                              height=new_height * 72 / 300)
                    
                    # 添加新页面（除了最后一张图片）
                    if file_info != image_files[-1]:
                        c.showPage()
                        
            except Exception as e:
                print(f"处理图片 {file_info['filename']} 时出错: {e}")
                continue
        
        c.save()
    
    def _create_zip(self, base_dir, filenames, zip_path):
        """创建ZIP文件"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in filenames:
                file_path = os.path.join(base_dir, filename)
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)