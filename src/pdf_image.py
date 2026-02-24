from pdf2image import convert_from_path
from pathlib import Path
from tqdm import tqdm



def pdf_to_images(pdf_path, output_folder, dpi=400, poppler_path=None):


    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"Converting PDF to images at {dpi} DPI...")

    images = convert_from_path(
        pdf_path,
        dpi=dpi,
        poppler_path=poppler_path
    )

    image_paths = []

    for i, img in tqdm(enumerate(images), total=len(images)):
        image_path = output_folder / f"page_{i+1:03}.png"
        img.save(image_path, "PNG")
        image_paths.append(str(image_path))

    print("Conversion complete.")
    return image_paths