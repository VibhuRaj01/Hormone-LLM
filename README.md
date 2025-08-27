# 🧠 Emotion-Driven Hormone Simulation

This project simulates a **hormone system influenced by emotions** using a Hugging Face emotion classification model.  
Each input text is analyzed, mapped to an emotion, and translated into hormone level changes that simulate psychological and physiological effects.  

---

## 🚀 How It Works

1. **Emotion Detection**  
   The system uses [`cardiffnlp/twitter-roberta-base-emotion`](https://huggingface.co/cardiffnlp/twitter-roberta-base-emotion) to classify emotions from text.

2. **Hormone Mapping**  
   Each detected emotion is mapped to a set of **hormone changes** (increases or decreases).

3. **Decay Mechanism**  
   Hormones naturally **decay back toward baseline** over time to avoid permanent extremes.

4. **Confidence Weighting**  
   The intensity of hormone changes depends on the **confidence score** of the emotion classifier.

5. **Clamping**  
   Hormone levels are always kept in the range **[0.0, 1.0]**.

---

## 🧪 Hormones in the System

| Hormone        | Role in Simulation                                                               |
|----------------|----------------------------------------------------------------------------------|
| **Dopamine**   | Motivation, reward, excitement. Boosted by joy, love, and optimism.              |
| **Serotonin**  | Mood stability, calmness, long-term happiness. Reduced by sadness and fear.      |
| **Cortisol**   | Stress hormone. Increases with fear and anger, decreases with joy.               |
| **Oxytocin**   | Bonding, trust, and love. Boosted when detecting love or optimism.               |
| **Confidence** | Represents self-assurance and assertiveness. Strengthened by anger and optimism. |

---

## 🎭 Emotion → Hormone Effects

| Emotion      | Hormone Changes                                                               |
|--------------|-------------------------------------------------------------------------------|
| **Joy**      | ↑ Dopamine (+0.2), ↑ Serotonin (+0.15), ↓ Cortisol (-0.1)                     |
| **Optimism** | ↑ Dopamine (+0.15), ↑ Serotonin (+0.1), ↑ Oxytocin (+0.05)                    |
| **Sadness**  | ↓ Serotonin (-0.2), ↑ Cortisol (+0.1), ↓ Dopamine (-0.1)                      |
| **Anger**    | ↑ Cortisol (+0.25), ↑ Confidence (+0.1), ↓ Serotonin (-0.15)                  |
| **Fear**     | ↑ Cortisol (+0.3), ↓ Serotonin (-0.1)                                         |
| **Love**     | ↑ Oxytocin (+0.3), ↑ Dopamine (+0.1), ↑ Serotonin (+0.1)                      |

All values are **scaled by confidence score** from the classifier.

---

## ⚖️ Decay System

- Each turn, hormones **decay toward their baseline values**.
- Formula: new_value = baseline + (current - baseline) * DECAY_RATE

- Default decay rate: **0.9** (slow drift toward baseline).

---
