#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查新生成的测试文件
"""
import fitz
import os
import re

def check_file(pdf_path):
    """检查PDF中所有的签名字段和外观流对象"""
    print(f"\n检查文件: {os.path.basename(pdf_path)}")
    print("="*80)
    
    if not os.path.exists(pdf_path):
        print(f"文件不存在: {pdf_path}")
        return
    
    doc = fitz.open(pdf_path)
    
    print(f"\n【扫描所有xref对象】")
    
    # 获取PDF中的所有xref数量
    xref_count = doc.xref_length()
    print(f"PDF中共有 {xref_count} 个xref对象")
    
    signature_objects = []
    appearance_objects = []
    
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
                print(f"对象内容:")
                print(obj)
                
                # 检查是否有/AP键
                if '/AP' in obj:
                    print(f"  ✗ 警告：/AP键仍然存在！")
                else:
                    print(f"  ✓ /AP键已被清除")
            
            # 检查是否是外观流对象（Form XObject）
            elif '/Type /XObject' in obj and '/Subtype /Form' in obj:
                appearance_objects.append(xref)
        
        except Exception as e:
            continue
    
    print(f"\n【统计结果】")
    print(f"签名字段对象: {len(signature_objects)}")
    print(f"外观流对象: {len(appearance_objects)}")
    
    if signature_objects:
        print(f"\n*** 警告：发现 {len(signature_objects)} 个签名字段对象！***")
        print(f"xref列表: {signature_objects}")
    else:
        print(f"\n✓ 未发现任何签名字段对象")
    
    doc.close()

if __name__ == "__main__":
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    test_file = os.path.join(folder, "测试修复-西安市卫生健康委员会.pdf")
    
    check_file(test_file)
