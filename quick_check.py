import sys, traceback
print("[STEP] start", flush=True)
try:
    print("[STEP] python:", sys.version, flush=True)
    import fitz
    print("[STEP] fitz version ok", flush=True)
    import cv2
    print("[STEP] cv2 version:", getattr(cv2, "__version__", "unknown"), flush=True)
    import numpy as np
    print("[STEP] numpy version:", np.__version__, flush=True)
    import PIL
    print("[STEP] PIL version:", getattr(PIL, "__version__", "unknown"), flush=True)
    import skimage
    print("[STEP] skimage version:", getattr(skimage, "__version__", "unknown"), flush=True)
    import reportlab
    print("[STEP] reportlab version:", getattr(reportlab, "__version__", "unknown"), flush=True)
    import fitz
    doc = fitz.open("3.pdf")
    print("[STEP] open pdf ok, pages:", len(doc), flush=True)
    doc.close()
    print("[DONE] quick check OK", flush=True)
except Exception as e:
    print("[ERR] quick check failed:", e, flush=True)
    traceback.print_exc()