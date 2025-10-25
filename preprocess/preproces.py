from preprocess.crop_from_yolo import cropFromYolo
from preprocess.minicpm_predict import predict_labels
import include.utils as utils

import os
import re
from pathlib import Path
from typing import List, Dict

def preprocess(path: str, outPath: str) -> List[Dict[str, str]]:
    out = cropFromYolo(path, outPath)

    utils.log_message('info', f'cropping in -> {path}')
    try:
        out = cropFromYolo(path, outPath)
    except Exception as e:
        utils.errorMsg('preprocess', f'error -> {e}')

    dishPath = os.path.join(out, 'dishes')
    labelPath = os.path.join(out, 'labels')

    dishList = []
    labelList = []

    for filename in os.listdir(dishPath):
        p = os.path.normpath(os.path.join(dishPath, filename))
        if os.path.isfile(p):
            dishList.append(p)

    for filename in os.listdir(labelPath):
        p = os.path.normpath(os.path.join(labelPath, filename))
        if os.path.isfile(p):
            labelList.append(p)

    def pair_dish_label(dish_list: List[str], label_list: List[str]) -> List[Dict[str, str]]:
        pattern = re.compile(r"(?P<prefix>.+)_(?P<type>[DL])(?P<index>\d+)(?:_[^.]*)?\.[^.]+$")

        def parse(files):
            parsed = {}
            for f in files:
                name = os.path.basename(f)
                m = pattern.match(name)
                if m:
                    key = (m.group("prefix"), m.group("index"))
                    parsed[key] = f
            return parsed

        dishes = parse(dish_list)
        labels = parse(label_list)

        result = []
        for key, dish_path in dishes.items():
            label_path = labels.get(key, "")
            result.append({
                "img_path": dish_path,
                "label_path": label_path,
                "name": ""
            })
        return result

    pairs = pair_dish_label(dishList, labelList)
    
    utils.log_message('info', f'pair in -> {pairs}')

    label_paths = [Path(p["label_path"]) for p in pairs if p["label_path"]]

    utils.log_message('info', f'start predicting label in -> {label_paths}')
    try:
        preds = predict_labels(label_paths)
    except Exception as e:
        utils.errorMsg('preprocess', f'predict_labels-error -> {e}')
 
    by_name = {os.path.basename(p["image"]): p for p in preds}

    enriched = []
    for item in pairs:
        lp = os.path.basename(item["label_path"]) if item["label_path"] else ""
        r = by_name.get(lp, {"prediction": "", "confidence": 0.0})
        enriched.append({
            **item,
            "prediction": r["prediction"],
            "confidence": r["confidence"],
        })
    return enriched

if __name__ == "__main__":
    demo = preprocess("./preprocess/E1", "out")
    for row in demo:
        print(row)
