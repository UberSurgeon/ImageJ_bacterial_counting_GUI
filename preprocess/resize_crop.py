import os
from PIL import Image

def normSize(folder_path):
    resized_folder = os.path.join(folder_path)
    os.makedirs(resized_folder, exist_ok=True)


    exts = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp")
    target_size = (792, 822)  # (width, height)

    for name in os.listdir(folder_path):
        if not name.lower().endswith(exts):
            continue

        img_path = os.path.join(folder_path, name)
        img = Image.open(img_path).convert("RGB")

        # --- resize ---
        resized = img.resize(target_size, Image.LANCZOS)
        resized_path = os.path.join(resized_folder, name)
        resized.save(resized_path)

