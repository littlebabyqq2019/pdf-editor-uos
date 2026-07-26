# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('pdf-new', 'pdf-new'),
        ('pdf-editor（draw）', 'pdf-editor（draw）'),
    ],
    hiddenimports=[
        'flask',
        'PIL',
        'cv2',
        'numpy',
        'PyPDF2',
        'reportlab',
        'docx',
        'fitz',
        'skimage',
        'skimage.measure',
        'skimage.morphology',
        'skimage.filters',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PDF编辑工具集成版',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
