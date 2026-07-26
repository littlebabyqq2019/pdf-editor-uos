#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的公章删除功能
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from pdf_processor import PDFProcessor

def test_fix():
    """测试修复"""
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    original_file = os.path.join(folder, "西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf")
    output_file = os.path.join(folder, "测试修复-西安市卫生健康委员会.pdf")
    
    print("="*80)
    print("测试修复后的公章删除功能")
    print("="*80)
    print(f"\n输入文件: {os.path.basename(original_file)}")
    print(f"输出文件: {os.path.basename(output_file)}")
    
    # 创建处理器
    processor = PDFProcessor()
    
    # 直接调用处理方法
    print("\n开始处理...")
    try:
        processor._remove_header_seal_text_pdf(original_file, output_file)
        print(f"\n处理完成！输出文件: {output_file}")
    except Exception as e:
        print(f"\n处理失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 验证结果
    print("\n" + "="*80)
    print("验证处理结果")
    print("="*80)
    
    import fitz
    import re
    
    doc = fitz.open(output_file)
    
    # 检查第2页
    page = doc[1]
    page_xref = page.xref
    page_obj = doc.xref_object(page_xref)
    
    print(f"\n第2页分析:")
    print(f"  页面xref: {page_xref}")
    
    if '/Annots' in page_obj:
        print("  *** 警告：/Annots键仍然存在 ***")
        annots_match = re.search(r'/Annots\s*(\[[\s\S]*?\]|null)', page_obj)
        if annots_match:
            print(f"  Annots值: {annots_match.group(1)}")
    else:
        print("  ✓ /Annots键已被删除")
    
    # 扫描所有xref对象，查找签名字段
    print("\n扫描所有xref对象...")
    xref_count = doc.xref_length()
    signature_found = False
    
    for xref in range(1, xref_count):
        try:
            obj = doc.xref_object(xref)
            if not obj or obj.strip() == "":
                continue
            
            if '/FT /Sig' in obj and '/Subtype /Widget' in obj:
                print(f"\n*** 发现签名字段对象 xref={xref} ***")
                signature_found = True
                
                # 检查是否还有/AP键
                if '/AP' in obj:
                    print(f"  ✗ 警告：/AP键仍然存在！WPS可能仍会显示公章")
                    ap_match = re.search(r'/AP\s*<<([^>]*)>>', obj)
                    if ap_match:
                        print(f"  /AP内容: {ap_match.group(0)[:100]}")
                else:
                    print(f"  ✓ /AP键已被清除")
                
                # 检查/V键
                if '/V' in obj and '/V null' not in obj:
                    print(f"  ✗ 警告：/V键仍然存在")
                else:
                    print(f"  ✓ /V键已被清除")
                
                # 检查/DR键
                if '/DR' in obj and '/DR null' not in obj:
                    print(f"  ✗ 警告：/DR键仍然存在")
                else:
                    print(f"  ✓ /DR键已被清除")
        except:
            continue
    
    if not signature_found:
        print("\n✓ 未发现任何签名字段对象")
    
    doc.close()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print("""
下一步：
1. 使用WPS手机版或WPS电脑版打开处理后的文件
2. 检查第2页的公章是否仍然可见
3. 如果公章已不可见，说明修复成功！
""")

if __name__ == "__main__":
    test_fix()
