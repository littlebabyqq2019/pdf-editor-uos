"""
PDF编辑工具集成应用
整合了PDF处理工具(pdf-new)和PDF编辑器(pdf-editor draw)
版本: 1.1
"""

# 版本信息
VERSION = "1.1"
VERSION_DATE = "2026-01-02"

from flask import Flask, render_template, request, jsonify, send_file, session, send_from_directory
import os
import uuid
from datetime import datetime
import zipfile
import io
import re
import shutil
import base64
from urllib.parse import quote, unquote
import threading
import subprocess
import time

def safe_filename(filename):
    """安全的文件名处理，保留中文字符"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip(' .')
    if not filename:
        filename = 'unnamed_file'
    return filename

# 导入pdf-new的处理器模块
import sys
pdf_new_path = os.path.join(os.path.dirname(__file__), 'pdf-new')
sys.path.insert(0, pdf_new_path)

from pdf_processor import PDFProcessor
from image_processor import ImageProcessor
from file_manager import FileManager

# PyInstaller 下资源路径与可写路径分离
if getattr(sys, "frozen", False):
    TEMPLATE_BASE = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    APP_DIR = os.path.dirname(sys.executable)
else:
    TEMPLATE_BASE = os.path.abspath(os.path.dirname(__file__))
    APP_DIR = TEMPLATE_BASE


def _bootstrap_project_paths():
    """为 PyInstaller 打包后的可执行文件补充模块路径。"""
    candidates = []
    if getattr(sys, "frozen", False):
        base_dir = TEMPLATE_BASE
        candidates.extend([
            os.path.join(base_dir, 'pdf-new'),
            os.path.join(base_dir, 'pdf-editor（draw）'),
            os.path.join(os.path.dirname(sys.executable), 'pdf-new'),
            os.path.join(os.path.dirname(sys.executable), 'pdf-editor（draw）'),
        ])
    else:
        root_dir = os.path.abspath(os.path.dirname(__file__))
        candidates.extend([
            os.path.join(root_dir, 'pdf-new'),
            os.path.join(root_dir, 'pdf-editor（draw）'),
        ])

    for path in candidates:
        if path and os.path.isdir(path) and path not in sys.path:
            sys.path.insert(0, path)


_bootstrap_project_paths()

app = Flask(__name__, 
            template_folder=os.path.join(TEMPLATE_BASE, "templates"),
            static_folder=os.path.join(TEMPLATE_BASE, "static"))
app.secret_key = 'pdf-editor-integrated-2024'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 静态文件缓存1年

# 添加静态文件缓存响应头
@app.after_request
def add_cache_headers(response):
    """为静态资源添加缓存头"""
    if request.path.startswith('/static/') or request.path.startswith('/editor/static/'):
        # 静态文件缓存1年
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    elif request.path in ['/', '/editor']:
        # HTML页面缓存5分钟，但允许使用缓存副本
        response.headers['Cache-Control'] = 'public, max-age=300'
    return response

# 提前定义并创建上传/处理目录
UPLOAD_FOLDER = os.path.join(APP_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(APP_DIR, 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def clean_temp_folders():
    """清空uploads和processed文件夹内容"""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            for item in os.listdir(UPLOAD_FOLDER):
                item_path = os.path.join(UPLOAD_FOLDER, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"[WARNING] 无法删除 {item_path}: {e}")
        
        if os.path.exists(PROCESSED_FOLDER):
            for item in os.listdir(PROCESSED_FOLDER):
                item_path = os.path.join(PROCESSED_FOLDER, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f"[WARNING] 无法删除 {item_path}: {e}")
        
        print("[INFO] 已清空临时文件夹 (uploads & processed)")
    except Exception as e:
        print(f"[WARNING] 清理临时文件夹时出错: {e}")

# 初始化处理器
pdf_processor = PDFProcessor(UPLOAD_FOLDER, PROCESSED_FOLDER)
image_processor = ImageProcessor(UPLOAD_FOLDER, PROCESSED_FOLDER)
file_manager = FileManager(UPLOAD_FOLDER, PROCESSED_FOLDER)

# ========== PDF页面管理工具函数 ==========
def _session_dir():
    sid = session.get('session_id')
    if not sid:
        raise RuntimeError('会话无效')
    updir = os.path.join(UPLOAD_FOLDER, sid)
    procdir = os.path.join(PROCESSED_FOLDER, sid)
    os.makedirs(updir, exist_ok=True)
    os.makedirs(procdir, exist_ok=True)
    return sid, updir, procdir

def _abs_upload_path(filename):
    sid, updir, _ = _session_dir()
    return os.path.join(updir, filename)

def _abs_processed_path(filename):
    sid, _, procdir = _session_dir()
    return os.path.join(procdir, filename)

def _is_pdf(path):
    return path.lower().endswith('.pdf') and os.path.exists(path)

def _thumb_dataurl_for_page(doc, page_index, zoom=0.5):
    import fitz
    page = doc[page_index]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    png_bytes = pix.tobytes("png")
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return f"data:image/png;base64,{b64}"

# ========== 路由：主页 (pdf-new) ==========
@app.route('/')
def index():
    """主页面 - PDF处理工具"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html', version=VERSION, version_date=VERSION_DATE)

