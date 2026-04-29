# 🧠 PCVR EdTech — AI Handoff Document

> Purpose: Give any AI system (Claude, GPT, Gemini, Copilot, etc.) full context on the PCVR EdTech project so it can continue building safely without breaking what already works.

---

## 1. Project Identity

- **Project Name:** PCVR EdTech
- **Owner / Builder:** AIVaneer (GitHub: https://github.com/AIVaneer)
- **Repository:** https://github.com/AIVaneer/PCVR-EdTech
- **Live Host:** GitHub Pages
- **Live Root URL:** https://aivaneer.github.io/PCVR-EdTech/
- **Mission Motto:** *"Always for good, never for bad."*
- **Tone:** Dark neon, cyberpunk, cinematic, motivating, gamified.

---

## 2. What PCVR Is

PCVR EdTech is a **gamified learning system** that teaches real coding (starting with Python) through a story-driven game called **Code Raiders**. Users scan a QR code, land on a hero page, and progress through "levels" where they fix broken code to unlock the next world.

It is part of a larger ecosystem:
- **Code Raiders** = the public-facing game (live now).
- **$PCVR Loop System** = future tokenized "Move to Learn / Buy to Learn" reward layer (not built yet — placeholder only).
- **Atlas Infinity Core** = private Tier 3 AI orchestration system (not in this repo, internal only).

---

## 3. Repository Structure

```
PCVR-EdTech/
├── index.html                 # Root landing page (PCVR EdTech home)
├── README.md
├── LICENSE
├── AI_HANDOFF.md              # This file
└── code-raiders/
    ├── index.html             # Code Raiders entry / level selector
    ├── level-1.html           # World 1 — Level 1
    ├── level-2.html           # World 1 — Level 2
    ├── level-3.html           # World 1 — Level 3 (Loop Gate)
    ├── level-4.html           # World 2 — Level 4 (Variable Core, Fire Cave)
    └── portal.html            # Portal Hub (navigation between worlds + links)
```

**DO NOT** modify or delete any file unless the user explicitly approves the file name and the change.

---

## 4. User Flow (Current)

```
QR code  →  Landing (/)  →  code-raiders/index.html
        →  level-1.html  →  level-2.html  →  level-3.html
        →  portal.html  →  level-4.html  →  portal.html
```

The Portal Hub is the central navigation point. From there the user can:
- Re-enter Code Raiders Worlds
- See locked World 1 and World 2 cards (toast popup — coming soon)
- Visit the PCVR EdTech landing
- Visit AIVaneer's GitHub
- Visit the PCVR EdTech repo
- See "coming soon" cards for $PCVR Loop and Atlas Infinity

---

## 5. Level Design Pattern (IMPORTANT — follow exactly)

Every level is a **single self-contained HTML file** with:
1. `<style>` block (no external CSS).
2. A `.code-box` showing broken code with `white-space: pre;` so line breaks render correctly. **Never use `<br>` or `&nbsp;` for code formatting.**
3. A `<textarea id="input">` where the player types the fix.
4. Two buttons: **Run Code** and **Need a hint?**
5. A `<div id="terminal">` for ✅ CORRECT / ❌ TRY AGAIN feedback.
6. A hidden `<div id="unlock">` shown on success, with a button linking to `./portal.html`.
7. A `<script>` containing `normalize()`, `runCode()`, `hint()`.

### Normalize function (used in every level)
```js
function normalize(str) {
  return str.replace(/\s+/g, "").replace(/'/g, '"').toLowerCase();
}
```
This makes the answer-checker forgiving of whitespace, single vs double quotes, and case.

### World theming (visual identity)
- **World 1 (Levels 1–3):** Green `#4ade80` + Cyan `#38bdf8` on dark blue/black radial gradient.
- **World 2 (Levels 4+):** Orange `#fb923c` + Yellow `#facc15` on **fire red → black** radial gradient (`#7f1d1d` → `#020617` → `#000`).
- Each future world should get its own color palette but follow the same structural pattern.

---

## 6. Levels Already Built

| Level | World | Mission        | Broken Code                          | Correct Answer                            | Concept Taught          |
|-------|-------|----------------|--------------------------------------|--------------------------------------------|-------------------------|
| 1     | 1     | (intro)        | (see file)                           | (see file)                                 | print syntax            |
| 2     | 1     | (intro)        | (see file)                           | (see file)                                 | basic syntax            |
| 3     | 1     | Loop Gate      | `for i in range(3)` (missing colon)  | `for i in range(3):` + `    print("PCVR")` | for-loops + colons      |
| 4     | 2     | Variable Core  | `name = PCVR`                        | `name = "PCVR"`                            | strings need quotes     |

> **Note:** All levels exist as files and work individually, but the Portal Hub currently shows World 1 and World 2 as 🔒 LOCKED while more levels are being built. The QR/landing flow into `code-raiders/index.html` still works directly.

---

## 7. Portal Hub (`code-raiders/portal.html`)

A mobile-friendly card grid. Each card is either an `<a class="card">` (link), an `<a class="card locked" data-locked="World N">` (locked with toast popup), or a `<div class="card info">` (placeholder).

Current cards (in order):
1. 🛡️ **Code Raiders Worlds** → `./index.html` (LIVE, green)
2. 🔒 **World 1 Locked** → toast popup "Coming soon" (LOCKED — temporary while expanding)
3. 🔒 **World 2 Locked** → toast popup "Coming soon" (LOCKED — temporary while expanding)
4. 🌐 **PCVR EdTech Landing** → `../` (LIVE)
5. 👤 **AIVaneer GitHub** → `https://github.com/AIVaneer` (LIVE)
6. 📦 **PCVR EdTech Repo** → `https://github.com/AIVaneer/PCVR-EdTech` (LIVE)
7. 🪙 **$PCVR Loop System** — placeholder (SOON, gold)
8. 🔐 **Atlas Infinity Core** — placeholder (LOCKED, muted)

Locked cards use a toast popup (no navigation) via `data-locked="World N"` + a small JS toast at the bottom of `portal.html`. To unlock a world later, replace the locked `<a>` with a real link card and remove the `data-locked` attribute.

When new worlds are built, add a new green card linking to the first level of that world.

---

## 8. Build Rules (CRITICAL — for any AI continuing this work)

1. **One safe step at a time.** Never bundle multiple file changes in one commit unless explicitly approved.
2. **Confirm before writing.** Always describe the change first, then push only after the user accepts.
3. **Never delete files.** Only create or update the exact file the user names.
4. **Never modify Level 1, 2, 3, 4, portal.html, index.html, README, or LICENSE unless the user names that exact file.**
5. **Never change GitHub Pages settings or QR destination.**
6. **Code formatting in `.code-box`** must use `white-space: pre;` and real newlines — never `<br>` or `&nbsp;`.
7. **Style consistency:** match the World palette. World 1 = green/cyan. World 2 = orange/yellow on red. Future worlds get their own palette but same structure.
8. **Every level ends with a "Return to Portal Hub" button** linking to `./portal.html`.
9. **Commit messages** must be short and descriptive (e.g., `Add Code Raiders Level 5 Function Forge`).
10. **Report after every commit:** file changed, commit hash, and live URL.

---

## 9. Roadmap (Planned, Not Built Yet)

- **World 2 expansion:** Levels 5, 6 (Fire Cave continues — functions, conditionals).
- **World 3:** Ice Spire (lists, loops over data).
- **World 4:** Sky Temple (dictionaries, JSON).
- **World 5:** Void Core (classes, OOP).
- **$PCVR Loop integration:** reward tracking page (no real token yet).
- **Atlas Infinity Core:** stays private, never exposed in this repo.

---

## 10. Hand-Off Summary for the Next AI

> You are continuing the PCVR EdTech build for AIVaneer.
> The system is a gamified Python-learning game called **Code Raiders**, hosted on GitHub Pages.
> Levels 1–4 exist as files, but the Portal Hub currently shows both worlds as 🔒 LOCKED with a "coming soon" toast while AIVaneer expands the level set.
> A central **Portal Hub** routes users between locked worlds, the landing page, and external links.
> Follow the level pattern in Section 5, the build rules in Section 8, and never modify files the user did not name.
> Always confirm before writing. Always report commit hash + live URL after pushing.
> Motto: **Always for good, never for bad.**

---

*Last updated: 2026-04-29*
