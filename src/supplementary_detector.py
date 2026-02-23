import cv2
import os
from pathlib import Path


SUPPLEMENT_TEMPLATE_DIR = Path(r"C:\WEB\scrape\template\supplement")

THRESHOLD = 0.85


# ============================
# Load Supplement Templates
# ============================

supplement_templates = {}

for file in SUPPLEMENT_TEMPLATE_DIR.glob("*.png"):
    name = file.stem

    if name.isdigit():
        section_number = int(name)
        tmpl = cv2.imread(str(file), 0)

        if tmpl is not None:
            supplement_templates[section_number] = tmpl


# ============================
# Supplement Section Extractor
# ============================

def supplement_section(image, box, debug=False):

    x, y, w, h = box
    roi = image[y:y+h, x:x+w]

    # Crop top 25% of voter box
    top_region = roi[0:int(h * 0.25), :]

    # Focus on area of second small box
    candidate = top_region[:, int(w * 0.35):int(w * 0.75)]

    if candidate.size == 0:
        return None

    gray = cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)

    best_section = None
    best_score = 0

    for sec_num, tmpl in supplement_templates.items():

        result = cv2.matchTemplate(
            gray,
            tmpl,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_section = sec_num

    if debug:
        print(f"Best Score: {best_score} | Section: {best_section}")

    if best_score >= THRESHOLD:
        return best_section

    return None