# ========== 路由：PDF编辑器 (pdf-editor draw) ==========
@app.route('/editor')
def editor():
    """PDF编辑器页面"""
    return render_template('editor.html', version=VERSION, version_date=VERSION_DATE)

# ========== 静态文件路由 ==========
@app.route('/editor/static/<path:path>')
def send_editor_static(path):
    """提供PDF编辑器的静态文件"""
    editor_static = os.path.join(TEMPLATE_BASE, 'static', 'editor')
    return send_from_directory(editor_static, path)

# ========== pdf-new的所有API路由 ==========
@app.route('/pdf/pages', methods=['POST'])
def list_pdf_pages():
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        if not filename:
            return jsonify({'error':'缺少文件名'}), 400
        src_path = _abs_upload_path(filename)
        if not _is_pdf(src_path):
            return jsonify({'error':'文件不存在或不是PDF'}), 400
        import fitz
        doc = fitz.open(src_path)
        thumbs = []
        for i in range(len(doc)):
            thumbs.append({
                'index': i,
                'thumb': _thumb_dataurl_for_page(doc, i, zoom=0.5)
            })
        meta = {'total': len(doc), 'pages': thumbs}
        doc.close()
        return jsonify({'success': True, 'meta': meta})
    except Exception as e:
        return jsonify({'error': f'读取页面失败: {e}'}), 500

@app.route('/pdf/pages/export', methods=['POST'])
def export_pdf_pages():
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        order = data.get('order', [])
        remove = data.get('remove', [])
        if not filename:
            return jsonify({'error':'缺少文件名'}), 400
        src_path = _abs_upload_path(filename)
        if not _is_pdf(src_path):
            return jsonify({'error':'文件不存在或不是PDF'}), 400

        import fitz
        src = fitz.open(src_path)
        new_doc = fitz.open()
        keep_set = set(range(len(src))) - set(remove or [])
        if order:
            seq = [i for i in order if i in keep_set]
        else:
            seq = [i for i in range(len(src)) if i in keep_set]
        if not seq:
            src.close()
            return jsonify({'error':'没有可保留的页面'}), 400
        for i in seq:
            new_doc.insert_pdf(src, from_page=i, to_page=i)
        out_path = _abs_processed_path(filename)
        new_doc.save(out_path)
        src.close()
        new_doc.close()
        return jsonify({'success': True, 'download': filename})
    except Exception as e:
        return jsonify({'error': f'导出失败: {e}'}), 500

@app.route('/pdf/merge', methods=['POST'])
def merge_pdfs():
    try:
        data = request.get_json() or {}
        order = data.get('files', [])
        if not order or len(order) < 2:
            return jsonify({'error':'请至少选择两个PDF'}), 400
        first = order[0]
        name, ext = os.path.splitext(first)
        merged_name = f"{name}（合并）.pdf"
        import fitz
        out_doc = fitz.open()
        for fname in order:
            src_path = _abs_upload_path(fname)
            if not _is_pdf(src_path):
                return jsonify({'error': f'文件不存在或不是PDF: {fname}'}), 400
            src = fitz.open(src_path)
            out_doc.insert_pdf(src)
            src.close()
        out_path = _abs_processed_path(merged_name)
        out_doc.save(out_path)
        out_doc.close()
        return jsonify({'success': True, 'download': merged_name})
    except Exception as e:
        return jsonify({'error': f'合并失败: {e}'}), 500

