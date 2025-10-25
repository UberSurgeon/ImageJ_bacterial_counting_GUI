from preprocess.crop_from_yolo import cropFromYolo
from preprocess.orientation import reOrientation
import os
import re
from typing import List, Dict
import include.utils as utils


# def preprocess(save_dir, temp_dir):
#     if save_dir is None:
#         path = os.join(temp_dir)

#         # reOrientation(path)
#         cropFromYolo()



def preprocess(path, outPath):
    # reOrientation(path)
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
        path = os.path.normpath(os.path.join(dishPath, filename))
        dishList.append(path)

    for filename in os.listdir(labelPath):
        path = os.path.normpath(os.path.join(labelPath, filename))
        labelList.append(path)

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

    return pair_dish_label(dishList, labelList)

def main():
    path = r'C:\Users\NotEW\Documents\Code\roboai\gui\preprocess\editedTest'
    x = preprocess(path)
    print(x)

if __name__ == '__main__':
    main()
