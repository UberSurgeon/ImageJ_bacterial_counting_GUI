#!/usr/bin/env python3
import io, json, base64, re, time, subprocess
from pathlib import Path
from typing import Iterable, List, Dict, Any
from urllib import request
from PIL import Image

MODEL      = "minicpm-v:latest"
OLLAMA_URL = "http://localhost:11434/api"
PROMPT     = ("Read the printed sample ID on this label. "
              "Return only the ID (letters+digits, no spaces, no extra words).")
VALID_RX   = re.compile(r"^[A-Z]?\d{1,4}[A-Z]?$", re.I)

def _norm(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", (s or "")).upper()

def _b64(p: Path) -> str:
    with Image.open(p).convert("RGB") as im:
        buf = io.BytesIO(); im.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode()

def _lev(a: str, b: str) -> int:
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    prev = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(cur[j-1]+1, prev[j]+1, prev[j-1] + (ca != cb)))
        prev = cur
    return prev[-1]

def _sim(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    d = _lev(a, b)
    return max(0.0, 1.0 - d / max(len(a), len(b)))

def _heur_conf(pred_norm: str) -> float:
    if VALID_RX.fullmatch(pred_norm or ""): return 0.9
    L = len(pred_norm or "")
    return 0.0 if L == 0 else max(0.1, min(0.8, L / 10.0))

def _ping() -> bool:
    try:
        with request.urlopen(f"{OLLAMA_URL}/version", timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def ensure_ollama_ready(timeout_sec: int = 20) -> None:
    if _ping(): return 'FOUND'
    subprocess.Popen(["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True)
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        if _ping(): return 'FOUND'
        time.sleep(0.5)
    raise RuntimeError("Ollama API not available at http://localhost:11434")

def _ask(img_b64: str, timeout: int = 120) -> str:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT, "images": [img_b64]}],
        "stream": False,
    }
    data = json.dumps(payload).encode()
    req = request.Request(f"{OLLAMA_URL}/chat", data=data,
                          headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read().decode())
    return (out.get("message", {}).get("content") or out.get("response", "") or "").strip()

def predict_labels(label_paths: Iterable[Path]) -> List[Dict[str, Any]]:
    ensure_ollama_ready()

    results: List[Dict[str, Any]] = []
    for p in label_paths:
        try:
            raw = _ask(_b64(p))
        except Exception:
            raw = ""  
        pred = _norm(raw)  

        conf = _heur_conf(pred)

        results.append({
            "image": str(p),
            "prediction": pred if pred else "",
            "confidence": round(float(conf), 3),
        })

    return results
