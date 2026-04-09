# pcvr_edtech.py
# A combined, interactive PCVR educational experience for Pythonista (iOS).
# Merges LoebShowcase visuals with PCVRRadioUI and adds Code Raiders puzzles.
#
# Scene flow:
#   NAME_ENTRY → INTRO → SHOWCASE (x3 themes) → START → RADIO ↔ CODE_RAIDERS

from scene import *
import ui
import random
import math
import sound


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATE_NAME = "NAME_ENTRY"
STATE_INTRO = "INTRO"
STATE_SHOWCASE = "SHOWCASE"
STATE_START = "START"
STATE_RADIO = "RADIO"
STATE_CODE_RAIDERS = "CODE_RAIDERS"

SHOWCASE_THEMES = [
    {
        "title": "Speed ⚡",
        "subtitle": "Real-time processing. Instant feedback.",
        "detail": "PCVR responds in milliseconds —\njust like a live broadcast.",
        "color": (0.25, 0.84, 1.0),
    },
    {
        "title": "Systems 🌌",
        "subtitle": "Apps · Radio · Cloud · Code — all connected.",
        "detail": "One platform, infinite pipelines.\nBuild the stack from scratch.",
        "color": (0.1, 1.0, 0.6),
    },
    {
        "title": "Vision 🚀",
        "subtitle": "PCVR turns raw ideas into real products.",
        "detail": "Not demos. Real tools.\nDeployed. Scaled. Shipped.",
        "color": (1.0, 0.78, 0.2),
    },
]

RADIO_STATIONS = [
    {
        "name": "Station Alpha",
        "freq": "88.1",
        "genre": "Tech Beats",
        "locked": False,
        "color": (0.25, 0.84, 1.0),
        "desc": "Ambient coding music to keep you in flow.",
    },
    {
        "name": "Station Beta",
        "freq": "92.5",
        "genre": "Code Radio",
        "locked": False,
        "color": (0.1, 1.0, 0.6),
        "desc": "Lo-fi beats streamed live over Loeb Protocol.",
    },
    {
        "name": "Station Gamma",
        "freq": "96.3",
        "genre": "Vision FM",
        "locked": True,
        "color": (1.0, 0.78, 0.2),
        "desc": "Solve the puzzle below to unlock this channel.",
        "puzzle_index": 0,
    },
    {
        "name": "Station Delta",
        "freq": "101.7",
        "genre": "Systems HZ",
        "locked": True,
        "color": (0.8, 0.3, 1.0),
        "desc": "Solve the puzzle below to unlock this channel.",
        "puzzle_index": 1,
    },
]

CODE_PUZZLES = [
    {
        "title": "🔒  Debug the Function",
        "description": (
            "This function should double a number,\n"
            "but it has a bug. What replaces '?' ?"
        ),
        "code": "def double(x):\n    return x ? 2",
        "options": ["+ 2", "* 2", "- 2", "/ 2"],
        "answer": 1,          # index of correct option
        "hint": "Doubling a number means multiplying it by 2",
        "unlocks": 2,         # index into RADIO_STATIONS
    },
    {
        "title": "🔒  Complete the Loop",
        "description": (
            "Fill in the blank so that\n"
            "numbers 0 through 4 are printed."
        ),
        "code": "for i in range(?):\n    print(i)",
        "options": ["3", "4", "5", "6"],
        "answer": 2,
        "hint": "range(5) generates: 0, 1, 2, 3, 4",
        "unlocks": 3,
    },
]

CODE_RAIN_WORDS = [
    "build()", "launch()", "pcvr_core()", "radio_v8()",
    "code_raiders()", "atlas.infinity()", "grow()", "deploy()",
    "vision = real", "stream()", "connect()", "scale()",
]

BUTTON_W = 240
BUTTON_H = 56

# ui.TextField overlay dimensions (ui coords: top-left origin)
NAME_FIELD_W = 300
NAME_FIELD_H = 50


# ---------------------------------------------------------------------------
# Main Scene
# ---------------------------------------------------------------------------

