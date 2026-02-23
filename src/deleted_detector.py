import cv2
import numpy as np


# ===============================
# LOAD + PREPROCESS TEMPLATE ONCE
# ===============================

TEMPLATE_PATH = r"C:\WEB\scrape\template\D.png"

template_gray = cv2.imread(TEMPLATE_PATH, 0)

if template_gray is None:
    raise ValueError("D template not found at path")

# Light blur (must match ROI processing)
template_gray = cv2.GaussianBlur(template_gray, (3, 3), 0)

# Edge extraction
template_edges = cv2.Canny(template_gray, 50, 150)

th, tw = template_edges.shape


# ===============================
# DELETED DETECTOR
# ===============================

def is_deleted_box(image, box):

    x, y, w, h = box
    roi = image[y:y+h, x:x+w]

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(
        gray,
        template_gray,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_val, _, _ = cv2.minMaxLoc(result)

    print("Score:", max_val)

    return max_val >= 0.60