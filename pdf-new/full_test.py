#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试：模拟Web界面的处理流程
"""
import sys
import os
import shutil
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor
from file_manager import FileManager

def full_test():
    """完整的处理流程测试"""
    
    print("="*80)
    print("完整处理流程测试")
    print("="*80)
    
    # 准备测试环境
    session_id = str(uuid.uuid4())
    upload_folder = "uploads"
    processed_folder = "processed"
    
    # 创建处理器
    processor = PDFProcessor(upload_folder, processed_folder)
    file_manager = FileManager(upload_folder, processed_folder)
    
    # 源文件
    source_file = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1\西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf"
    
    # 复制到uploads目录
    upload_dir = os.path.join(upload_folder, session_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = os.path.basename(source_file)
    upload_path = os.path.join(upload_dir, filename)
    shutil.copy2(source_file, upload_path)
    
    print(f"\n已上传文件: {filename}")
    print(f"Session ID: {session_id}")
    
    # 检测PDF类型
    print("\n检测PDF类型...")
    files = [{
        'filename': filename,
        'type': '文本型PDF',  # 已知是文本型
        'pages': 4
    }]
    
    print(f"文件类型: {files[0]['type']}")
    
    # 执行去红头及公章操作
    print("\n执行去红头及公章操作...")
    result = processor.remove_header_and_seal(session_id, files)
    
    if 'error' in result:
        print(f"❌ 处理失败: {result['error']}")
        return
    
    print(f"✅ 处理成功！")
    print(f"输出文件: {result.get('download_file')}")
    
    # 验证结果
    output_file = os.path.join(processed_folder, session_id, result.get('download_file'))
    
    if not os.path.exists(output_file):
        print(f"❌ 输出文件不存在: {output_file}")
        return
    
    print(f"\n验证处理结果...")
    
    import fitz
    import re
    
    doc = fitz.open(output_file)
    
    print(f"\n文档信息:")
    print(f"  页数: {len(doc)}")
    
    # 检查第2页
    page = doc[1]
    print(f"\n第2页分析:")
    
    # 检查Annots
    page_xref = page.xref
    page_obj = doc.xref_object(page_xref)
    
    if '/Annots' in page_obj:
        annots_match = re.search(r'/Annots\s*(\[[\s\S]*?\]|null)', page_obj)
        if annots_match:
            annots_value = annots_match.group(1)
            if 'null' in annots_value:
                print(f"  ✓ /Annots已设置为null")
            else:
                print(f"  ✗ /Annots仍包含引用: {annots_value}")
    else:
        print(f"  ✓ /Annots键已删除")
    
    # 扫描签名字段对象
    xref_count = doc.xref_length()
    signature_found = False
    
    for xref in range(1, xref_count):
        try:
            obj = doc.xref_object(xref)
            if not obj:
                continue
            
            if '/FT /Sig' in obj and '/Subtype /Widget' in obj:
                signature_found = True
                print(f"\n  ✗ 发现签名字段对象 xref={xref}")
                
                if '/AP' in obj:
                    print(f"    ✗ /AP键仍然存在")
                else:
                    print(f"    ✓ /AP键已清除")
                break
        except:
            continue
    
    if not signature_found:
        print(f"  ✓ 未发现任何签名字段对象")
    
    doc.close()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print(f"""
结果文件位置: {output_file}

下一步：
1. 用WPS手机版或WPS电脑版打开: {output_file}
2. 检查第2页的公章是否完全不可见
3. 如果公章不可见，说明修复成功！

也可以用其他PDF阅读器验证：
- Adobe Acrobat Reader
- Foxit Reader  
- Chrome浏览器
""")

if __name__ == "__main__":
    full_test()
