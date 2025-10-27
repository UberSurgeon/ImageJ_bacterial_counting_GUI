from pathlib import Path
from PIL import Image
import os
import include.utils as utils

# input_folders = ["E1", "H2", "H4"] # the feed

def reOrientation(imgPath: str):
    img = Image.open(imgPath)
    img_rotated = img.rotate(180)
    if os.path.exists(imgPath):
        try:
            img_rotated.save(imgPath)
            utils.log_message('info', f"Rotated image saved: {imgPath}")
        except Exception as e:
            utils.errorMsg('rotateImage', f'Failed to replace rotated image {imgPath}: {e}')
            utils.log_message('error', f"Failed to replace rotated image {imgPath}: {e}")