@app.route('/pdf/split', methods=['POST'])
def split_pdf():
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        splits = data.get('splits', [])
        if not filename or not splits:
            return jsonify({'error':'缺少参数'}), 400
        src_path = _abs_upload_path(filename)
        if not _is_pdf(src_path):
            return jsonify({'error':'文件不存在或不是PDF'}), 400

        import fitz, zipfile, io
        src = fitz.open(src_path)
        total = len(src)
        base, ext = os.path.splitext(filename)
        mem = io.BytesIO()
        zf = zipfile.ZipFile(mem, 'w', zipfile.ZIP_DEFLATED)

        index = 1
        for part in splits:
            s = int(part.get('start', 1))
            e = int(part.get('end', s))
            s = max(1, min(s, total))
            e = max(1, min(e, total))
            if s > e:
                s, e = e, s
            new_doc = fitz.open()
            new_doc.insert_pdf(src, from_page=s-1, to_page=e-1)
            part_name = f"{base}-{index}.pdf"
            buf = new_doc.tobytes()
            new_doc.close()
            zf.writestr(part_name, buf)
            index += 1

        zf.close()
        src.close()

        zip_name = f"{base}.zip"
        out_path = _abs_processed_path(zip_name)
        with open(out_path, 'wb') as f:
            f.write(mem.getvalue())

        return jsonify({'success': True, 'download': zip_name})
    except Exception as e:
        return jsonify({'error': f'拆分失败: {e}'}), 500

def clear_startup_folders():
    """程序启动时仅清空 uploads 文件夹"""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
        print("启动时已清空uploads文件夹（保留processed）")
    except Exception as e:
        print(f"清空启动文件夹时出错: {e}")

clear_startup_folders()

