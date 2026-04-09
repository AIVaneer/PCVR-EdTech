# PCVR-EdTech

An immersive, interactive PCVR educational experience built for **Pythonista 3** on iOS.

## Features

| Feature | Details |
|---|---|
| **Animated splash screen** | Pulsating title with starfield warp effect |
| **Username entry** | Personalised greeting carried through every scene |
| **PCVR overview** | Glow-ring pulse animation, staggered bullet reveal |
| **5 themed learning pages** | Each lesson has a unique background hue, slide-in text, and staggered line fade-in |
| **Button press effects** | Screen shake + white flash + particle burst + sound on every press |
| **Enhanced particles** | Colourful burst particles (vibrant HSV palette) on all interactions |
| **Dynamic sound effects** | Different arcade/digital sound per scene transition |
| **Smooth transitions** | Black fade-out → state switch → black fade-in between every scene |
| **Warp Protocol arcade game** | Full arcade shooter demo: jump, shoot, shields, health, bull mode, 4 themed sectors |

## How to Run

1. Install **Pythonista 3** on your iPhone or iPad.
2. Copy `pcvr_edtech.py` into Pythonista.
3. Tap ▶ to run.

> The app runs in **portrait** orientation.
> Tap to progress through scenes; in the game, tap to jump and shoot.

## Scene Flow

```
Splash → Username → PCVR Overview → Lesson 1–5 → Warp Protocol Intro → Gameplay
```

After game-over: **short tap** = retry mission · **long hold (>0.6 s)** = back to lessons.

## Learning Content

| # | Topic |
|---|---|
| 1 | What is PCVR? |
| 2 | Core hardware components |
| 3 | How GPU rendering works end-to-end |
| 4 | Writing your first VR code loop |
| 5 | Performance optimisation tips |

## License

MIT — see [LICENSE](LICENSE).
