import csv
import re
from pathlib import Path
from multiprocessing import Pool, cpu_count
from datetime import datetime

from pdf_image import pdf_to_images
from process_pdf import process_pages


# ================= CONFIG =================

BASE_PDF_FOLDER = Path(r".\pdf")
BASE_OUTPUT_FOLDER = Path(r".\outputs")
BASE_OUTPUT_FOLDER.mkdir(exist_ok=True)


# ================= UTIL =================

def extract_ps_number(filename):
    match = re.search(r"HIN-(\d+)-WI", filename)
    if match:
        return int(match.group(1))
    return None


# ================= SINGLE ER =================

def process_single_er(pdf_path, debug_folder, force_reconvert=False):

    pdf_path = Path(pdf_path)
    debug_folder = Path(debug_folder)

    image_folder = debug_folder / pdf_path.stem
    image_folder.mkdir(parents=True, exist_ok=True)

    existing_images = sorted(image_folder.glob("page_*.png"))

    if existing_images and not force_reconvert:
        images = [str(p) for p in existing_images]
    else:
        images = pdf_to_images(pdf_path, image_folder, dpi=400)

    return process_pages(images)


# ================= WRAPPER =================

def process_wrapper(args):

    pdf_path, debug_folder = args

    ps_number = extract_ps_number(pdf_path.name)
    print(f"Processing {pdf_path.parent.name} | PS {ps_number}")

    results = process_single_er(pdf_path, debug_folder)

    rows = []

    for section in sorted(results.keys()):
        data = results[section]

        rows.append([
            ps_number,
            section,
            data["total"],
            data["deleted"],
            data["added"],
            data["male"],
            data["female"],
            data["third"],
            data["net"]
        ])

    return rows


# ================= AC PROCESSOR =================

def process_ac(ac_folder):

    ac_name = ac_folder.name
    print(f"\n========== Processing AC: {ac_name} ==========\n")

    pdf_files = sorted(
        ac_folder.glob("*.pdf"),
        key=lambda x: extract_ps_number(x.name)
    )

    if not pdf_files:
        print("No PDFs found in", ac_name)
        return

    workers = min(len(pdf_files), max(2, cpu_count() // 2))
    print(f"Using {workers} CPU cores for {ac_name}")

    debug_folder = Path(r"C:\WEB\scrape\debug\images") / ac_name
    debug_folder.mkdir(parents=True, exist_ok=True)

    args = [(pdf, debug_folder) for pdf in pdf_files]

    with Pool(processes=workers) as pool:
        results = pool.map(process_wrapper, args, chunksize=1)

    all_rows = []
    for ps_rows in results:
        all_rows.extend(ps_rows)

    all_rows.sort(key=lambda x: (x[0], x[1]))

    output_csv = BASE_OUTPUT_FOLDER / f"{ac_name}_summary.csv"

    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "PS",
            "Section",
            "Count",
            "Delete",
            "Add",
            "Male",
            "Female",
            "Third",
            "Net"
        ])

        writer.writerows(all_rows)

    print(f"\nAC CSV exported → {output_csv}")


# ================= MAIN =================

if __name__ == "__main__":

    ac_folders = [f for f in BASE_PDF_FOLDER.iterdir() if f.is_dir()]

    if not ac_folders:
        print("No AC folders found.")
        exit()

    for ac_folder in ac_folders:
        process_ac(ac_folder)

    print("\nAll ACs processed successfully.")