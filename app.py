"""
PDF编辑工具集成应用
整合了PDF处理工具(pdf-new)和PDF编辑器(pdf-editor draw)
版本: 1.1
"""

# 版本信息
VERSION = "1.2.3"
VERSION_DATE = "2026-08-02"

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
from watermark_processor import WatermarkProcessor

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
watermark_processor = WatermarkProcessor()

# 水印预设与配置持久化存储
WATERMARK_PRESETS_FILE = os.path.join(APP_DIR, 'watermark_presets.json')
WATERMARK_CONFIG_FILE = os.path.join(APP_DIR, 'watermark_config.json')

def _load_watermark_config():
    """加载全局水印配置"""
    if os.path.exists(WATERMARK_CONFIG_FILE):
        try:
            import json
            with open(WATERMARK_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 加载水印配置失败: {e}")
    # 默认配置
    return {
        'font_size': 40,
        'color': '#CCCCCC',
        'opacity': 0.3,
        'rotation': 45,
        'density': 3
    }

def _save_watermark_config(config):
    """保存全局水印配置"""
    try:
        import json
        with open(WATERMARK_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] 保存水印配置失败: {e}")
        return False

def _load_watermark_presets():
    """加载水印预设列表（只包含name和text）"""
    if os.path.exists(WATERMARK_PRESETS_FILE):
        try:
            import json
            with open(WATERMARK_PRESETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 加载水印预设失败: {e}")
    return []

def _save_watermark_presets(presets):
    """保存水印预设列表"""
    try:
        import json
        with open(WATERMARK_PRESETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[ERROR] 保存水印预设失败: {e}")
        return False

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

@app.route('/watermark/config', methods=['GET'])
def get_watermark_config():
    """获取全局水印配置"""
    try:
        config = _load_watermark_config()
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        return jsonify({'error': f'获取配置失败: {e}'}), 500

@app.route('/watermark/config', methods=['POST'])
def save_watermark_config():
    """保存全局水印配置"""
    try:
        data = request.get_json() or {}
        config = {
            'font_size': int(data.get('font_size', 40)),
            'color': data.get('color', '#CCCCCC'),
            'opacity': float(data.get('opacity', 0.3)),
            'rotation': int(data.get('rotation', 45)),
            'density': int(data.get('density', 3))
        }

        if _save_watermark_config(config):
            return jsonify({'success': True, 'config': config})
        else:
            return jsonify({'error': '保存失败'}), 500
    except Exception as e:
        return jsonify({'error': f'保存失败: {e}'}), 500

@app.route('/watermark/presets', methods=['GET'])
def get_watermark_presets():
    """获取所有水印预设"""
    try:
        presets = _load_watermark_presets()
        return jsonify({'success': True, 'presets': presets})
    except Exception as e:
        return jsonify({'error': f'获取失败: {e}'}), 500

@app.route('/watermark/presets', methods=['POST'])
def add_watermark_preset():
    """添加水印预设（仅保存name和text）"""
    try:
        data = request.get_json() or {}
        preset = {
            'id': str(uuid.uuid4()),
            'name': data.get('name', '未命名水印'),
            'text': data.get('text', '水印'),
            'created_at': datetime.now().isoformat()
        }

        presets = _load_watermark_presets()
        presets.append(preset)

        if _save_watermark_presets(presets):
            return jsonify({'success': True, 'preset': preset})
        else:
            return jsonify({'error': '保存失败'}), 500
    except Exception as e:
        return jsonify({'error': f'添加失败: {e}'}), 500

@app.route('/watermark/presets/<preset_id>', methods=['PUT'])
def update_watermark_preset(preset_id):
    """更新水印预设（仅更新name和text）"""
    try:
        data = request.get_json() or {}
        presets = _load_watermark_presets()

        found = False
        for i, preset in enumerate(presets):
            if preset.get('id') == preset_id:
                presets[i].update({
                    'name': data.get('name', preset['name']),
                    'text': data.get('text', preset['text']),
                })
                found = True
                break

        if not found:
            return jsonify({'error': '预设不存在'}), 404

        if _save_watermark_presets(presets):
            return jsonify({'success': True})
        else:
            return jsonify({'error': '保存失败'}), 500
    except Exception as e:
        return jsonify({'error': f'更新失败: {e}'}), 500

@app.route('/watermark/presets/<preset_id>', methods=['DELETE'])
def delete_watermark_preset(preset_id):
    """删除水印预设"""
    try:
        presets = _load_watermark_presets()
        presets = [p for p in presets if p.get('id') != preset_id]

        if _save_watermark_presets(presets):
            return jsonify({'success': True})
        else:
            return jsonify({'error': '删除失败'}), 500
    except Exception as e:
        return jsonify({'error': f'删除失败: {e}'}), 500

@app.route('/watermark/apply', methods=['POST'])
def apply_watermarks():
    """批量应用水印到PDF或图片文件（支持多文件）"""
    try:
        data = request.get_json() or {}
        filenames = data.get('filenames', [])  # 改为接收文件名列表
        preset_ids = data.get('preset_ids', [])
        session_id = session.get('session_id')

        if not session_id:
            return jsonify({'error': '会话无效'}), 400

        if not filenames:
            return jsonify({'error': '缺少文件名'}), 400

        if not preset_ids:
            return jsonify({'error': '请至少选择一个水印预设'}), 400

        session_upload = os.path.join(UPLOAD_FOLDER, session_id)
        session_processed = os.path.join(PROCESSED_FOLDER, session_id)
        os.makedirs(session_processed, exist_ok=True)

        # 加载全局配置
        global_config = _load_watermark_config()

        # 获取所选预设
        all_presets = _load_watermark_presets()
        selected_presets = [p for p in all_presets if p.get('id') in preset_ids]

        if not selected_presets:
            return jsonify({'error': '未找到所选预设'}), 404

        # 合并全局配置和预设，创建完整的水印配置
        full_presets = []
        for preset in selected_presets:
            full_preset = {
                'id': preset['id'],
                'name': preset['name'],
                'text': preset['text'],
                'font_size': global_config['font_size'],
                'color': global_config['color'],
                'opacity': global_config['opacity'],
                'rotation': global_config['rotation'],
                'density': global_config['density']
            }
            full_presets.append(full_preset)

        # 存储所有生成的文件夹路径（用于打包）
        all_output_folders = []

        # 定义图片扩展名
        image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif')

        # 循环处理每个文件
        for filename in filenames:
            input_path = os.path.join(session_upload, filename)
            if not os.path.exists(input_path):
                print(f"[WARNING] 文件不存在，跳过: {filename}")
                continue

            # 判断文件类型
            file_ext = os.path.splitext(filename)[1].lower()
            is_image = file_ext in image_extensions
            is_pdf = file_ext == '.pdf'

            print(f"[INFO] 处理文件: {filename}, 类型: {'图片' if is_image else 'PDF' if is_pdf else '未知'}")

            if not is_image and not is_pdf:
                print(f"[WARNING] 不支持的文件类型，跳过: {filename}")
                continue

            # 为当前文件创建独立文件夹: 加水印-原文件名
            base_name = os.path.splitext(filename)[0]
            file_output_folder = os.path.join(session_processed, f'加水印-{base_name}')
            os.makedirs(file_output_folder, exist_ok=True)
            print(f"[INFO] 创建输出文件夹: {file_output_folder}")

            # 循环添加每个水印预设
            file_watermarked_count = 0
            for preset in full_presets:
                if is_pdf:
                    # PDF：输出为PDF格式
                    output_filename = f"{preset['name']}-{base_name}.pdf"
                    output_path = os.path.join(file_output_folder, output_filename)
                    print(f"[INFO] 添加PDF水印: {output_filename}")
                    success = watermark_processor.add_single_watermark(
                        input_path,
                        output_path,
                        preset
                    )
                else:  # is_image
                    # 图片：保持原格式输出
                    output_filename = f"{preset['name']}-{base_name}{file_ext}"
                    output_path = os.path.join(file_output_folder, output_filename)
                    print(f"[INFO] 添加图片水印: {output_filename}, 输出路径: {output_path}")
                    success = watermark_processor.add_watermark_to_image(
                        input_path,
                        output_path,
                        preset
                    )

                if success:
                    file_watermarked_count += 1
                    print(f"[INFO] 水印添加成功，文件已生成: {output_path}")
                else:
                    print(f"[ERROR] 水印添加失败: {output_filename}")

            if file_watermarked_count > 0:
                all_output_folders.append(file_output_folder)
                print(f"[INFO] 文件处理完成，成功添加 {file_watermarked_count} 个水印")

        if not all_output_folders:
            print(f"[ERROR] 所有文件处理失败，没有生成任何输出")
            return jsonify({'error': '所有文件处理失败'}), 500

        # 统计总共生成的文件数量
        total_files = 0
        all_generated_files = []  # 存储所有生成的文件路径
        for folder_path in all_output_folders:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_generated_files.append((file_path, file))  # (完整路径, 文件名)
                    total_files += 1

        # 判断是否需要打包：只有1个文件时直接返回，多个文件时打包
        if total_files == 1:
            # 单个文件，移到processed根目录并直接返回
            src_file_path, original_filename = all_generated_files[0]
            dest_file_path = os.path.join(session_processed, original_filename)

            # 如果目标文件已存在，先删除
            if os.path.exists(dest_file_path):
                os.remove(dest_file_path)

            # 移动文件到根目录
            shutil.move(src_file_path, dest_file_path)
            print(f"[INFO] 仅1个文件，移动到根目录: {original_filename}")

            # 删除空文件夹
            for folder_path in all_output_folders:
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)

            return jsonify({
                'success': True,
                'download_file': original_filename,
                'files_count': 1,
                'direct_file': True  # 标记为直接文件
            })
        else:
            # 多个文件，打包成ZIP
            print(f"[INFO] 共{total_files}个文件，开始打包为ZIP")
            zip_filename = '已处理.zip'
            zip_path = os.path.join(session_processed, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for folder_path in all_output_folders:
                    folder_name = os.path.basename(folder_path)
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 在 ZIP 中保留文件夹结构: 加水印-xxx/水印名-xxx.pdf
                            arcname = os.path.join(folder_name, file)
                            zipf.write(file_path, arcname)
                            print(f"[INFO] 添加到ZIP: {arcname}")

            print(f"[INFO] ZIP文件创建成功: {zip_path}, 大小: {os.path.getsize(zip_path)} bytes")

            return jsonify({
                'success': True,
                'download_file': zip_filename,
                'files_count': len(all_output_folders)
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理失败: {e}'}), 500


@app.route('/ofd_to_pdf', methods=['POST'])
def ofd_to_pdf():
    """OFD转PDF（支持多文件）"""
    try:
        from ofd2img import OFD
        
        data = request.get_json() or {}
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'error': '未提供文件'}), 400
        
        session_id = session.get('session_id')
        session_upload = os.path.join(UPLOAD_FOLDER, session_id)
        session_processed = os.path.join(PROCESSED_FOLDER, session_id)
        os.makedirs(session_processed, exist_ok=True)
        
        print(f"[INFO] 开始转换 {len(filenames)} 个OFD文件为PDF")
        
        # 存储所有转换成功的PDF文件
        converted_files = []
        
        for filename in filenames:
            input_path = os.path.join(session_upload, filename)
            if not os.path.exists(input_path):
                print(f"[WARNING] 文件不存在，跳过: {filename}")
                continue
            
            # 检查文件扩展名
            if not filename.lower().endswith('.ofd'):
                print(f"[WARNING] 不是OFD文件，跳过: {filename}")
                continue
            
            base_name = os.path.splitext(filename)[0]
            output_filename = f"{base_name}.pdf"
            output_path = os.path.join(session_processed, output_filename)
            
            print(f"[INFO] 转换OFD文件: {filename}")
            
            try:
                # 使用ofd2img转换
                ofd = OFD()
                ofd.read(input_path, fmt="path")
                pdf_bytes = ofd.to_pdf()
                
                # 保存转换后的PDF
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"[INFO] 转换成功: {output_filename}, 大小: {len(pdf_bytes)} bytes")
                converted_files.append(output_filename)
                
            except Exception as e:
                print(f"[ERROR] 转换OFD失败 {filename}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not converted_files:
            print(f"[ERROR] 所有文件转换失败")
            return jsonify({'error': '所有文件转换失败'}), 500
        
        # 判断是否需要打包
        if len(converted_files) == 1:
            # 单个文件，直接返回
            print(f"[INFO] 单个文件，直接返回: {converted_files[0]}")
            return jsonify({
                'success': True,
                'download_file': converted_files[0]
            })
        else:
            # 多个文件，打包成ZIP
            print(f"[INFO] 多个文件，打包为ZIP")
            zip_filename = 'OFD转PDF.zip'
            zip_path = os.path.join(session_processed, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf_filename in converted_files:
                    pdf_path = os.path.join(session_processed, pdf_filename)
                    zipf.write(pdf_path, pdf_filename)
                    print(f"[INFO] 添加到ZIP: {pdf_filename}")
            
            print(f"[INFO] ZIP文件创建成功: {zip_path}")
            
            return jsonify({
                'success': True,
                'download_file': zip_filename
            })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'转换失败: {e}'}), 500


@app.route('/pdf_to_images', methods=['POST'])
def pdf_to_images():
    """PDF转图片（支持多文件）"""
    try:
        import fitz  # PyMuPDF

        data = request.get_json() or {}
        filenames = data.get('filenames', [])

        if not filenames:
            return jsonify({'error': '未提供文件'}), 400

        session_id = session.get('session_id')
        session_upload = os.path.join(UPLOAD_FOLDER, session_id)
        session_processed = os.path.join(PROCESSED_FOLDER, session_id)
        os.makedirs(session_processed, exist_ok=True)

        print(f"[INFO] 开始转换 {len(filenames)} 个PDF文件为图片")

        # 存储所有生成的文件/文件夹
        all_outputs = []  # 元素格式: (type, path, name) - type: 'file' 或 'folder'

        for filename in filenames:
            input_path = os.path.join(session_upload, filename)
            if not os.path.exists(input_path):
                print(f"[WARNING] 文件不存在，跳过: {filename}")
                continue

            base_name = os.path.splitext(filename)[0]
            print(f"[INFO] 处理PDF: {filename}")

            try:
                # 打开PDF
                pdf_doc = fitz.open(input_path)
                page_count = len(pdf_doc)
                print(f"[INFO] PDF共有 {page_count} 页")

                # 如果只有1页，直接保存到根目录
                if page_count == 1:
                    page = pdf_doc[0]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍分辨率
                    output_filename = f"{base_name}.jpg"
                    output_path = os.path.join(session_processed, output_filename)
                    pix.save(output_path)
                    print(f"[INFO] 单页PDF转换完成: {output_filename}")
                    all_outputs.append(('file', output_path, output_filename))
                else:
                    # 多页，创建文件夹
                    folder_name = base_name
                    folder_path = os.path.join(session_processed, folder_name)
                    os.makedirs(folder_path, exist_ok=True)

                    for page_num in range(page_count):
                        page = pdf_doc[page_num]
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍分辨率
                        output_filename = f"{base_name}-页面{page_num + 1}.jpg"
                        output_path = os.path.join(folder_path, output_filename)
                        pix.save(output_path)
                        print(f"[INFO] 转换完成: {output_filename}")

                    all_outputs.append(('folder', folder_path, folder_name))

                pdf_doc.close()

            except Exception as e:
                print(f"[ERROR] 转换PDF失败 {filename}: {e}")
                continue

        if not all_outputs:
            print(f"[ERROR] 所有文件转换失败")
            return jsonify({'error': '所有文件转换失败'}), 500

        # 判断是否需要打包
        if len(all_outputs) == 1 and all_outputs[0][0] == 'file':
            # 单个文件，直接返回
            _, file_path, filename = all_outputs[0]
            print(f"[INFO] 单个文件，直接返回: {filename}")
            return jsonify({
                'success': True,
                'download_file': filename
            })
        else:
            # 多个文件或有文件夹，打包成ZIP
            print(f"[INFO] 多个输出，打包为ZIP")
            zip_filename = 'PDF转图片.zip'
            zip_path = os.path.join(session_processed, zip_filename)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for output_type, output_path, output_name in all_outputs:
                    if output_type == 'file':
                        # 单个文件直接添加到ZIP根目录
                        zipf.write(output_path, output_name)
                        print(f"[INFO] 添加到ZIP: {output_name}")
                    else:
                        # 文件夹，遍历添加
                        for root, dirs, files in os.walk(output_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.join(output_name, file)
                                zipf.write(file_path, arcname)
                                print(f"[INFO] 添加到ZIP: {arcname}")

            print(f"[INFO] ZIP文件创建成功: {zip_path}, 大小: {os.path.getsize(zip_path)} bytes")

            return jsonify({
                'success': True,
                'download_file': zip_filename
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'转换失败: {e}'}), 500


@app.route('/watermark/apply_with_action', methods=['POST'])
def apply_watermarks_with_action():
    """先执行PDF处理操作，然后批量添加水印（支持多文件）"""
    try:
        data = request.get_json() or {}
        filenames = data.get('filenames', [])  # 改为接收文件名列表
        preset_ids = data.get('preset_ids', [])
        action_type = data.get('action_type')  # remove_header_seal, remove_seal, convert_then_remove
        session_id = session.get('session_id')

        if not session_id:
            return jsonify({'error': '会话无效'}), 400

        if not filenames or not preset_ids or not action_type:
            return jsonify({'error': '缺少必要参数'}), 400

        session_upload = os.path.join(UPLOAD_FOLDER, session_id)
        session_processed = os.path.join(PROCESSED_FOLDER, session_id)
        os.makedirs(session_processed, exist_ok=True)

        # 步骤1: 加载水印配置
        global_config = _load_watermark_config()
        all_presets = _load_watermark_presets()
        selected_presets = [p for p in all_presets if p.get('id') in preset_ids]

        if not selected_presets:
            return jsonify({'error': '未找到所选预设'}), 404

        full_presets = []
        for preset in selected_presets:
            full_preset = {
                'id': preset['id'],
                'name': preset['name'],
                'text': preset['text'],
                'font_size': global_config['font_size'],
                'color': global_config['color'],
                'opacity': global_config['opacity'],
                'rotation': global_config['rotation'],
                'density': global_config['density']
            }
            full_presets.append(full_preset)

        # 动作名称映射
        action_prefix_map = {
            'remove_header_seal': '去红头',
            'remove_seal': '去公章',
            'convert_then_remove': '去红头'
        }
        action_prefix = action_prefix_map.get(action_type, '处理')

        # 存储所有生成的文件夹路径（用于打包）
        all_output_folders = []

        # 步骤2: 循环处理每个文件
        for filename in filenames:
            input_path = os.path.join(session_upload, filename)
            if not os.path.exists(input_path):
                print(f"[WARNING] 文件不存在，跳过: {filename}")
                continue

            # 2.1 执行前置操作（去红头/去公章等）
            file_info = file_manager.analyze_file(input_path, filename)
            files = [file_info]

            if action_type == 'remove_header_seal':
                result = pdf_processor.remove_header_and_seal(session_id, files)
            elif action_type == 'remove_seal':
                result = pdf_processor.remove_seal_only(session_id, files)
            elif action_type == 'convert_then_remove':
                result = pdf_processor.convert_then_remove_header_seal(session_id, files)
            else:
                continue

            if not result.get('success'):
                print(f"[WARNING] 前置操作失败，跳过: {filename}")
                continue

            # 获取处理后的文件
            processed_filename = result.get('download_file')
            if not processed_filename:
                print(f"[WARNING] 前置操作未返回文件，跳过: {filename}")
                continue

            processed_path = os.path.join(session_processed, processed_filename)
            if not os.path.exists(processed_path):
                print(f"[WARNING] 处理后的文件不存在，跳过: {filename}")
                continue

            # 2.2 为当前文件创建独立文件夹: 加水印-原文件名
            base_name = os.path.splitext(filename)[0]
            file_output_folder = os.path.join(session_processed, f'加水印-{base_name}')
            os.makedirs(file_output_folder, exist_ok=True)

            # 2.3 循环添加每个水印预设
            file_watermarked_count = 0
            for preset in full_presets:
                # 生成文件名: 水印名-去红头-原文件名.pdf
                output_filename = f"{preset['name']}-{action_prefix}-{base_name}.pdf"
                output_path = os.path.join(file_output_folder, output_filename)

                # 添加单个水印
                success = watermark_processor.add_single_watermark(
                    processed_path,
                    output_path,
                    preset
                )

                if success:
                    file_watermarked_count += 1

            if file_watermarked_count > 0:
                all_output_folders.append(file_output_folder)

        if not all_output_folders:
            return jsonify({'error': '所有文件处理失败'}), 500

        # 步骤3: 统计生成的文件数量，单个文件直接返回，多个文件打包为ZIP
        total_files = 0
        all_generated_files = []  # (完整路径, 文件名)
        for folder_path in all_output_folders:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_generated_files.append((file_path, file))
                    total_files += 1

        if total_files == 1:
            # 单个文件，移到processed根目录并直接返回
            src_file_path, original_filename = all_generated_files[0]
            dest_file_path = os.path.join(session_processed, original_filename)

            if os.path.exists(dest_file_path):
                os.remove(dest_file_path)

            shutil.move(src_file_path, dest_file_path)

            # 删除空文件夹
            for folder_path in all_output_folders:
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)

            return jsonify({
                'success': True,
                'download_file': original_filename,
                'files_count': 1,
                'direct_file': True
            })

        # 多个文件，打包所有文件夹为 "已处理.zip"
        zip_filename = '已处理.zip'
        zip_path = os.path.join(session_processed, zip_filename)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_path in all_output_folders:
                folder_name = os.path.basename(folder_path)
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 在 ZIP 中保留文件夹结构: 加水印-xxx/水印名-去红头-xxx.pdf
                        arcname = os.path.join(folder_name, file)
                        zipf.write(file_path, arcname)

        return jsonify({
            'success': True,
            'download_file': zip_filename,
            'files_count': len(all_output_folders)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理失败: {e}'}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """文件下载"""
    try:
        session_id = session.get('session_id')
        processed_dir = os.path.join(PROCESSED_FOLDER, session_id)
        file_path = os.path.join(processed_dir, filename)

        print(f"[INFO] 下载请求 - 文件名: {filename}")
        print(f"[INFO] Session ID: {session_id}")
        print(f"[INFO] 文件路径: {file_path}")
        print(f"[INFO] 文件是否存在: {os.path.exists(file_path)}")

        if os.path.exists(file_path):
            print(f"[INFO] 开始发送文件: {filename}")
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            print(f"[ERROR] 文件不存在: {file_path}")
            # 列出目录中的所有文件
            if os.path.exists(processed_dir):
                files_in_dir = os.listdir(processed_dir)
                print(f"[INFO] 目录中的文件: {files_in_dir}")
            return jsonify({'error': '文件不存在'}), 404

    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        import traceback
        traceback.print_exc()
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

        print(f"本机访问: http://localhost:{args.port}")
        print(f"局域网访问: http://{local_ip}:{args.port}")
        print(f"PDF处理工具: http://{local_ip}:{args.port}")
        print(f"PDF编辑器: http://{local_ip}:{args.port}/editor")
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
