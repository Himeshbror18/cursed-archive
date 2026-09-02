# Real-time-GesRec hand-sign bridge

The Domain Expansion simulator now has a **local Python gesture-recognition path** based on the architecture in [ahmetgunduz/Real-time-GesRec](https://github.com/ahmetgunduz/Real-time-GesRec).

The important catch: the upstream pretrained models are trained for datasets such as EgoGesture, nvGesture, Jester, Kinetics and UCF101. They do **not** contain the six Jujutsu Kaisen hand seals used by this project. The bridge therefore expects a **custom six-class checkpoint** trained/fine-tuned for these signs. citeturn1search0

## Layout

```text
Browser camera
      │ JPEG frames
      ▼
gesture_bridge/server.py
      │
      │ 16-frame RGB clip
      ▼
Real-time-GesRec model
      │
      ▼
class_id + confidence
      │
      ▼
gesture_map.json
      │
      ▼
Domain Expansion + character FX
```

The upstream project itself uses a detector/classifier and a temporal sliding-window approach for online recognition, which is why this bridge keeps a frame buffer instead of treating each webcam frame as an isolated gesture. citeturn1search0

## Setup

Clone the upstream project outside this repository:

```bash
git clone https://github.com/ahmetgunduz/Real-time-GesRec.git vendor/Real-time-GesRec
```

Install this bridge:

```bash
pip install -r gesture_bridge/requirements.txt
```

Then provide a custom checkpoint:

```bash
python gesture_bridge/server.py \
  --gesrec-root vendor/Real-time-GesRec \
  --checkpoint path/to/cursed_archive_gestures.pth
```

The server listens on:

```text
http://127.0.0.1:8765
```

Health check:

```text
GET /health
```

Prediction:

```text
POST /predict
{"image":"data:image/jpeg;base64,..."}
```

## Training the six seals

Do **not** map arbitrary upstream gesture classes to JJK characters and call it done. That would look impressive until someone actually makes the hand sign.

Record short RGB clips for:

1. Gojo / Unlimited Void
2. Megumi / Chimera Shadow Garden
3. Sukuna / Malevolent Shrine
4. Mahito / Self-Embodiment of Perfection
5. Yuji / Domain Amplification
6. Cursed Technique Ember

Keep multiple performers, lighting conditions, distances, orientations and backgrounds in the dataset. Fine-tune the upstream temporal model and export the resulting checkpoint with six output classes.

The upstream project provides training/fine-tuning code and pretrained models, so this bridge deliberately reuses that architecture instead of pretending six static finger counts are temporal gesture recognition. citeturn1search0

## License / credit

This bridge is an integration layer around the work by **Ahmet Gunduz, Okan Köpüklü, Neslihan Kose and Gerhard Rigoll**.

Please retain the upstream project's license and citation requirements when using its source code or pretrained models. The upstream repository documents the associated 2019 and 2020 papers and its license/resources. citeturn1search0
