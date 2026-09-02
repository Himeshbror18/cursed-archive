"""Local gesture-recognition bridge for Cursed Archive.

This adapter uses the model architecture from ahmetgunduz/Real-time-GesRec.
It is intentionally local: the browser sends short RGB frame samples here,
and this service returns a gesture class. A custom checkpoint trained for the
Cursed Archive hand-sign classes is required; the upstream pretrained models
were trained on EgoGesture/nvGesture/Jester/Kinetics/UCF101 and do not
magically know Jujutsu Kaisen seals.
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import os
import sys
from collections import deque
from types import SimpleNamespace

import numpy as np
import torch
from PIL import Image
from flask import Flask, jsonify, request
from flask_cors import CORS


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class GestureEngine:
    def __init__(self, gesrec_root: str, checkpoint: str, classes: int, sample_duration: int, width_mult: float):
        self.root = os.path.abspath(gesrec_root)
        sys.path.insert(0, self.root)

        # Import the upstream architecture rather than copying it into this repo.
        model_module = load_module(os.path.join(self.root, "model.py"), "gesrec_model")
        opts = SimpleNamespace(
            model="shufflenetv2",
            n_classes=classes,
            sample_size=112,
            width_mult=width_mult,
            no_cuda=True,
            modality="RGB",
            pretrain_path="",
            pretrain_modality="RGB",
            n_finetune_classes=classes,
            ft_portion="complete",
            ft_begin_index=0,
            sample_duration=sample_duration,
        )
        self.model, _ = model_module.generate_model(opts)

        state = torch.load(checkpoint, map_location="cpu")
        state = state.get("state_dict", state)
        state = {k.removeprefix("module."): v for k, v in state.items()}
        self.model.load_state_dict(state, strict=True)
        self.model.eval()

        self.sample_duration = sample_duration
        self.frames = deque(maxlen=sample_duration)

    @staticmethod
    def preprocess(frame: np.ndarray) -> torch.Tensor:
        image = Image.fromarray(frame).convert("RGB")
        image = image.resize((112, 112), Image.Resampling.BILINEAR)
        arr = np.asarray(image).astype(np.float32) / 255.0
        arr = (arr - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        return torch.from_numpy(arr).permute(2, 0, 1)

    def predict(self, frame: np.ndarray):
        self.frames.append(self.preprocess(frame))
        if len(self.frames) < self.sample_duration:
            return None

        clip = torch.stack(list(self.frames), dim=1).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(self.model(clip), dim=1)[0]
            confidence, index = torch.max(probabilities, dim=0)

        return {
            "class_id": int(index),
            "confidence": float(confidence),
            "ready": True,
        }


def decode_image(data_url: str) -> np.ndarray:
    if "," in data_url:
        data_url = data_url.split(",", 1)[1]
    raw = base64.b64decode(data_url)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    return np.asarray(image)


def create_app(engine: GestureEngine, gesture_map: dict):
    app = Flask(__name__)
    CORS(app)

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "engine": "Real-time-GesRec", "custom_checkpoint": True})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True) or {}
        image = payload.get("image")
        if not image:
            return jsonify({"ok": False, "error": "missing image"}), 400

        try:
            result = engine.predict(decode_image(image))
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 500

        if result is None:
            return jsonify({"ok": True, "ready": False})

        mapping = gesture_map.get(str(result["class_id"]))
        if mapping is None:
            return jsonify({"ok": True, **result, "mapped": False})

        return jsonify({"ok": True, **result, "mapped": True, **mapping})

    return app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gesrec-root", default=os.environ.get("GESREC_ROOT", "../vendor/Real-time-GesRec"))
    parser.add_argument("--checkpoint", default=os.environ.get("GESREC_CHECKPOINT", ""))
    parser.add_argument("--classes", type=int, default=6)
    parser.add_argument("--sample-duration", type=int, default=16)
    parser.add_argument("--width-mult", type=float, default=0.25)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if not args.checkpoint:
        raise SystemExit("Set --checkpoint to a custom Cursed Archive gesture checkpoint.")

    with open(os.path.join(os.path.dirname(__file__), "gesture_map.json"), encoding="utf-8") as f:
        gesture_map = json.load(f)

    engine = GestureEngine(
        args.gesrec_root,
        args.checkpoint,
        args.classes,
        args.sample_duration,
        args.width_mult,
    )
    create_app(engine, gesture_map).run(host="127.0.0.1", port=args.port, debug=False)


if __name__ == "__main__":
    main()
