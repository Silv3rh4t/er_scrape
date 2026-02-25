import cv2
import numpy as np


def detect_voter_boxes(image_path, debug=False):


    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strong threshold to isolate borders
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Morphological closing to strengthen borders
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        closed,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter by size — tune after inspection
        if 300 < w < 1200 and 200 < h < 800:
            boxes.append((x, y, w, h))

    # Sort top-to-bottom, then left-to-right
    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))


    debug_img = img.copy()
    for (x, y, w, h) in boxes:
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0,255,0), 3)

    cv2.imwrite("C:/WEB/scrape/debug/debug_boxes.png", debug_img)

    return boxes