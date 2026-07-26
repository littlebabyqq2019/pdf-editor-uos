#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本信息是否正确传递到模板
"""
from app import app, VERSION, VERSION_DATE

with app.test_client() as client:
    response = client.get('/')
    html = response.data.decode('utf-8')
    
    print("="*60)
    print("版本信息测试")
    print("="*60)
    print(f"\nVERSION常量: {VERSION}")
    print(f"VERSION_DATE常量: {VERSION_DATE}")
    print(f"\nHTTP状态码: {response.status_code}")
    
    # 检查版本号是否在HTML中
    if VERSION in html:
        print(f"✓ 版本号 '{VERSION}' 已正确传递到模板")
    else:
        print(f"✗ 版本号 '{VERSION}' 未找到")
        print(f"  检查是否有 '{{ version }}' 未被渲染")
        if '{{ version }}' in html:
            print(f"  ✗ 发现未渲染的Jinja2变量")
    
    # 检查日期是否在HTML中
    if VERSION_DATE in html:
        print(f"✓ 日期 '{VERSION_DATE}' 已正确传递到模板")
    else:
        print(f"✗ 日期 '{VERSION_DATE}' 未找到")
        if '{{ version_date }}' in html:
            print(f"  ✗ 发现未渲染的Jinja2变量")
    
    # 检查WPS标识
    if 'WPS公章修复版' in html:
        print(f"✓ 'WPS公章修复版' 标识已找到")
    else:
        print(f"✗ 'WPS公章修复版' 标识未找到")
    
    # 查找版本信息区域
    if '<!-- 版本信息 -->' in html:
        print(f"\n✓ 版本信息注释已找到")
        # 提取版本信息区域
        start_idx = html.find('<!-- 版本信息 -->')
        end_idx = html.find('<!-- 预览模态框 -->', start_idx)
        if end_idx > start_idx:
            version_section = html[start_idx:end_idx]
            print(f"\n版本信息区域内容:")
            print("-" * 60)
            print(version_section[:500])  # 显示前500个字符
            print("-" * 60)
    else:
        print(f"\n✗ 版本信息注释未找到")
    
    print("\n" + "="*60)
