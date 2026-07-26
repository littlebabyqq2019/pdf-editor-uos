#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重点分析公章删除问题
"""
import fitz  # PyMuPDF
import os
import re

def analyze_seal_issue(original_path, processed_path):
    """对比分析处理前后的公章情况"""
    
    print("\n" + "="*80)
    print("公章删除问题分析")
    print("="*80 + "\n")
    
    # 分析原始文件
    print("【原始文件分析】")
    doc1 = fitz.open(original_path)
    
    for page_num in range(len(doc1)):
        page = doc1[page_num]
        print(f"\n第 {page_num + 1} 页:")
        
        # 检查图像
        images = page.get_images(full=True)
        print(f"  图像数量: {len(images)}")
        for i, img in enumerate(images):
            xref = img[0]
            name = img[7] if len(img) > 7 else "未命名"
            try:
                img_rects = page.get_image_rects(xref)
                if img_rects:
                    rect = img_rects[0]
                    page_height = page.rect.height
                    from_bottom = page_height - rect.y1
                    print(f"    图像{i+1}: {name}, xref={xref}, 距底部={from_bottom:.1f}")
            except:
                pass
        
        # 检查页面对象中的Annots
        page_xref = page.xref
        page_obj = doc1.xref_object(page_xref)
        
        if '/Annots' in page_obj:
            annots_match = re.search(r'/Annots\s*\[\s*([^\]]+)\]', page_obj)
            if annots_match:
                annots_content = annots_match.group(1)
                annot_xrefs = re.findall(r'(\d+)\s+0\s+R', annots_content)
                print(f"  Annots数组: {len(annot_xrefs)} 个xref: {annot_xrefs}")
                
                # 检查每个注释对象
                for xref_str in annot_xrefs:
                    xref = int(xref_str)
                    try:
                        annot_obj = doc1.xref_object(xref)
                        
                        # 检查位置
                        rect_match = re.search(r'/Rect\s*\[\s*([\d\.\s]+)\]', annot_obj)
                        if rect_match:
                            coords = rect_match.group(1).split()
                            if len(coords) >= 4:
                                x0, y0, x1, y1 = [float(c) for c in coords[:4]]
                                from_bottom = page.rect.height - y1
                                
                                # 检查是否是签名字段
                                is_sig = '/FT /Sig' in annot_obj
                                is_widget = '/Subtype /Widget' in annot_obj
                                
                                if from_bottom < 500:  # 距底部较近（中下部）
                                    print(f"    注释 xref={xref}: 距底部={from_bottom:.1f}, 签名={is_sig}, Widget={is_widget}")
                                    if is_sig or is_widget:
                                        print(f"      *** 可能是公章 ***")
                                        # 打印部分对象内容
                                        lines = annot_obj.split('\n')[:5]
                                        for line in lines:
                                            print(f"        {line}")
                    except Exception as e:
                        pass
    
    doc1.close()
    
    # 分析处理后的文件
    print("\n" + "="*80)
    print("【处理后文件分析】")
    doc2 = fitz.open(processed_path)
    
    for page_num in range(len(doc2)):
        page = doc2[page_num]
        print(f"\n第 {page_num + 1} 页:")
        
        # 检查图像
        images = page.get_images(full=True)
        print(f"  图像数量: {len(images)}")
        for i, img in enumerate(images):
            xref = img[0]
            name = img[7] if len(img) > 7 else "未命名"
            try:
                img_rects = page.get_image_rects(xref)
                if img_rects:
                    rect = img_rects[0]
                    page_height = page.rect.height
                    from_bottom = page_height - rect.y1
                    print(f"    图像{i+1}: {name}, xref={xref}, 距底部={from_bottom:.1f}")
            except:
                pass
        
        # 检查页面对象中的Annots
        page_xref = page.xref
        page_obj = doc2.xref_object(page_xref)
        
        if '/Annots' in page_obj:
            annots_match = re.search(r'/Annots\s*\[\s*([^\]]+)\]', page_obj)
            if annots_match:
                annots_content = annots_match.group(1)
                annot_xrefs = re.findall(r'(\d+)\s+0\s+R', annots_content)
                print(f"  *** Annots数组仍然存在: {len(annot_xrefs)} 个xref: {annot_xrefs} ***")
                print(f"  *** 这可能是问题所在：Annots没有被清除 ***")
                
                # 检查每个注释对象
                for xref_str in annot_xrefs:
                    xref = int(xref_str)
                    try:
                        annot_obj = doc2.xref_object(xref)
                        
                        # 检查位置
                        rect_match = re.search(r'/Rect\s*\[\s*([\d\.\s]+)\]', annot_obj)
                        if rect_match:
                            coords = rect_match.group(1).split()
                            if len(coords) >= 4:
                                x0, y0, x1, y1 = [float(c) for c in coords[:4]]
                                from_bottom = page.rect.height - y1
                                
                                # 检查是否是签名字段
                                is_sig = '/FT /Sig' in annot_obj
                                is_widget = '/Subtype /Widget' in annot_obj
                                has_ap = '/AP' in annot_obj  # 外观流
                                
                                if from_bottom < 500:  # 距底部较近（中下部）
                                    print(f"    注释 xref={xref}: 距底部={from_bottom:.1f}, 签名={is_sig}, Widget={is_widget}, 有外观流={has_ap}")
                                    if is_sig or is_widget:
                                        print(f"      *** 这个公章注释没有被删除！***")
                                        
                                        # 打印关键信息
                                        print(f"      对象摘要:")
                                        if has_ap:
                                            print(f"        - 包含/AP（外观流），这可能是WPS显示公章的原因")
                                        
                                        # 查找/N（正常外观）
                                        ap_n_match = re.search(r'/AP\s*<<\s*/N\s+(\d+)\s+0\s+R', annot_obj)
                                        if ap_n_match:
                                            ap_xref = int(ap_n_match.group(1))
                                            print(f"        - /AP/N指向xref={ap_xref}")
                                            try:
                                                ap_obj = doc2.xref_object(ap_xref)
                                                print(f"        - 外观流对象前50字符: {ap_obj[:50]}")
                                            except:
                                                pass
                    except Exception as e:
                        pass
        else:
            print(f"  Annots已被清除")
    
    doc2.close()
    
    print("\n" + "="*80)
    print("【分析结论】")
    print("="*80)
    print("""
如果处理后的文件仍然包含Annots数组，说明：
1. 代码中的 doc.xref_set_key(page_xref, "Annots", "null") 没有生效
2. 或者PDF保存时没有应用垃圾回收清理这些对象
3. 或者需要同时清除Annots引用的AP（外观流）对象

WPS可能会渲染Annots中的/AP外观流，即使其他PDF阅读器不显示。
建议的解决方案：
1. 确保彻底删除Annots键，使用更激进的方法
2. 删除Annots引用的所有外观流对象（/AP）
3. 使用garbage=4和clean=True保存以清理未引用的对象
""")

if __name__ == "__main__":
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    original_file = os.path.join(folder, "西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf")
    processed_file = os.path.join(folder, "去红头-西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知(2).pdf")
    
    analyze_seal_issue(original_file, processed_file)
