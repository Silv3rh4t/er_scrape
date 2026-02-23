import cv2
import os


TEMPLATE_DIR = r"C:\WEB\scrape\template\sections"

section_templates = {}

for file in os.listdir(TEMPLATE_DIR):
    if file.endswith(".png"):
        section_number = int(os.path.splitext(file)[0])
        path = os.path.join(TEMPLATE_DIR, file)
        tmpl = cv2.imread(path, 0)
        section_templates[section_number] = tmpl


def get_section_number(image, page_index=None):

    h, w, _ = image.shape

    # Crop header region
    header = image[0:int(h * 0.20), :]

    gray = cv2.cvtColor(header, cv2.COLOR_BGR2GRAY)

    best_score = -1
    best_section = None

    for section_number, tmpl in section_templates.items():

        result = cv2.matchTemplate(
            gray,
            tmpl,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_val, _, _ = cv2.minMaxLoc(result)

        if max_val > best_score:
            best_score = max_val
            best_section = section_number

    # Debug (optional)
    if page_index is not None:
        print(f"Page {page_index} | Best Score: {best_score:.3f} | Section: {best_section}")

    # 🔒 Hard threshold
    if best_score >= 0.85:
        return best_section

    return None

