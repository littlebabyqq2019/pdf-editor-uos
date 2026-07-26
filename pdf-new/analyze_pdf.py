#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析PDF文件结构，找出公章数据
"""
import fitz  # PyMuPDF
import sys
import os

def analyze_pdf(pdf_path):
    """深度分析PDF文件结构"""
    print(f"\n{'='*80}")
    print(f"分析文件: {os.path.basename(pdf_path)}")
    print(f"{'='*80}\n")
    
    try:
        doc = fitz.open(pdf_path)
        print(f"文档信息:")
        print(f"  页数: {len(doc)}")
        print(f"  是否加密: {doc.is_encrypted}")
        print(f"  是否有表单: {doc.is_form_pdf}")
        
        # 分析每一页
        for page_num in range(len(doc)):
            page = doc[page_num]
            print(f"\n{'='*80}")
            print(f"第 {page_num + 1} 页分析:")
            print(f"{'='*80}")
            print(f"页面尺寸: {page.rect}")
            
            # 1. 检查注释 (Annotations)
            print(f"\n【注释 (Annotations)】")
            annots = list(page.annots())
            print(f"  注释数量: {len(annots)}")
            if annots:
                for i, annot in enumerate(annots):
                    print(f"  注释 {i+1}:")
                    print(f"    类型: {annot.type}")
                    print(f"    矩形: {annot.rect}")
                    print(f"    信息: {annot.info}")
                    try:
                        # 尝试获取注释内容
                        print(f"    内容: {annot.get_text()}")
                    except:
                        pass
            
            # 2. 检查图像
            print(f"\n【图像 (Images)】")
            images = page.get_images(full=True)
            print(f"  图像数量: {len(images)}")
            if images:
                for i, img in enumerate(images):
                    xref = img[0]
                    name = img[7] if len(img) > 7 else "未命名"
                    print(f"  图像 {i+1}:")
                    print(f"    xref: {xref}")
                    print(f"    名称: {name}")
                    
                    # 获取图像位置
                    try:
                        img_rects = page.get_image_rects(xref)
                        if img_rects:
                            for rect in img_rects:
                                print(f"    位置: {rect}")
                                page_height = page.rect.height
                                y_center = (rect.y0 + rect.y1) / 2
                                from_bottom = page_height - rect.y1
                                print(f"    y中心: {y_center:.1f}, 距底部: {from_bottom:.1f}")
                    except Exception as e:
                        print(f"    无法获取位置: {e}")
                    
                    # 检查图像数据
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        print(f"    尺寸: {pix.width}x{pix.height}")
                        print(f"    色彩空间: {pix.colorspace}")
                        print(f"    是否有Alpha通道: {pix.alpha}")
                        pix = None
                    except Exception as e:
                        print(f"    无法读取图像数据: {e}")
            
            # 3. 检查矢量图形
            print(f"\n【矢量图形 (Drawings)】")
            drawings = page.get_drawings()
            print(f"  矢量图形数量: {len(drawings)}")
            if drawings:
                red_drawings = []
                for i, drawing in enumerate(drawings):
                    # 检查是否包含红色
                    fill_color = drawing.get('fill')
                    stroke_color = drawing.get('color')
                    rect = drawing.get('rect')
                    
                    is_red = False
                    if fill_color and len(fill_color) >= 3:
                        r, g, b = fill_color[:3]
                        if r > 0.7 and g < 0.3 and b < 0.3:
                            is_red = True
                    if stroke_color and len(stroke_color) >= 3:
                        r, g, b = stroke_color[:3]
                        if r > 0.7 and g < 0.3 and b < 0.3:
                            is_red = True
                    
                    if is_red and rect:
                        red_drawings.append((i, drawing))
                        print(f"  矢量图形 {i+1} (红色):")
                        print(f"    矩形: {rect}")
                        page_height = page.rect.height
                        if isinstance(rect, (list, tuple)) and len(rect) >= 4:
                            y_center = (rect[1] + rect[3]) / 2
                        else:
                            y_center = (rect.y0 + rect.y1) / 2
                        from_bottom = page_height - y_center
                        print(f"    y中心: {y_center:.1f}, 距底部: {from_bottom:.1f}")
                        print(f"    填充色: {fill_color}")
                        print(f"    描边色: {stroke_color}")
                
                if red_drawings:
                    print(f"  共发现 {len(red_drawings)} 个红色矢量图形")
            
            # 4. 检查表单字段
            print(f"\n【表单字段 (Form Fields)】")
            try:
                widgets = list(page.widgets())
                print(f"  表单字段数量: {len(widgets)}")
                if widgets:
                    for i, widget in enumerate(widgets):
                        print(f"  字段 {i+1}:")
                        print(f"    类型: {widget.field_type}")
                        print(f"    名称: {widget.field_name}")
                        print(f"    矩形: {widget.rect}")
            except Exception as e:
                print(f"  检查表单字段失败: {e}")
            
            # 5. 检查页面对象中的Annots
            print(f"\n【页面对象中的Annots】")
            try:
                page_xref = page.xref
                page_obj = doc.xref_object(page_xref)
                
                if '/Annots' in page_obj:
                    print("  页面对象包含/Annots键")
                    import re
                    annots_match = re.search(r'/Annots\s*\[\s*([^\]]+)\]', page_obj)
                    if annots_match:
                        annots_content = annots_match.group(1)
                        annot_xrefs = re.findall(r'(\d+)\s+0\s+R', annots_content)
                        print(f"  Annots数组包含 {len(annot_xrefs)} 个xref引用: {annot_xrefs}")
                        
                        # 详细检查每个注释对象
                        for xref_str in annot_xrefs:
                            xref = int(xref_str)
                            print(f"\n  检查注释对象 xref={xref}:")
                            try:
                                annot_obj = doc.xref_object(xref)
                                print(f"    对象内容片段:")
                                lines = annot_obj.split('\n')[:10]  # 只显示前10行
                                for line in lines:
                                    print(f"      {line}")
                                
                                # 检查是否包含签名字段
                                if '/FT /Sig' in annot_obj:
                                    print(f"    *** 这是一个签名字段 ***")
                                if '/Subtype /Widget' in annot_obj:
                                    print(f"    *** 这是一个Widget（表单字段）***")
                                
                                # 检查位置
                                rect_match = re.search(r'/Rect\s*\[\s*([\d\.\s]+)\]', annot_obj)
                                if rect_match:
                                    coords = rect_match.group(1).split()
                                    if len(coords) >= 4:
                                        x0, y0, x1, y1 = [float(c) for c in coords[:4]]
                                        print(f"    位置: [{x0}, {y0}, {x1}, {y1}]")
                            except Exception as e:
                                print(f"    无法读取注释对象: {e}")
                    else:
                        print("  无法解析/Annots数组")
                else:
                    print("  页面对象不包含/Annots键")
            except Exception as e:
                print(f"  检查页面对象失败: {e}")
            
            # 6. 分析内容流
            print(f"\n【内容流分析】")
            try:
                content = page.read_contents()
                content_str = content.decode('latin-1', errors='ignore')
                print(f"  内容流大小: {len(content_str)} 字节")
                
                # 查找红色指令
                import re
                red_pattern = r'(1(?:\.0+)?\s+0(?:\.0+)?\s+0(?:\.0+)?\s+(?:rg|RG))'
                red_matches = list(re.finditer(red_pattern, content_str))
                print(f"  红色指令数量: {len(red_matches)}")
                
                # 查找图像引用
                img_pattern = r'/Im\d+\s+Do'
                img_refs = re.findall(img_pattern, content_str)
                print(f"  图像引用数量: {len(img_refs)}")
                if img_refs:
                    print(f"  图像引用: {img_refs}")
                
            except Exception as e:
                print(f"  分析内容流失败: {e}")
        
        doc.close()
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 分析处理前后的PDF文件
    folder = r"e:\dev\pdf-new0.2\pdf-new1.3\pdf-new\1"
    
    # 原始文件
    original_file = os.path.join(folder, "西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知.pdf")
    
    # 处理后的文件
    processed_file = os.path.join(folder, "去红头-西安市卫生健康委员会关于召开西安市新生儿疾病医疗质量控制培训会暨质控中心第一次工作会议的通知(2).pdf")
    
    print("\n" + "="*100)
    print("PDF文件结构分析")
    print("="*100)
    
    if os.path.exists(original_file):
        analyze_pdf(original_file)
    else:
        print(f"原始文件不存在: {original_file}")
    
    if os.path.exists(processed_file):
        analyze_pdf(processed_file)
    else:
        print(f"处理后文件不存在: {processed_file}")
