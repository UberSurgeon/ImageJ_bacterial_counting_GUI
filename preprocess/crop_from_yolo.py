#!/usr/bin/env python3
from pathlib import Path
import sys
import subprocess
import os
from typing import Literal
from PIL import Image
import include.utils as utils 
from preprocess.yolov7.detect import run_detection
import shutil


def cropFromYolo(images_dir: str | os.PathLike, out_root: str | os.PathLike) -> str:

    def getDst(dst: Literal['Y7_DETECT', 'Y7_PROJECT', 'Y7_WEIGHTS']) -> str:
        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS
        else:
            BASE_DIR = sys.path[0]
        if dst == 'Y7_DETECT':
            x = os.path.join('preprocess', 'yolov7', 'detect.py')
        elif dst == 'Y7_PROJECT':
            x = os.path.join('preprocess', 'yolov7', 'runs', 'detect')
        elif dst == 'Y7_WEIGHTS':
            x = os.path.join('preprocess', 'best.pt')
        else:
            raise ValueError(f'unknown dst key: {dst}')
        return os.path.join(BASE_DIR, x)

    NAMES = "petri_dish,textbox"
    IMG_SIZE = 1024
    MIN_CONF = 0.25

    D = {"dish", "petri_dish"}
    L = {"textbox"}
    B = 10
    X = 0.35
    T = 20
    R1, R2 = 0.1, 2.5
    P = 2

    def cx(b): return (b[0] + b[2]) / 2
    def cy(b): return (b[1] + b[3]) / 2

    def y2x(cx_n, cy_n, w_n, h_n, W, H):

        cx = cx_n * W
        cy = cy_n * H
        w = w_n * W
        h = h_n * H

        x1 = max(0, int(cx - w / 2))
        y1 = max(0, int(cy - h / 2))
        x2 = min(W, int(cx + w / 2))
        y2 = min(H, int(cy + h / 2))
        return x1, y1, x2, y2

    def xo(a, b):

        ax1, _, ax2, _ = a
        bx1, _, bx2, _ = b

        inter = max(0, min(ax2, bx2) - max(ax1, bx1))
        width_a = ax2 - ax1
        width_b = bx2 - bx1
        denom = min(width_a, width_b)
        return inter / denom if denom > 0 else 0.0

    def split(boxes):
        if len(boxes) <= 1:
            return list(range(len(boxes))), []
        rows = sorted(((cy(bb), i) for i, bb in enumerate(boxes)))
        gaps = [(rows[i + 1][0] - rows[i][0], i) for i in range(len(rows) - 1)]
        k = max(gaps, key=lambda t: t[0])[1]
        return [i for _, i in rows[:k + 1]], [i for _, i in rows[k + 1:]]

    def sort_lr(idx, boxes): return sorted(idx, key=lambda i: cx(boxes[i]))

    def detect(imgs_dir: Path, name: str = "auto_pred") -> Path:
        # print(">>> detect() called <<<")
        imgs = str(imgs_dir.resolve())
        # project = str(Path(getDst('Y7_PROJECT')).resolve())
        project_path = Path(getDst('Y7_PROJECT')).resolve()
        for old_run in project_path.glob(f"{name}*"):
            shutil.rmtree(old_run, ignore_errors=True) 
        project = str(project_path)
        run_detection(
            weights=Path(getDst('Y7_WEIGHTS')).resolve(),
            source=str(imgs),
            img_size=IMG_SIZE,
            conf_thres=MIN_CONF,
            save_txt=True,
            save_conf=True,
            project=project,
            name=name,
        )
        base = Path(project)
        runs = sorted(base.glob(f"{name}*"), key=lambda p: p.stat().st_mtime, reverse=True)
        for r in runs:
            lbl = r / "labels"
            if lbl.exists() and any(lbl.glob("*.txt")):
                return lbl
        return Path(project) / name / "labels"

    imgs = Path(images_dir).expanduser().resolve()
    utils.log_message('debug', f"for croping in folder {imgs} there are {os.listdir(images_dir)}")
    if not imgs.exists():
        raise SystemExit(f"images folder not found: {imgs}")

    classes = [s.strip() for s in NAMES.split(",") if s.strip()]
    idm = {n: i for i, n in enumerate(classes)}
    dish_ids = [idm[n] for n in classes if n in D]
    label_ids = [idm[n] for n in classes if n in L]
    if not dish_ids:
        raise SystemExit("dish class missing in NAMES")

    labels_dir = detect(imgs)
    out = Path(out_root).expanduser().resolve() / imgs.name

    if out.exists():
        for p in out.rglob("*"):
            if p.is_file():
                try:
                    p.unlink()
                except:
                    pass

    dishes_dir = out / "dishes"
    labels_out = out / "labels"
    dishes_dir.mkdir(parents=True, exist_ok=True)
    labels_out.mkdir(parents=True, exist_ok=True)

    def _save_crops(im, W, H, stem, dishes, labels):
        dt, db = split(dishes)
        dt, db = sort_lr(dt, dishes), sort_lr(db, dishes)
        if labels:
            lt, lb = split(labels)
            lt, lb = sort_lr(lt, labels), sort_lr(lb, labels)
        else:
            lt, lb = [], []
        used = set()

        def go(d_ids, l_ids, off):
            for k, di in enumerate(d_ids):
                db = dishes[di]; idx = off + k
                d_crop = im.crop((max(0, db[0] - P), max(0, db[1] - P), min(W, db[2] + P), min(H, db[3] + P)))
                if l_ids:
                    cands = []
                    for lj in l_ids:
                        if lj in used:
                            continue
                        lb = labels[lj]
                        if cy(lb) <= cy(db) + B:
                            continue
                        if xo(db, lb) < X:
                            continue
                        cands.append((abs(cx(db) - cx(lb)), lj))
                    if cands:
                        cands.sort(key=lambda t: t[0])
                        j = cands[0][1]
                        used.add(j)
                        lb = labels[j]
                        l_crop = im.crop((max(0, lb[0] - P), max(0, lb[1] - P), min(W, lb[2] + P), min(H, lb[3] + P)))
                        d_crop.save(dishes_dir / f"{stem}_D{idx:02d}.jpg", quality=95)
                        l_crop.save(labels_out / f"{stem}_L{idx:02d}.jpg", quality=95)
                    else:
                        d_crop.save(dishes_dir / f"{stem}_D{idx:02d}_nolabel.jpg", quality=95)
                else:
                    d_crop.save(dishes_dir / f"{stem}_D{idx:02d}_nolabel.jpg", quality=95)

        go(dt, lt, 0)
        go(db, lb, len(dt))

    for txt in sorted(labels_dir.glob("*.txt")):
        stem = txt.stem
        img = None
        for e in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
            p = imgs / f"{stem}{e}"
            if p.exists():
                img = p
                break
        if img is None:
            continue

        with Image.open(img).convert("RGB") as im:
            W, H = im.size
            dishes, labels = [], []
            for line in txt.read_text(encoding="utf-8").splitlines():
                a = line.split()
                if len(a) < 5:
                    continue
                c = int(float(a[0]))
                cx_, cy_, bw, bh = map(float, a[1:5])
                conf = float(a[5]) if len(a) >= 6 else 1.0
                if conf < MIN_CONF:
                    continue
                box = y2x(cx_, cy_, bw, bh, W, H)
                if c in dish_ids:
                    dishes.append(box)
                elif c in label_ids:
                    labels.append(box)
            if not dishes:
                continue
            if labels:
                mn = min(b[0] for b in dishes) - T
                mx = max(b[2] for b in dishes) + T
                widths = [b[2] - b[0] for b in labels]
                med = sorted(widths)[len(widths) // 2] if widths else 0
                labels = [
                    lb for lb in labels
                    if mn <= cx(lb) <= mx and (med == 0 or (R1 * med <= (lb[2] - lb[0]) <= R2 * med))
                ]
            _save_crops(im, W, H, stem, dishes, labels)

    return str(out)


def main():
    if len(sys.argv) < 3:
        print("Usage: cropFromYolo <images_dir> <out_root>", file=sys.stderr)
        sys.exit(2)
    images_dir = sys.argv[1]
    out_root = sys.argv[2]
    print(cropFromYolo(images_dir, out_root))


if __name__ == "__main__":
    main()
