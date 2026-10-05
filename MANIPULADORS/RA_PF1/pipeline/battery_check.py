import os
import cv2
import numpy as np
import time
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(SCRIPT_DIR, "battery_model.joblib")

def extract_features(roi):
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h_ch, s_ch, v_ch = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    b, g, r = roi[:, :, 0].astype(float), roi[:, :, 1].astype(float), roi[:, :, 2].astype(float)
    total = roi.shape[0] * roi.shape[1]
    features = []

    # Blue/Cyan extraction
    for s_min, v_min in [(30, 60), (40, 80), (40, 100), (50, 100)]:
        mask = cv2.inRange(hsv, np.array([80, s_min, v_min]), np.array([115, 255, 255]))
        features.append(cv2.countNonZero(mask) / total)

    # Yellow extraction
    for h_lo, h_hi, s_min, v_min in [(15, 35, 40, 70), (20, 40, 50, 80), (20, 35, 60, 90), (15, 40, 40, 70)]:
        mask = cv2.inRange(hsv, np.array([h_lo, s_min, v_min]), np.array([h_hi, 255, 255]))
        features.append(cv2.countNonZero(mask) / total)

    features.append((v_ch < 40).sum() / total)
    features.append((v_ch < 60).sum() / total)
    features.append((v_ch < 80).sum() / total)
    features.append((v_ch > 180).sum() / total)

    nd = v_ch >= 60
    nd_count = nd.sum()
    if nd_count > 100:
        features.append(h_ch[nd].mean() / 180.0)
        features.append(h_ch[nd].std() / 180.0)
        features.append(s_ch[nd].mean() / 255.0)
        features.append(v_ch[nd].mean() / 255.0)
        features.append(b[nd].mean() / 255.0)
        features.append(g[nd].mean() / 255.0)
        features.append(r[nd].mean() / 255.0)
        bm, gm, rm = b[nd].mean(), g[nd].mean(), r[nd].mean()
        features.append((bm - rm) / 255.0)
        features.append((gm - rm) / 255.0)
        features.append((gm - bm) / 255.0)
    else:
        features.extend([0] * 10)

    if nd_count > 100:
        hist, _ = np.histogram(h_ch[nd], bins=6, range=(0, 180))
        features.extend((hist / hist.sum()).tolist())
    else:
        features.extend([0] * 6)

    return np.array(features, dtype=np.float32)


def rule_based_predict(roi):
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    total = roi.shape[0] * roi.shape[1]
    
    # Blue/Cyan = defective, Yellow = good
    blue_cyan = cv2.countNonZero(cv2.inRange(hsv, np.array([80, 40, 90]), np.array([115, 255, 255])))
    yellow = cv2.countNonZero(cv2.inRange(hsv, np.array([15, 40, 80]), np.array([40, 255, 255])))
    
    if blue_cyan / total > 0.05:
        return "defective"
    if yellow / total > 0.05:
        return "good"
    return "unknown"


def predict_slot(roi, model_data=None):
    pred_rule = rule_based_predict(roi)
    if model_data is None:
        return pred_rule
    feat = extract_features(roi)
    pred_rf = model_data["rf"].predict([feat])[0]
    pred_gb = model_data["le"].inverse_transform(model_data["gb"].predict([feat]))[0]
    votes = [pred_rf, pred_rule, pred_gb]
    return Counter(votes).most_common(1)[0][0]


def analyze_batteries(countdown_seconds=5):
    """
    Opens the webcam, runs a countdown, takes a snapshot inside the target alignment box,
    analyzes the two battery slots, and returns their states.
    
    Returns:
        tuple: (state_slot_1, state_slot_2) e.g., ("good", "defective")
    """
    model_data = None
    if os.path.exists(MODEL_FILE):
        import joblib
        try:
            model_data = joblib.load(MODEL_FILE)
        except Exception:
            pass

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam.")
        return "error", "error"

    start_time = time.time()
    pos1, pos2 = "unknown", "unknown"
    analysis_done = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        box_w, box_h = int(w * 0.35), int(h * 0.65)
        x = (w - box_w) // 2
        y = (h - box_h) // 2

        # Drawing box grid overlay
        cv2.rectangle(frame, (x, y), (x + box_w, x + box_h), (0, 255, 0), 2)
        cv2.putText(frame, "ALIGN BATTERIES HERE", (x, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        elapsed = time.time() - start_time
        remaining = max(0, countdown_seconds - int(elapsed))

        if remaining > 0:
            cv2.putText(frame, f"Capturing in: {remaining}s", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        else:
            if not analysis_done:
                # Capture and run logic
                roi = frame[y:y+box_h, x:x+box_w]
                mid = roi.shape[1] // 2
                slot1_roi = roi[:, :mid]
                slot2_roi = roi[:, mid:]

                cv2.imwrite(os.path.join(SCRIPT_DIR, "captured_snapshot.png"), roi)

                pos1 = predict_slot(slot1_roi, model_data)
                pos2 = predict_slot(slot2_roi, model_data)
                analysis_done = True
                
                # Break automatically once the snap and classification occurs
                break

        cv2.imshow("Automatic Battery Analyzer Hub", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    return pos1, pos2