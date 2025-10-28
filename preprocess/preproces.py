from preprocess.crop_from_yolo import cropFromYolo
from preprocess.minicpm_predict import predict_labels
import include.utils as utils
from include.loading import LoadingWindow

import os
import re
from pathlib import Path
from typing import List, Dict
import time

cropping = LoadingWindow("cropping...", spinner=True)
labeling = LoadingWindow("reading Label...", spinner=True)

def preprocess(path: str, outPath: str, labeling_toggle: int) -> List[Dict[str, str]]:
    utils.log_message('info', f'cropping in -> {path}')
    try:
        cropping.start()
        start = time.time()
        out = cropFromYolo(path, outPath)
        print(f'time taken to crop {time.time() - start}')
        cropping.stop()
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

    
    if (labeling_toggle == 1):
        utils.log_message('info', f'start predicting label in -> {label_paths}')
        try:
            labeling.start()
            start = time.time()
            preds = predict_labels(label_paths)
            print(f'time taken to label {time.time() - start}')
            labeling.stop()
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
    else:
        utils.log_message('info', 'user dont want to predict label')
        # fill prediction with "" and confidence with 0.0
        enriched = []
        for item in pairs:
            enriched.append({
                **item,
                "prediction": "",
                "confidence": 0.0,
            })
        return enriched


if __name__ == "__main__":
    demo = preprocess("./preprocess/E1", "out")
    for row in demo:
        print(row)
