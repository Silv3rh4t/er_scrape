import csv
import re
from pathlib import Path
from multiprocessing import Pool, cpu_count
from datetime import datetime

from pdf_image import pdf_to_images
from process_pdf import process_pages


# ============================
# CONFIG
# ============================

PDF_FOLDER = Path(r"C:\WEB\scrape\pdf")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_CSV = Path(
    fr"C:\WEB\scrape\outputs\PS_summary_{timestamp}.csv"
)
OUTPUT_CSV.parent.mkdir(exist_ok=True)


# ============================
# UTILITIES
# ============================

def extract_ps_number(filename):
    match = re.search(r"HIN-(\d+)-WI", filename)
    if match:
        return int(match.group(1))
    return None


# ============================
# SINGLE ER PROCESSOR
# ============================

def process_single_er(pdf_path, output_folder, force_reconvert=False):

    pdf_path = Path(pdf_path)
    output_folder = Path(output_folder)

    image_folder = output_folder / pdf_path.stem
    image_folder.mkdir(parents=True, exist_ok=True)

    existing_images = sorted(image_folder.glob("page_*.png"))

    if existing_images and not force_reconvert:
        print(f"Using existing images for {pdf_path.stem}")
        images = [str(p) for p in existing_images]
    else:
        images = pdf_to_images(
            pdf_path,
            image_folder,
            dpi=400   # reduced from 400 for efficiency
        )

    results = process_pages(images)

    return results


# ============================
# MULTIPROCESS WRAPPER
# ============================

def process_wrapper(pdf_path):

    ps_number = extract_ps_number(pdf_path.name)

    print(f"Processing PS {ps_number}")

    results = process_single_er(
        pdf_path,
        output_folder=r"C:\WEB\scrape\debug\images"
    )

    rows = []

    for section in sorted(results.keys()):
        data = results[section]

        rows.append([
            ps_number,
            section,
            data.get("total", 0),
            data.get("deleted", 0),
            data.get("added", 0),
            data.get("male", 0),
            data.get("female", 0),
            data.get("third", 0),
            data.get("net", 0)
        ])

    return rows


# ============================
# MAIN
# ============================

if __name__ == "__main__":

    pdf_files = sorted(
        PDF_FOLDER.glob("*.pdf"),
        key=lambda x: extract_ps_number(x.name)
    )

    print(f"Total PS files: {len(pdf_files)}")

    # Controlled worker scaling
    workers = min(len(pdf_files), max(2, cpu_count() // 2))
    print(f"Using {workers} CPU cores")

    with Pool(processes=workers) as pool:
        results = pool.map(process_wrapper, pdf_files, chunksize=1)

    all_rows = []

    for ps_rows in results:
        all_rows.extend(ps_rows)

    # Sort final output
    all_rows.sort(key=lambda x: (x[0], x[1]))

    # Write CSV
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:

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

    print(f"\nParallel PS CSV exported → {OUTPUT_CSV}")