class PCVREdTech(Scene):

    # ------------------------------------------------------------------ setup

    def setup(self):
        self.state = STATE_NAME
        self.timer = 0.0
        self.tap_flash = 0.0
        self.message_scale = 1.0

        # Username (collected in NAME_ENTRY)
        self.username = ""
        self._name_field = None       # ui.TextField overlay
        self._setup_name_field()

        # Starfield
        self.stars = [
            {
                "x": random.uniform(-3, 3),
                "y": random.uniform(-2, 2),
                "z": random.random(),
            }
            for _ in range(120)
        ]

        # Falling code-rain lines
        self.code_lines = [
            {
                "x": random.uniform(0, self.size.w),
                "y": random.uniform(0, self.size.h),
                "speed": random.uniform(1.2, 4.0),
                "text": random.choice(CODE_RAIN_WORDS),
            }
            for _ in range(20)
        ]

        # Particle system
        self.particles = []

        # Showcase state
        self.showcase_index = 0    # which theme is visible

        # Radio state (mutable copy so we can unlock stations)
        import copy
        self.stations = copy.deepcopy(RADIO_STATIONS)
        self.active_station = 0
        self.radio_wave = 0.0

        # Code-Raiders state
        self.current_puzzle_idx = 0   # index into CODE_PUZZLES
        self.selected_option = -1
        self.puzzle_result = None     # True / False / None
        self.puzzle_result_timer = 0.0

    def _setup_name_field(self):
        """Overlay a ui.TextField so the user can type their name."""
        w = self.size.w
        h = self.size.h

        field = ui.TextField()
        field.placeholder = "Type your name and press ↩"
        field.text_color = "white"
        field.background_color = (0.1, 0.15, 0.25, 0.9)
        field.font = ("<system-bold>", 20)
        field.alignment = ui.ALIGN_CENTER
        field.bordered = False
        # ui coords: top-left origin, so vertical centre = h/2 - NAME_FIELD_H/2
        field.frame = (
            w / 2 - NAME_FIELD_W / 2,
            h / 2 - NAME_FIELD_H / 2,
            NAME_FIELD_W,
            NAME_FIELD_H,
        )
        field.action = self._name_submitted

        self.view.add_subview(field)
        field.begin_editing()
        self._name_field = field

    def _name_submitted(self, sender):
        """Called when the user presses Return in the name field."""
        name = (sender.text or "").strip()
        if not name:
            return
        self.username = name
        sender.end_editing()
        self.view.remove_subview(sender)
        self._name_field = None
        # Burst of particles at the centre
        cx, cy = self.size.w / 2, self.size.h / 2
        self.spawn_particles(cx, cy, count=50)
        self._play_sound("digital:PowerUp7")
        self.state = STATE_INTRO

    # --------------------------------------------------------------- particles

    def spawn_particles(self, x, y, count=20):
        for _ in range(count):
            self.particles.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-7, 7),
                "vy": random.uniform(-7, 7),
                "life": 1.0,
                "size": random.uniform(4, 12),
                "color": (
                    random.uniform(0.2, 1.0),
                    random.uniform(0.5, 1.0),
                    random.uniform(0.7, 1.0),
                ),
            })

    # ------------------------------------------------------------------ update

    def update(self):
        self.timer += self.dt

        # Starfield
        for s in self.stars:
            s["z"] -= 0.008
            if s["z"] <= 0:
                s["z"] = 1.0
                s["x"] = random.uniform(-3, 3)
                s["y"] = random.uniform(-2, 2)

        # Code rain
        for cl in self.code_lines:
            cl["y"] -= cl["speed"]
            if cl["y"] < -20:
                cl["y"] = self.size.h + 20
                cl["x"] = random.uniform(0, self.size.w)
                cl["text"] = random.choice(CODE_RAIN_WORDS)

        # Particles
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.025
            p["size"] *= 0.97
            if p["life"] <= 0:
                self.particles.remove(p)

        # Tap-flash fade
        if self.tap_flash > 0:
            self.tap_flash *= 0.85

        # Pulsing scale
        if self.state in (STATE_SHOWCASE, STATE_RADIO):
            self.message_scale = 1.0 + abs(math.sin(self.timer * 3)) * 0.05
        else:
            self.message_scale = 1.0

        # Radio wave
        self.radio_wave = math.sin(self.timer * 4) * 0.5 + 0.5

        # Auto-dismiss puzzle result feedback
        if self.puzzle_result_timer > 0:
            self.puzzle_result_timer -= self.dt
            if self.puzzle_result_timer <= 0:
                # Only clear negative results; positive ones show "unlocked"
                if not self.puzzle_result:
                    self.puzzle_result = None
                    self.selected_option = -1

    # ================================================================== DRAWING

    def draw(self):
        self._draw_background()
        self._draw_particles()

        if self.state == STATE_NAME:
            self._draw_name_entry()
        elif self.state == STATE_INTRO:
            self._draw_intro()
        elif self.state == STATE_SHOWCASE:
            self._draw_showcase()
        elif self.state == STATE_START:
            self._draw_start()
        elif self.state == STATE_RADIO:
            self._draw_radio()
        elif self.state == STATE_CODE_RAIDERS:
            self._draw_code_raiders()

    # ----------------------------------------- shared background & particles

    def _draw_background(self):
        background(0.03, 0.05, 0.09)
        cx, cy = self.size.w / 2, self.size.h / 2

        # Starfield warp lines
        stroke(1, 1, 1, 0.5)
        for s in self.stars:
            z = s["z"]
            if z <= 0:
                continue
            px = cx + s["x"] * (cx / z)
            py = cy + s["y"] * (cy / z)
            stroke_weight(max(0.5, 2.0 / z))
            line(px, py, px, py + 8.0 / z)

        # Falling code rain
        tint(0.2, 1, 0.6, 0.18)
        for cl in self.code_lines:
            text(
                cl["text"],
                font_name="Menlo",
                font_size=10,
                x=cl["x"],
                y=cl["y"],
                alignment=5,
            )

        # Tap-flash overlay
        if self.tap_flash > 0:
            fill(1, 1, 1, self.tap_flash * 0.2)
            rect(0, 0, self.size.w, self.size.h)

    def _draw_particles(self):
        no_stroke()
        for p in self.particles:
            r, g, b = p["color"]
            fill(r, g, b, p["life"])
            ellipse(p["x"], p["y"], p["size"], p["size"])

    # ----------------------------------------- reusable button

    def _draw_button(self, label, bx=None, by=None, bw=BUTTON_W, bh=BUTTON_H):
        if bx is None:
            bx = self.size.w / 2
        if by is None:
            by = self.size.h * 0.20

        # Glow shadow
        no_stroke()
        fill(0.48, 0.24, 0.95, 0.18)
        rect(bx - bw / 2 - 6, by - bh / 2 - 6, bw + 12, bh + 12)

        fill(0.48, 0.24, 0.95, 0.95)
        stroke(1, 1, 1, 0.25)
        stroke_weight(2)
        rect(bx - bw / 2, by - bh / 2, bw, bh)

        tint(1, 1, 1, 1)
        text(
            label,
            font_name="AvenirNext-Bold",
            font_size=20,
            x=bx,
            y=by,
            alignment=5,
        )

    def _button_hit(self, touch, bx=None, by=None, bw=BUTTON_W, bh=BUTTON_H):
        if bx is None:
            bx = self.size.w / 2
        if by is None:
            by = self.size.h * 0.20
        return touch.location in Rect(bx - bw / 2, by - bh / 2, bw, bh)

    # ----------------------------------------- Scene 1 – Name Entry

    def _draw_name_entry(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        pulse = abs(math.sin(self.timer * 2))

        tint(0.25, 0.84, 1, 1)
        text(
            "WELCOME TO PCVR 👋",
            font_name="AvenirNext-Bold",
            font_size=26,
            x=cx,
            y=cy + 150,
            alignment=5,
        )

        tint(1, 1, 1, 0.9)
        text(
            "What should we call you?",
            font_name="AvenirNext",
            font_size=20,
            x=cx,
            y=cy + 95,
            alignment=5,
        )

        # Decorative border around the text field
        no_fill()
        stroke(0.48, 0.24, 0.95, 0.7)
        stroke_weight(2)
        rect(cx - 158, cy - 34, 316, 58)

        tint(0.85, 0.9, 1, 0.55)
        text(
            "type your name above, then press ↩",
            font_name="AvenirNext",
            font_size=13,
            x=cx,
            y=cy - 60,
            alignment=5,
        )

        # Animated sparkle hint
        tint(0.1, 1, 0.6, 0.5 + pulse * 0.5)
        text(
            "✦   ✦   ✦",
            font_name="AvenirNext",
            font_size=18,
            x=cx,
            y=cy - 110,
            alignment=5,
        )

    # ----------------------------------------- Scene 2 – Educational Intro

    def _draw_intro(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        pulse = abs(math.sin(self.timer * 1.5))

        tint(1, 1, 1, 1)
        text(
            "WHAT IS PCVR? 🌐",
            font_name="AvenirNext-Bold",
            font_size=30,
            x=cx,
            y=cy + 170,
            alignment=5,
        )

        tint(0.25, 0.84, 1, 1)
        text(
            "Personal Computing · Virtual Reality",
            font_name="AvenirNext",
            font_size=17,
            x=cx,
            y=cy + 125,
            alignment=5,
        )

        # Explanation panel
        no_fill()
        stroke(0.25, 0.84, 1, 0.2)
        stroke_weight(1)
        rect(cx - 165, cy + 15, 330, 90)

        tint(0.85, 0.9, 1, 0.85)
        for i, line_str in enumerate(
            [
                "A platform for building apps, tools,",
                "radio, and educational systems —",
                "all from your device.  📱",
            ]
        ):
            text(
                line_str,
                font_name="AvenirNext",
                font_size=15,
                x=cx,
                y=cy + 82 - i * 22,
                alignment=5,
            )

        tint(1, 0.78, 0.2, 0.65 + pulse * 0.35)
        text(
            "built fast  •  built real  •  built with vision",
            font_name="AvenirNext",
            font_size=15,
            x=cx,
            y=cy - 20,
            alignment=5,
        )

        self._draw_button("EXPLORE PCVR →")

    # ----------------------------------------- Scene 3 – Showcase Themes

    def _draw_showcase(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        theme = SHOWCASE_THEMES[self.showcase_index]
        r, g, b = theme["color"]

        # Big animated title
        tint(r, g, b, 1)
        text(
            theme["title"],
            font_name="AvenirNext-Bold",
            font_size=int(44 * self.message_scale),
            x=cx,
            y=cy + 150,
            alignment=5,
        )

        tint(0.85, 0.9, 1, 0.9)
        text(
            theme["subtitle"],
            font_name="AvenirNext-Bold",
            font_size=18,
            x=cx,
            y=cy + 95,
            alignment=5,
        )

        # Detail box
        no_fill()
        stroke(r, g, b, 0.25)
        stroke_weight(1)
        rect(cx - 155, cy + 20, 310, 62)

        tint(0.85, 0.9, 1, 0.8)
        for i, dl in enumerate(theme["detail"].split("\n")):
            text(
                dl,
                font_name="AvenirNext",
                font_size=16,
                x=cx,
                y=cy + 65 - i * 24,
                alignment=5,
            )

        tint(1, 0.55, 0.15, 1)
        text(
            "this took seconds to build  ⚡",
            font_name="AvenirNext-Bold",
            font_size=18,
            x=cx,
            y=cy - 25,
            alignment=5,
        )

        # Progress dots
        dot_y = cy - 60
        total = len(SHOWCASE_THEMES)
        for i in range(total):
            dot_x = cx + (i - total / 2 + 0.5) * 20
            if i == self.showcase_index:
                fill(r, g, b, 1)
            else:
                fill(0.4, 0.4, 0.5, 0.5)
            no_stroke()
            ellipse(dot_x - 5, dot_y - 5, 10, 10)

        is_last = self.showcase_index == len(SHOWCASE_THEMES) - 1
        label = "START EXPLORING →" if is_last else "NEXT THEME →"
        self._draw_button(label)

    # ----------------------------------------- Scene 4 – Interactive Start

    def _draw_start(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        pulse = abs(math.sin(self.timer * 2))
        name_display = self.username or "Explorer"

        tint(1, 1, 1, 1)
        text(
            f"Ready, {name_display}? 🚀",
            font_name="AvenirNext-Bold",
            font_size=30,
            x=cx,
            y=cy + 160,
            alignment=5,
        )

        tint(0.25, 0.84, 1, 1)
        text(
            "THAT IS THE VISION",
            font_name="AvenirNext-Bold",
            font_size=24,
            x=cx,
            y=cy + 105,
            alignment=5,
        )

        tint(0.1, 1, 0.6, 1)
        text(
            "systems  •  speed  •  execution",
            font_name="AvenirNext-Bold",
            font_size=19,
            x=cx,
            y=cy + 60,
            alignment=5,
        )

        tint(1, 0.78, 0.2, 1)
        text(
            "PCVR can become something real",
            font_name="AvenirNext",
            font_size=18,
            x=cx,
            y=cy + 15,
            alignment=5,
        )

        tint(0.85, 0.95, 1, 0.65 + pulse * 0.35)
        text(
            "now imagine this scaled into real products 🌐",
            font_name="AvenirNext",
            font_size=15,
            x=cx,
            y=cy - 30,
            alignment=5,
        )

        self._draw_button("LAUNCH RADIO 📻")

    # ----------------------------------------- Scene 5 – Interactive Radio

    def _draw_radio(self):
        cx = self.size.w / 2
        w, h = self.size.w, self.size.h
        name_display = self.username or "Explorer"

        # ---- header ----
        tint(0.25, 0.84, 1, 1)
        text(
            f"🎙  {name_display}'s PCVR Radio",
            font_name="AvenirNext-Bold",
            font_size=21,
            x=cx,
            y=h - 36,
            alignment=5,
        )

        # ---- educational streaming info ----
        tint(0.1, 1, 0.6, 0.7)
        text(
            "Real-time audio  •  44.1 kHz  •  Loeb Streaming Protocol",
            font_name="Menlo",
            font_size=10,
            x=cx,
            y=h - 60,
            alignment=5,
        )

        # ---- wave visualizer ----
        bar_count = 22
        bar_area_w = w * 0.72
        bar_w = bar_area_w / bar_count
        wave_y = h * 0.74

        wave_palette = [
            (0.25, 0.84, 1.0),
            (0.1, 1.0, 0.6),
            (1.0, 0.78, 0.2),
        ]
        for layer, (lr, lg, lb) in enumerate(wave_palette):
            stroke(lr, lg, lb, 0.25 + self.radio_wave * 0.35)
            stroke_weight(2)
            no_fill()
            for j in range(bar_count):
                bh = 12 + math.sin(self.timer * 4.5 + j * 0.55 + layer * 1.2) * 13
                bx = cx - bar_area_w / 2 + j * bar_w
                line(bx, wave_y - bh / 2, bx, wave_y + bh / 2)

        # ---- streaming education tooltip ----
        tint(0.48, 0.84, 1, 0.45)
        text(
            "↑  Audio packets sent 44,100× per second over IP",
            font_name="AvenirNext",
            font_size=11,
            x=cx,
            y=h * 0.67,
            alignment=5,
        )

        # ---- station cards ----
        card_h = 70
        card_gap = 10
        station_top = h * 0.60

        for i, st in enumerate(self.stations):
            sy = station_top - i * (card_h + card_gap)
            sr, sg, sb = st["color"]
            is_active = i == self.active_station

            # Card background
            if st["locked"]:
                fill(0.1, 0.08, 0.05, 0.85)
                stroke(sr, sg, sb, 0.3)
            elif is_active:
                fill(sr * 0.25, sg * 0.25, sb * 0.25, 0.9)
                stroke(sr, sg, sb, 0.95)
            else:
                fill(0.06, 0.10, 0.18, 0.82)
                stroke(sr, sg, sb, 0.35)
            stroke_weight(2)
            rect(cx - 165, sy - card_h / 2, 330, card_h)

            if st["locked"]:
                # Station info
                tint(0.9, 0.55, 0.2, 0.85)
                text(
                    "🔒  " + st["name"],
                    font_name="AvenirNext-Bold",
                    font_size=15,
                    x=cx - 45,
                    y=sy + 12,
                    alignment=5,
                )
                tint(0.75, 0.6, 0.35, 0.75)
                text(
                    st["freq"] + " FM  •  " + st["genre"],
                    font_name="AvenirNext",
                    font_size=12,
                    x=cx - 45,
                    y=sy - 10,
                    alignment=5,
                )
                # Unlock button
                fill(0.85, 0.35, 0.08, 0.92)
                stroke(1.0, 0.6, 0.2, 0.5)
                stroke_weight(1)
                rect(cx + 78, sy - 18, 76, 36)
                tint(1, 1, 1, 1)
                text(
                    "UNLOCK",
                    font_name="AvenirNext-Bold",
                    font_size=13,
                    x=cx + 116,
                    y=sy,
                    alignment=5,
                )
            else:
                # Station info
                tint(sr, sg, sb, 0.9 if is_active else 0.65)
                text(
                    st["name"],
                    font_name="AvenirNext-Bold",
                    font_size=15,
                    x=cx - 40,
                    y=sy + 12,
                    alignment=5,
                )
                tint(0.85, 0.9, 1, 0.75)
                text(
                    st["freq"] + " FM  •  " + st["genre"],
                    font_name="AvenirNext",
                    font_size=12,
                    x=cx - 40,
                    y=sy - 10,
                    alignment=5,
                )
                if is_active:
                    # On-air indicator with pulse
                    tint(0.1, 1, 0.6, 0.75 + self.radio_wave * 0.25)
                    text(
                        "▶  ON AIR",
                        font_name="AvenirNext-Bold",
                        font_size=12,
                        x=cx + 110,
                        y=sy,
                        alignment=5,
                    )

        # Bottom hint
        bottom_y = station_top - len(self.stations) * (card_h + card_gap) - 14
        tint(0.48, 0.84, 1, 0.40)
        text(
            "Tap a station to tune in   •   🔒 Solve a puzzle to unlock",
            font_name="AvenirNext",
            font_size=11,
            x=cx,
            y=bottom_y,
            alignment=5,
        )

    # ----------------------------------------- Scene 6 – Code Raiders

    def _draw_code_raiders(self):
        cx, cy = self.size.w / 2, self.size.h / 2
        puzzle = CODE_PUZZLES[self.current_puzzle_idx]

        # ---- header ----
        tint(1, 0.78, 0.2, 1)
        text(
            "⚔️   CODE RAIDERS",
            font_name="AvenirNext-Bold",
            font_size=26,
            x=cx,
            y=cy + 215,
            alignment=5,
        )

        tint(0.85, 0.9, 1, 0.9)
        text(
            puzzle["title"],
            font_name="AvenirNext-Bold",
            font_size=18,
            x=cx,
            y=cy + 175,
            alignment=5,
        )

        # ---- description panel ----
        fill(0.04, 0.07, 0.14, 0.88)
        stroke(0.48, 0.24, 0.95, 0.4)
        stroke_weight(1)
        rect(cx - 165, cy + 90, 330, 72)

        tint(0.85, 0.9, 1, 0.9)
        for i, dl in enumerate(puzzle["description"].split("\n")):
            text(
                dl,
                font_name="AvenirNext",
                font_size=14,
                x=cx,
                y=cy + 144 - i * 22,
                alignment=5,
            )

        # ---- code panel ----
        fill(0.02, 0.04, 0.09, 0.92)
        stroke(0.2, 1, 0.6, 0.35)
        stroke_weight(1)
        rect(cx - 165, cy + 16, 330, 66)

        tint(0.2, 1, 0.6, 1)
        for i, cl in enumerate(puzzle["code"].split("\n")):
            text(
                cl,
                font_name="Menlo",
                font_size=15,
                x=cx,
                y=cy + 62 - i * 24,
                alignment=5,
            )

        # ---- answer options ----
        option_base_y = cy - 12
        option_spacing = 52

        for i, opt in enumerate(puzzle["options"]):
            oy = option_base_y - i * option_spacing
            is_sel = i == self.selected_option

            if self.puzzle_result is not None and is_sel:
                if self.puzzle_result:
                    fill(0.08, 0.85, 0.28, 0.92)
                    stroke(0.1, 1, 0.4, 0.9)
                else:
                    fill(0.85, 0.15, 0.15, 0.92)
                    stroke(1, 0.3, 0.3, 0.9)
            elif is_sel:
                fill(0.48, 0.24, 0.95, 0.92)
                stroke(1, 1, 1, 0.5)
            else:
                fill(0.07, 0.11, 0.20, 0.82)
                stroke(0.48, 0.84, 1, 0.35)
            stroke_weight(2)
            rect(cx - 130, oy - 20, 260, 42)

            tint(1, 1, 1, 1)
            text(
                f"  {chr(65 + i)}.  {opt}",
                font_name="AvenirNext-Bold",
                font_size=16,
                x=cx,
                y=oy,
                alignment=5,
            )

        # ---- hint ----
        hint_y = option_base_y - len(puzzle["options"]) * option_spacing - 6
        tint(1, 0.78, 0.2, 0.6)
        text(
            f"💡  {puzzle['hint']}",
            font_name="AvenirNext",
            font_size=12,
            x=cx,
            y=hint_y,
            alignment=5,
        )

        # ---- result feedback ----
        if self.puzzle_result is not None:
            if self.puzzle_result:
                tint(0.1, 1, 0.4, 1)
                text(
                    "✅  CORRECT!  Station Unlocked! 🎉",
                    font_name="AvenirNext-Bold",
                    font_size=18,
                    x=cx,
                    y=hint_y - 30,
                    alignment=5,
                )
            else:
                tint(1, 0.3, 0.3, 1)
                text(
                    "❌  Try Again!",
                    font_name="AvenirNext-Bold",
                    font_size=18,
                    x=cx,
                    y=hint_y - 30,
                    alignment=5,
                )

        # ---- back button ----
        back_y = self.size.h * 0.07
        self._draw_button("← BACK TO RADIO", by=back_y, bw=200, bh=44)

    # ================================================================= TOUCH

    def touch_began(self, touch):
        self.tap_flash = 1.0
        cx = self.size.w / 2

        if self.state == STATE_NAME:
            # Touch anywhere outside the text field to re-show keyboard
            if self._name_field:
                self._name_field.begin_editing()

        elif self.state == STATE_INTRO:
            if self._button_hit(touch):
                self._play_sound("digital:PowerUp7")
                self.spawn_particles(cx, self.size.h * 0.20, 30)
                self.state = STATE_SHOWCASE
                self.showcase_index = 0

        elif self.state == STATE_SHOWCASE:
            if self._button_hit(touch):
                self._play_sound("digital:PowerUp7")
                self.spawn_particles(cx, self.size.h * 0.20, 25)
                self.showcase_index += 1
                if self.showcase_index >= len(SHOWCASE_THEMES):
                    self.state = STATE_START

        elif self.state == STATE_START:
            if self._button_hit(touch):
                self._play_sound("digital:PowerUp7")
                self.spawn_particles(cx, self.size.h * 0.20, 35)
                self.state = STATE_RADIO

        elif self.state == STATE_RADIO:
            self._handle_radio_touch(touch)

        elif self.state == STATE_CODE_RAIDERS:
            self._handle_puzzle_touch(touch)

    # ----------------------------------------- radio touch handling

    def _handle_radio_touch(self, touch):
        cx = self.size.w / 2
        h = self.size.h

        card_h = 70
        card_gap = 10
        station_top = h * 0.60

        for i, st in enumerate(self.stations):
            sy = station_top - i * (card_h + card_gap)
            card_rect = Rect(cx - 165, sy - card_h / 2, 330, card_h)

            if touch.location not in card_rect:
                continue

            if st["locked"]:
                # Did the user tap the UNLOCK button specifically?
                unlock_rect = Rect(cx + 78, sy - 18, 76, 36)
                if touch.location in unlock_rect:
                    puzzle_idx = st.get("puzzle_index", 0)
                    self.current_puzzle_idx = puzzle_idx
                    self.selected_option = -1
                    self.puzzle_result = None
                    self._play_sound("digital:ZapThreeToneUp")
                    self.spawn_particles(touch.location.x, touch.location.y, 20)
                    self.state = STATE_CODE_RAIDERS
                else:
                    self._play_sound("digital:Zap1")
                    self.spawn_particles(touch.location.x, touch.location.y, 8)
            else:
                self.active_station = i
                self._play_sound("digital:PowerUp7")
                self.spawn_particles(touch.location.x, touch.location.y, 22)
            break

    # ----------------------------------------- puzzle touch handling

    def _handle_puzzle_touch(self, touch):
        cx, cy = self.size.w / 2, self.size.h / 2
        back_y = self.size.h * 0.07

        # Back to radio
        if self._button_hit(touch, by=back_y, bw=200, bh=44):
            self._play_sound("digital:PowerUp7")
            self.state = STATE_RADIO
            return

        puzzle = CODE_PUZZLES[self.current_puzzle_idx]
        option_base_y = cy - 12
        option_spacing = 52

        for i in range(len(puzzle["options"])):
            oy = option_base_y - i * option_spacing
            option_rect = Rect(cx - 130, oy - 20, 260, 42)

            if touch.location not in option_rect:
                continue

            self.selected_option = i
            correct = i == puzzle["answer"]
            self.puzzle_result = correct
            self.puzzle_result_timer = 2.5

            if correct:
                self._play_sound("digital:PowerUp7")
                self.spawn_particles(cx, cy, 60)
                # Unlock the associated station
                target = puzzle.get("unlocks")
                if target is not None and target < len(self.stations):
                    self.stations[target]["locked"] = False
            else:
                self._play_sound("digital:Zap1")
                self.spawn_particles(touch.location.x, touch.location.y, 12)
            break

    # ----------------------------------------- safe sound helper

    @staticmethod
    def _play_sound(effect):
        try:
            sound.play_effect(effect)
        except (AttributeError, OSError):
            pass


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run(PCVREdTech(), PORTRAIT)
