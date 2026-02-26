import cv2
from pathlib import Path


GENDER_TEMPLATE_DIR = Path(r"C:\WEB\scrape\template\gender")
THRESHOLD = 0.51 

gender_templates = {}

for file in GENDER_TEMPLATE_DIR.glob("*.png"):
    name = file.stem.lower()
    tmpl = cv2.imread(str(file), 0)
    if tmpl is not None:
        gender_templates[name] = tmpl

def detect_gender(image, box, debug=False):

    x, y, w, h = box
    roi = image[y:y+h, x:x+w]

    if roi.size == 0:
        return None

    windows = [
        roi[:, int(w * 0.10):int(w * 0.40)],
        roi[:, int(w * 0.20):int(w * 0.50)],
        roi[:, int(w * 0.30):int(w * 0.60)],
        roi[:, int(w * 0.40):int(w * 0.80)],
    ]

    best_label = None
    best_score = 0

    for window in windows:

        gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)

        for label, tmpl in gender_templates.items():

            if window.shape[0] < tmpl.shape[0] or window.shape[1] < tmpl.shape[1]:
                continue

            result = cv2.matchTemplate(
                gray,
                tmpl,
                cv2.TM_CCOEFF_NORMED
            )

            _, max_val, _, _ = cv2.minMaxLoc(result)

            if max_val > best_score:
                best_score = max_val
                best_label = label

    return best_label if best_score >= THRESHOLD else "third"