@app.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file:
            filename = safe_filename(file.filename)
            session_id = session.get('session_id')
            
            session_dir = os.path.join(UPLOAD_FOLDER, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            file_path = os.path.join(session_dir, filename)
            file.save(file_path)
            
            file_info = file_manager.analyze_file(file_path, filename)
            
            return jsonify({
                'success': True,
                'file_info': file_info
            })
    
    except Exception as e:
        return jsonify({'error': f'上传失败: {str(e)}'}), 500

@app.route('/get_files')
def get_files():
    """获取当前会话的文件列表"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'files': []})
        
        files = file_manager.get_session_files(session_id)
        return jsonify({'files': files})
    
    except Exception as e:
        return jsonify({'error': f'获取文件列表失败: {str(e)}'}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    """删除文件"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        session_id = session.get('session_id')
        
        if file_manager.delete_file(session_id, filename):
            return jsonify({'success': True})
        else:
            return jsonify({'error': '删除失败'}), 400
    
    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500

@app.route('/clear_all_files', methods=['POST'])
def clear_all_files():
    """清空所有文件"""
    try:
        session_id = session.get('session_id')
        
        if file_manager.clear_all_files(session_id):
            return jsonify({'success': True})
        else:
            return jsonify({'error': '清空失败'}), 400
    
    except Exception as e:
        return jsonify({'error': f'清空失败: {str(e)}'}), 500

@app.route('/preview/<filename>')
def preview_file(filename):
    """文件预览"""
    try:
        session_id = session.get('session_id')
        preview_data = file_manager.get_preview(session_id, filename)
        return jsonify(preview_data)
    
    except Exception as e:
        return jsonify({'error': f'预览失败: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_files():
    """处理文件的通用接口"""
    try:
        data = request.get_json()
        action = data.get('action')
        file_order = data.get('file_order', [])
        session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({'error': '会话无效'}), 400
        
        files = file_manager.get_session_files(session_id)
        if not files:
            return jsonify({'error': '没有文件需要处理'}), 400
        
        if file_order:
            file_dict = {f['filename']: f for f in files}
            ordered_files = []
            for filename in file_order:
                if filename in file_dict:
                    ordered_files.append(file_dict[filename])
            for file_info in files:
                if file_info['filename'] not in file_order:
                    ordered_files.append(file_info)
            files = ordered_files
        
        if action == 'remove_header_seal':
            result = pdf_processor.remove_header_and_seal(session_id, files)
        elif action == 'remove_seal':
            result = pdf_processor.remove_seal_only(session_id, files)
        elif action == 'convert_then_remove':
            result = pdf_processor.convert_then_remove_header_seal(session_id, files)
        elif action == 'remove_background':
            result = image_processor.remove_background(session_id, files)
        elif action == 'convert_to_word':
            result = pdf_processor.convert_to_word(session_id, files)
        elif action == 'images_to_pdf':
            result = image_processor.images_to_pdf(session_id, files)
        else:
            return jsonify({'error': '未知的操作类型'}), 400
        
        try:
            if isinstance(result, dict) and result.get('success'):
                file_manager.clear_uploads_only(session_id)
        except Exception as _e:
            pass
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

# ========== 异步处理 ==========
JOBS = {}
JOBS_LOCK = threading.Lock()

def _run_process_job(job_id, session_id, action, file_order):
    try:
        with JOBS_LOCK:
            JOBS[job_id]['status'] = 'running'
        files = file_manager.get_session_files(session_id)
        if not files:
            raise RuntimeError('没有文件需要处理')
        if file_order:
            file_dict = {f['filename']: f for f in files}
            ordered_files = [file_dict[name] for name in file_order if name in file_dict]
            for fi in files:
                if fi['filename'] not in file_order:
                    ordered_files.append(fi)
            files = ordered_files

        if action == 'remove_header_seal':
            result = pdf_processor.remove_header_and_seal(session_id, files)
        elif action == 'remove_seal':
            result = pdf_processor.remove_seal_only(session_id, files)
        elif action == 'convert_then_remove':
            result = pdf_processor.convert_then_remove_header_seal(session_id, files)
        elif action == 'remove_background':
            result = image_processor.remove_background(session_id, files)
        elif action == 'convert_to_word':
            result = pdf_processor.convert_to_word(session_id, files)
        elif action == 'images_to_pdf':
            result = image_processor.images_to_pdf(session_id, files)
        else:
            raise RuntimeError('未知的操作类型')

        try:
            if isinstance(result, dict) and result.get('success'):
                file_manager.clear_uploads_only(session_id)
        except Exception:
            pass

        with JOBS_LOCK:
            JOBS[job_id]['status'] = 'success' if result.get('success') else 'error'
            JOBS[job_id]['result'] = {
                'download_file': result.get('download_file')
            }
            if not result.get('success'):
                JOBS[job_id]['error'] = result.get('error') or '处理失败'
    except Exception as e:
        with JOBS_LOCK:
            JOBS[job_id]['status'] = 'error'
            JOBS[job_id]['error'] = str(e)

@app.route('/process_async', methods=['POST'])
def process_async():
    """提交异步任务"""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        file_order = data.get('file_order', [])
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': '会话无效'}), 400
        job_id = str(uuid.uuid4())
        with JOBS_LOCK:
            JOBS[job_id] = {
                'status': 'queued',
                'created_at': datetime.utcnow().isoformat()
            }
        t = threading.Thread(target=_run_process_job, args=(job_id, session_id, action, file_order), daemon=True)
        t.start()
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        return jsonify({'error': f'提交失败: {e}'}), 500

@app.route('/job_status')
def job_status():
    """查询任务状态"""
    try:
        job_id = request.args.get('job_id')
        if not job_id:
            return jsonify({'error': '缺少 job_id'}), 400
        with JOBS_LOCK:
            job = JOBS.get(job_id)
        if not job:
            return jsonify({'error': '任务不存在'}), 404
        resp = {'status': job.get('status')}
        if job.get('status') == 'success':
            resp['result'] = job.get('result', {})
        if job.get('status') == 'error':
            resp['error'] = job.get('error', '未知错误')
        return jsonify(resp)
    except Exception as e:
        return jsonify({'error': f'查询失败: {e}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """文件下载"""
    try:
        session_id = session.get('session_id')
        processed_dir = os.path.join(PROCESSED_FOLDER, session_id)
        file_path = os.path.join(processed_dir, filename)
        
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '文件不存在'}), 404
    
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

def _restart_app():
    try:
        if getattr(sys, 'frozen', False):
            exe = sys.executable
            subprocess.Popen([exe], cwd=APP_DIR)
        else:
            py = sys.executable
            script = os.path.abspath(os.path.join(TEMPLATE_BASE, 'app.py'))
            subprocess.Popen([py, script], cwd=TEMPLATE_BASE)
    except Exception:
        pass
    finally:
        os._exit(0)

@app.route('/kill_and_restart', methods=['POST'])
def kill_and_restart():
    """终止当前进程并重启程序"""
    try:
        def delayed_restart():
            time.sleep(1.0)
            _restart_app()
        threading.Thread(target=delayed_restart, daemon=True).start()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'{e}'}), 500

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--port', type=int, default=int(os.environ.get('PDF_EDITOR_PORT', '5000')))
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--debug', action='store_true')
    args, _ = parser.parse_known_args()

    try:
        print("=" * 60)
        print("PDF编辑工具集成版 v2.0 已启动")
        print("=" * 60)
        
        clean_temp_folders()
        
        # 获取本机IP地址
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"📍 本机访问: http://localhost:{args.port}")
        print(f"🌐 局域网访问: http://{local_ip}:{args.port}")
        print(f"📄 PDF处理工具: http://{local_ip}:{args.port}")
        print(f"✏️  PDF编辑器: http://{local_ip}:{args.port}/editor")
        print(f"按 Ctrl+C 可停止服务")
        print("=" * 60)
        
        app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False, threaded=True)
    except Exception as e:
        try:
            with open(os.path.join(APP_DIR, "startup.log"), "a", encoding="utf-8") as f:
                f.write(f"[startup-error] {e}\n")
        except:
            pass
        raise
