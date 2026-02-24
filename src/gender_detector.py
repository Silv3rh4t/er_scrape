import cv2
from pathlib import Path

GENDER_TEMPLATE_DIR = Path(r"C:\WEB\scrape\template\gender")
THRESHOLD = 0.80

gender_templates = {}

# Load templates
for file in GENDER_TEMPLATE_DIR.glob("*.png"):
    name = file.stem.lower()
    tmpl = cv2.imread(str(file), 0)
    if tmpl is not None:
        gender_templates[name] = tmpl


def detect_gender(image, box, debug=False):

    x, y, w, h = box
    roi = image[y:y+h, x:x+w]

    # Bottom 30% of voter box
    bottom_region = roi[int(h * 0.65):h, :]

    # Right half (where gender text usually is)
    candidate = bottom_region[:, int(w * 0.4):]

    if candidate.size == 0:
        return None

    gray = cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)

    best_label = None
    best_score = 0

    for label, tmpl in gender_templates.items():

        result = cv2.matchTemplate(
            gray,
            tmpl,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_label = label

    if debug:
        print("Gender score:", best_score, best_label)

    if best_score >= THRESHOLD:
        return best_label

    return None