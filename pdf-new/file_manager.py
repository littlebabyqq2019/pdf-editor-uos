import os
import shutil
from PIL import Image
import PyPDF2
import fitz  # PyMuPDF
import base64
import io
import time

class FileManager:
    def __init__(self, upload_folder='uploads', processed_folder='processed'):
        self.upload_folder = upload_folder
        self.processed_folder = processed_folder
        
    def analyze_file(self, file_path, filename):
        """分析文件类型和属性"""
        file_ext = os.path.splitext(filename)[1].lower()
        file_info = {
            'filename': filename,
            'size': os.path.getsize(file_path),
            'type': 'unknown'
        }
        
        if file_ext == '.pdf':
            file_info['type'] = self._analyze_pdf_type(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            file_info['type'] = 'image'
        elif file_ext in ['.doc', '.docx']:
            file_info['type'] = 'word'
        elif file_ext == '.ofd':
            file_info['type'] = 'ofd'

        return file_info
    
    def _analyze_pdf_type(self, file_path):
        """分析PDF类型：文本型或扫描型"""
        try:
            # 使用PyMuPDF分析第一页的文本内容
            doc = fitz.open(file_path)
            if len(doc) == 0:
                return 'unknown'
            
            first_page = doc[0]
            text = first_page.get_text()
            
            # 如果第一页文本内容较多，判断为文本型PDF
            if len(text.strip()) > 100:
                return '文本型PDF'
            else:
                return '扫描型PDF'
                
        except Exception as e:
            print(f"分析PDF类型时出错: {e}")
            return 'unknown'
    
    def get_session_files(self, session_id):
        """获取会话的所有文件"""
        session_dir = os.path.join(self.upload_folder, session_id)
        if not os.path.exists(session_dir):
            return []
        
        files = []
        for filename in os.listdir(session_dir):
            file_path = os.path.join(session_dir, filename)
            if os.path.isfile(file_path):
                file_info = self.analyze_file(file_path, filename)
                files.append(file_info)
        
        return files
    
    def delete_file(self, session_id, filename):
        """删除指定文件"""
        try:
            session_dir = os.path.join(self.upload_folder, session_id)
            file_path = os.path.join(session_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件时出错: {e}")
            return False
    
    def clear_all_files(self, session_id):
        """清空会话的所有文件"""
        try:
            session_dir = os.path.join(self.upload_folder, session_id)
            if os.path.exists(session_dir):
                shutil.rmtree(session_dir)
                os.makedirs(session_dir, exist_ok=True)
            
            # 同时清空处理后的文件
            processed_dir = os.path.join(self.processed_folder, session_id)
            if os.path.exists(processed_dir):
                shutil.rmtree(processed_dir)
                
            return True
        except Exception as e:
            print(f"清空文件时出错: {e}")
            return False
    
    def get_preview(self, session_id, filename):
        """获取文件预览数据"""
        try:
            session_dir = os.path.join(self.upload_folder, session_id)
            file_path = os.path.join(session_dir, filename)
            
            if not os.path.exists(file_path):
                return {'error': '文件不存在'}
            
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                return self._get_pdf_preview(file_path)
            elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                return self._get_image_preview(file_path)
            elif file_ext in ['.doc', '.docx']:
                return {'type': 'word', 'filename': os.path.basename(file_path)}
            elif file_ext == '.ofd':
                return {'type': 'ofd', 'filename': os.path.basename(file_path)}
            else:
                return {'error': '不支持的文件类型'}
                
        except Exception as e:
            return {'error': f'预览失败: {str(e)}'}
    
    def _get_pdf_preview(self, file_path):
        """获取PDF预览"""
        try:
            doc = fitz.open(file_path)
            pages = []
            
            # 最多预览前5页
            max_pages = min(5, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                # 转换为图片
                mat = fitz.Matrix(1.5, 1.5)  # 缩放因子
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # 转换为base64
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                pages.append({
                    'page': page_num + 1,
                    'image': f'data:image/png;base64,{img_base64}'
                })
            
            doc.close()
            return {'type': 'pdf', 'pages': pages}
            
        except Exception as e:
            return {'error': f'PDF预览失败: {str(e)}'}
    
    def _get_image_preview(self, file_path):
        """获取图片预览"""
        try:
            with Image.open(file_path) as img:
                # 调整图片大小用于预览
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                
                # 转换为base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_data = buffer.getvalue()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                return {
                    'type': 'image',
                    'image': f'data:image/png;base64,{img_base64}'
                }
                
        except Exception as e:
            return {'error': f'图片预览失败: {str(e)}'}
    
    def get_file_path(self, session_id, filename):
        """获取文件的完整路径"""
        return os.path.join(self.upload_folder, session_id, filename)
    
    def ensure_processed_dir(self, session_id):
        """确保处理后文件的目录存在"""
        processed_dir = os.path.join(self.processed_folder, session_id)
        os.makedirs(processed_dir, exist_ok=True)
        return processed_dir

    def clear_uploads_only(self, session_id):
        """仅清空会话上传目录（不删除processed），带WinError 32重试"""
        try:
            session_dir = os.path.join(self.upload_folder, session_id)
            if not os.path.exists(session_dir):
                return True

            # 逐个文件安全删除，避免句柄占用
            for name in os.listdir(session_dir):
                path = os.path.join(session_dir, name)
                if os.path.isfile(path):
                    self._safe_remove_file(path)
                elif os.path.isdir(path):
                    self._safe_rmtree(path)

            return True
        except Exception as e:
            print(f"清空上传文件时出错: {e}")
            return False

    def _safe_remove_file(self, path, retries=5, delay=0.2):
        """安全删除单个文件，遇到WinError 32重试"""
        for i in range(retries):
            try:
                if os.path.exists(path):
                    os.remove(path)
                return True
            except PermissionError as e:
                # WinError 32: 文件正在使用，等待后重试
                time.sleep(delay)
            except Exception as e:
                # 其他异常直接抛出结束循环
                raise
        return False

    def _safe_rmtree(self, dir_path, retries=5, delay=0.2):
        """安全删除目录，遇到占用重试"""
        for i in range(retries):
            try:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                return True
            except PermissionError:
                time.sleep(delay)
            except Exception as e:
                raise
        return False