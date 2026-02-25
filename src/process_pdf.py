import cv2
from collections import defaultdict

from box_detector import detect_voter_boxes
from deleted_detector import is_deleted_box
from header_detector import get_section_number
from supplementary_detector import supplement_section  # correct import
from gender_detector import detect_gender


def process_pages(image_paths):

    results = defaultdict(lambda: {
        "total": 0,
        "deleted": 0,
        "added": 0,
        "male": 0,
        "female": 0,
        "third": 0
    })

    total_pages = len(image_paths)

    for idx, path in enumerate(image_paths):

        # Skip first 2 and last page
        if idx < 2 or idx == total_pages - 1:
            continue

        image = cv2.imread(path)

        if image is None:
            print("Failed to load:", path)
            continue

        section_no = get_section_number(image, idx + 1)

        if section_no is None:
            print("Section detection failed on:", path)
            continue

        # ======= SUPPLEMENT PAGE =======
        if section_no == 0:
            print(f"Page {idx+1} -> Supplement List")
                    
            boxes = detect_voter_boxes(path)

            for box in boxes:

                sec_added = supplement_section(image, box)

                if sec_added is None:
                    continue

                if sec_added not in results:
                    results[sec_added] = {
                        "total": 0,
                        "deleted": 0,
                        "added": 0,
                        "male": 0,
                        "female": 0,
                        "third": 0
                    }

                gender = detect_gender(image, box)

                if gender is None:
                    print("Supplement gender detection weak — skipping")
                    continue

                results[sec_added][gender] += 1
                results[sec_added]["added"] += 1

            continue

        # ======= NORMAL MAIN ROLL =======
        print(f"Page {idx+1} -> Section {section_no}")

        boxes = detect_voter_boxes(path)

        for box in boxes:
            results[section_no]["total"] += 1

            if is_deleted_box(image, box):
                results[section_no]["deleted"] += 1
                continue
            
            gender = detect_gender(image, box)

            if gender:
                results[section_no][gender] += 1
                    

    # ======= COMPUTE FINAL RESULTS =======

    final_results = {}

    for sec, data in results.items():
        final_results[sec] = {
            "total": data["total"],
            "deleted": data["deleted"],
            "added": data["added"],
            "male": data["male"],
            "female": data["female"],
            "third": data["third"],
            "net": data["total"] - data["deleted"] + data["added"]
        }

    return final_results