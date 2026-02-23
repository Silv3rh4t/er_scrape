from pathlib import Path
from process_pdf import process_pages

IMAGE_FOLDER = Path(r"C:\WEB\scrape\debug\images")

images = sorted(
    IMAGE_FOLDER.glob("page_*.png"),
    key=lambda p: int(p.stem.split("_")[1])
)

images = [str(p) for p in images]

results = process_pages(images)

for sec, data in results.items():
    print(f"Section {sec}:")
    print(data)