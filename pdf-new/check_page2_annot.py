#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深入检查第2页的Annots对象
"""
import fitz
import os
import re

def check_page2_annot(pdf_path, page_num=1):
    """检查指定页面的Annots详细信息"""
    print(f"\n检查文件: {os.path.basename(pdf_path)}")
    print(f"页面: {page_num + 1}")
    print("="*80)
    
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    page_xref = page.xref
    
    # 1. 读取页面对象
    print("\n【页面对象】")
    page_obj = doc.xref_object(page_xref)
    print(f"页面xref: {page_xref}")
    print(f"页面对象（前1000字符）:")
    print(page_obj[:1000])
    
    # 2. 检查Annots键
    print("\n【Annots键】")
    if '/Annots' in page_obj:
        print("找到/Annots键")
        annots_match = re.search(r'/Annots\s*(\[[\s\S]*?\]|null)', page_obj)
        if annots_match:
            annots_value = annots_match.group(1)
            print(f"Annots值: {annots_value}")
            
            # 提取xref引用
            annot_xrefs = re.findall(r'(\d+)\s+0\s+R', annots_value)
            if annot_xrefs:
                print(f"包含 {len(annot_xrefs)} 个注释xref: {annot_xrefs}")
                
                # 详细检查每个注释对象
                for xref_str in annot_xrefs:
                    xref = int(xref_str)
                    print(f"\n【注释对象 xref={xref}】")
                    try:
                        annot_obj = doc.xref_object(xref)
                        print("对象内容:")
                        print(annot_obj)
                        
                        # 检查是否有/AP（外观流）
                        if '/AP' in annot_obj:
                            print("\n*** 包含/AP（外观流） - 这是公章可见的关键！***")
                            
                            # 提取/AP/N引用
                            ap_n_match = re.search(r'/AP\s*<<\s*/N\s+(\d+)\s+0\s+R', annot_obj)
                            if ap_n_match:
                                ap_xref = int(ap_n_match.group(1))
                                print(f"/AP/N指向外观对象 xref={ap_xref}")
                                
                                # 读取外观对象
                                try:
                                    ap_obj = doc.xref_object(ap_xref)
                                    print(f"\n【外观对象 xref={ap_xref}】")
                                    print("对象内容（前500字符）:")
                                    print(ap_obj[:500])
                                    
                                    # 检查外观流是否包含图像引用
                                    if '/XObject' in ap_obj:
                                        print("\n外观对象包含XObject（可能是图像）")
                                        xobj_matches = re.findall(r'/(\w+)\s+(\d+)\s+0\s+R', ap_obj)
                                        for name, xobj_xref in xobj_matches:
                                            print(f"  {name}: xref={xobj_xref}")
                                except Exception as e:
                                    print(f"无法读取外观对象: {e}")
                    except Exception as e:
                        print(f"无法读取注释对象: {e}")
            else:
                print("Annots数组为空")
    else:
        print("未找到/Annots键")
    
    # 3. 使用PyMuPDF API检查注释
    print("\n【使用PyMuPDF API检查注释】")
    annots = list(page.annots())
    print(f"page.annots()返回 {len(annots)} 个注释")
    for i, annot in enumerate(annots):
        print(f"\n注释 {i+1}:")
        print(f"  类型: {annot.type}")
        print(f"  矩形: {annot.rect}")
        print(f"  信息: {annot.info}")
        try:
            # 尝试获取外观
            pix = annot.get_pixmap()
            if pix:
                print(f"  外观尺寸: {pix.width}x{pix.height}")
                print(f"  *** 注释有外观流，WPS可能会渲染它 ***")
                pix = None
        except Exception as e:
            print(f"  无法获取外观: {e}")
    
    doc.close()

if __name__ == "__main__":
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    original_file = os.path.join(folder, "西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf")
    processed_file = os.path.join(folder, "去红头-西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知(2).pdf")
    
    print("\n" + "="*100)
    print("原始文件 - 第2页")
    print("="*100)
    check_page2_annot(original_file, 1)
    
    print("\n\n" + "="*100)
    print("处理后文件 - 第2页")
    print("="*100)
    check_page2_annot(processed_file, 1)
