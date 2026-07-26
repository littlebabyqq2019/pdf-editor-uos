#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查处理后PDF中是否还有孤立的签名注释对象
"""
import fitz
import os
import re

def check_orphan_objects(pdf_path):
    """检查PDF中所有的签名字段和外观流对象"""
    print(f"\n检查文件: {os.path.basename(pdf_path)}")
    print("="*80)
    
    doc = fitz.open(pdf_path)
    
    print("\n【扫描所有xref对象】")
    
    # 获取PDF中的所有xref数量
    xref_count = doc.xref_length()
    print(f"PDF中共有 {xref_count} 个xref对象")
    
    signature_objects = []
    appearance_objects = []
    xobject_images = []
    
    # 遍历所有xref
    for xref in range(1, xref_count):
        try:
            obj = doc.xref_object(xref)
            if not obj or obj.strip() == "":
                continue
            
            # 检查是否是签名字段
            if '/FT /Sig' in obj and '/Subtype /Widget' in obj:
                signature_objects.append(xref)
                print(f"\n*** 发现签名字段对象 xref={xref} ***")
                print(f"对象内容（前300字符）:")
                print(obj[:300])
                
                # 提取/AP/N引用
                ap_n_match = re.search(r'/AP\s*<<\s*/N\s+(\d+)\s+0\s+R', obj)
                if ap_n_match:
                    ap_xref = int(ap_n_match.group(1))
                    print(f"  引用外观流 xref={ap_xref}")
            
            # 检查是否是外观流对象（Form XObject）
            elif '/Type /XObject' in obj and '/Subtype /Form' in obj:
                appearance_objects.append(xref)
                # 只打印引用了其他XObject的外观流
                if '/XObject' in obj:
                    print(f"\n发现外观流对象 xref={xref}")
                    print(f"对象内容（前200字符）:")
                    print(obj[:200])
                    
                    # 提取XObject引用
                    xobj_matches = re.findall(r'/(\w+)\s+(\d+)\s+0\s+R', obj)
                    for name, xobj_xref in xobj_matches:
                        if 'XObject' not in name:  # 排除/XObject本身
                            print(f"  引用XObject {name}: xref={xobj_xref}")
            
            # 检查是否是图像XObject
            elif '/Type /XObject' in obj and ('/Subtype /Image' in obj or '/Width' in obj):
                # 只记录，不打印所有图像
                xobject_images.append(xref)
        
        except Exception as e:
            continue
    
    print(f"\n【统计结果】")
    print(f"签名字段对象: {len(signature_objects)}")
    print(f"外观流对象: {len(appearance_objects)}")
    print(f"图像XObject: {len(xobject_images)}")
    
    if signature_objects:
        print(f"\n*** 警告：发现 {len(signature_objects)} 个孤立的签名字段对象！***")
        print(f"xref列表: {signature_objects}")
        print("这些对象虽然没有被页面的/Annots引用，但WPS可能仍然会渲染它们！")
    
    doc.close()

if __name__ == "__main__":
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    original_file = os.path.join(folder, "西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf")
    processed_file = os.path.join(folder, "去红头-西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知(2).pdf")
    
    print("\n" + "="*100)
    print("原始文件")
    print("="*100)
    check_orphan_objects(original_file)
    
    print("\n\n" + "="*100)
    print("处理后文件")
    print("="*100)
    check_orphan_objects(processed_file)
