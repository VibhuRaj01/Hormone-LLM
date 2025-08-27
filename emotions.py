from transformers import pipeline
import os, json
import warnings

warnings.filterwarnings("ignore")

STATE_FILE = "hormone_state.json"

# ---------- constants ----------
DECAY_RATE = 0.9
BASELINE = {
    "dopamine": 0.4,
    "serotonin": 0.5,
    "cortisol": 0.2,
    "oxytocin": 0.4,
    "confidence": 0.5,
}

emotion_to_hormone_map = {
    "joy": {"dopamine": 0.2, "serotonin": 0.15, "cortisol": -0.1},
    "optimism": {"dopamine": 0.15, "serotonin": 0.1, "oxytocin": 0.05},
    "sadness": {"serotonin": -0.2, "cortisol": 0.1, "dopamine": -0.1},
    "anger": {"cortisol": 0.25, "confidence": 0.1, "serotonin": -0.15},
    "fear": {"cortisol": 0.3, "serotonin": -0.1},
    "love": {"oxytocin": 0.3, "dopamine": 0.1, "serotonin": 0.1},
}

# ---------- load / initialise ----------
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        hormone_state = json.load(f)
else:
    hormone_state = BASELINE.copy()
    with open(STATE_FILE, "w") as f:
        json.dump(BASELINE, f)

# ---------- model ----------
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    return_all_scores=False,
)


# ---------- functions ----------
def update_hormone_levels(text_input, current_state):
    for h, v in current_state.items():
        current_state[h] = BASELINE[h] + (v - BASELINE[h]) * DECAY_RATE

    try:
        res = emotion_classifier(text_input)[0]
        emotion, conf = res["label"].lower(), res["score"]
        print(f"Detected Emotion: {emotion} (conf={conf:.2f})")
        if emotion in emotion_to_hormone_map:
            for h, delta in emotion_to_hormone_map[emotion].items():
                current_state[h] += delta * conf
    except Exception as e:
        print("Emotion classification failed:", e)

    for h in current_state:
        current_state[h] = max(0.0, min(1.0, current_state[h]))
    return current_state


def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(hormone_state, f)


# ---------- example ----------
# if __name__ == "__main__":
#     print("Initial state:", {k: round(v, 2) for k, v in hormone_state.items()})
#     txt = "Thankyou for your answer!"
#     hormone_state = update_hormone_levels(txt, hormone_state)
#     save_state()
#     print("State saved. Bye!")
#     print({k: round(v, 2) for k, v in hormone_state.items()})
