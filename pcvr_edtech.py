"""
PCVR-EdTech: Interactive PCVR Educational Experience
------------------------------------------------------
A Pythonista (iOS) educational app combining:
  - Animated splash screen with username entry
  - PCVR education overview with pulsating effects
  - 5 themed learning pages with slide-in animations
  - Warp Protocol arcade gameplay demo
  - Button press screen shake, particle bursts, and dynamic sounds

Run in Pythonista 3 on iOS:  run(PCVREdTech(), PORTRAIT)
"""

from scene import *
import sound
import random
import math
import colorsys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FONT_TITLE  = 'AvenirNext-Bold'
FONT_BODY   = 'AvenirNext'
FONT_MONO   = 'Menlo-Bold'
FONT_MONO_R = 'Menlo'

# Scene state names
S_SPLASH     = 'SPLASH'
S_ENTER_NAME = 'ENTER_NAME'
S_PCVR_INTRO = 'PCVR_INTRO'
S_LESSON     = 'LESSON'
S_GAME_INTRO = 'GAME_INTRO'
S_GAME       = 'GAME'
S_GAMEOVER   = 'GAMEOVER'

# Lesson content: (title, subtitle, body lines, theme_hue 0-1)
LESSONS = [
    {
        'title':    'What is PCVR?',
        'subtitle': 'Performance · Cognition · Vision · Reality',
        'lines': [
            'PCVR stands for PC-based Virtual Reality.',
            '',
            'It combines a powerful computer with a',
            'head-mounted display (HMD) to create',
            'fully immersive 3D environments.',
            '',
            '→ Higher fidelity than standalone headsets',
            '→ Supports room-scale tracking',
            '→ Used in education, training & research',
        ],
        'hue': 0.58,   # electric blue
    },
    {
        'title':    'Core Components',
        'subtitle': 'Hardware that powers the experience',
        'lines': [
            '1. PC / GPU  — renders the virtual world',
            '   • NVIDIA RTX / AMD RX series recommended',
            '',
            '2. HMD       — displays 90-120 fps stereo view',
            '   • e.g. Valve Index, Meta Quest (Link)',
            '',
            '3. Controllers — 6DoF tracked input devices',
            '',
            '4. Base Stations — lighthouse positional tracking',
        ],
        'hue': 0.35,   # green
    },
    {
        'title':    'How Rendering Works',
        'subtitle': 'From GPU to your eyes in < 11 ms',
        'lines': [
            'Step 1 — Pose Prediction',
            '  The runtime predicts head position ~20 ms ahead.',
            '',
            'Step 2 — Scene Rendering',
            '  Two viewports (left eye / right eye) rendered',
            '  using a single GPU pass (Instanced Stereo).',
            '',
            'Step 3 — Distortion Correction',
            '  Lens distortion is pre-warped in a post-pass.',
            '',
            'Step 4 — ATW / Reprojection',
            '  Missed frames are time-warped to reduce judder.',
        ],
        'hue': 0.12,   # amber
    },
    {
        'title':    'Writing VR Code',
        'subtitle': 'Your first OpenXR / Unity / Pygame XR loop',
        'lines': [
            'A VR app loop looks like this:',
            '',
            '  while running:',
            '      pose  = xr.get_head_pose()',
            '      input = xr.get_controller_state()',
            '      scene.update(pose, input)',
            '      renderer.submit_frame(scene)',
            '',
            'Key insight: keep frame time < 11 ms',
            'to maintain 90 fps and prevent motion sickness.',
        ],
        'hue': 0.75,   # violet
    },
    {
        'title':    'Optimization Tips',
        'subtitle': 'Keep it smooth — your users will thank you',
        'lines': [
            '✓ Use LOD (Level of Detail) meshes',
            '✓ Bake lighting — avoid real-time shadows',
            '✓ Keep draw calls < 100 per eye',
            '✓ Use occlusion culling',
            '✓ Prefer single-pass instanced rendering',
            '✓ Profile with GPU Trace / RenderDoc',
            '',
            'Next: try the Warp Protocol mini-game',
            'to experience low-latency input in action!',
        ],
        'hue': 0.92,   # rose/pink
    },
]

# Warp Protocol game themes
GAME_THEMES = [
    {'name': 'NEON SECTOR',   'p_color': (0, 1, 1),       'e_color': (1, 0.2, 0.4), 'bg_mult': 0.10, 'hazard': None},
    {'name': 'VOID SECTOR',   'p_color': (1, 1, 1),       'e_color': (0.4, 0.4, 0.4),'bg_mult': 0.03, 'hazard': 'gravity_well'},
    {'name': 'GOLDEN BULL',   'p_color': (1, 0.9, 0),     'e_color': (0, 1, 0.5),   'bg_mult': 0.20, 'hazard': 'slow_field'},
    {'name': 'CRIMSON CORE',  'p_color': (1, 0.2, 0),     'e_color': (0.2, 0.1, 1), 'bg_mult': 0.15, 'hazard': 'unstable'},
]


# ---------------------------------------------------------------------------
# Helper: simple Button descriptor (not a real ui widget, just a hit-box)
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, cx, cy, w, h, label, color=(0.1, 0.6, 1)):
        self.cx    = cx
        self.cy    = cy
        self.w     = w
        self.h     = h
        self.label = label
        self.color = color
        self.pulse = 0.0   # 0..1, animates on press

    def hit(self, tx, ty):
        return abs(tx - self.cx) < self.w / 2 and abs(ty - self.cy) < self.h / 2

    def draw(self, shake_x=0, shake_y=0):
        x = self.cx + shake_x
        y = self.cy + shake_y
        glow = 0.35 + 0.65 * self.pulse
        r, g, b = self.color
        # outer glow
        no_stroke()
        fill(r, g, b, glow * 0.35)
        rect(x - self.w / 2 - 6, y - self.h / 2 - 6, self.w + 12, self.h + 12)
        # button body
        fill(r * 0.3, g * 0.3, b * 0.3, 0.9)
        rect(x - self.w / 2, y - self.h / 2, self.w, self.h)
        # border
        stroke(r, g, b, 0.8 + 0.2 * glow)
        stroke_weight(2)
        no_fill()
        rect(x - self.w / 2, y - self.h / 2, self.w, self.h)
        # label
        no_stroke()
        tint(r, g, b, 0.9 + 0.1 * glow)
        text(self.label, FONT_TITLE, 20, x, y, alignment=5)
        tint(1, 1, 1, 1)


# ---------------------------------------------------------------------------
# Particle system
# ---------------------------------------------------------------------------
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'size', 'r', 'g', 'b')

    def __init__(self, x, y, r, g, b, speed=7, size=8):
        self.x    = x
        self.y    = y
        angle     = random.uniform(0, math.tau)
        spd       = random.uniform(speed * 0.4, speed)
        self.vx   = math.cos(angle) * spd
        self.vy   = math.sin(angle) * spd
        self.life = 1.0
        self.size = random.uniform(size * 0.5, size)
        self.r    = r
        self.g    = g
        self.b    = b

    def update(self):
        self.x    += self.vx
        self.y    += self.vy
        self.vx   *= 0.96
        self.vy   *= 0.96
        self.life -= 0.03
        self.size *= 0.97
        return self.life > 0

    def draw(self, ox=0, oy=0):
        fill(self.r, self.g, self.b, self.life * self.life)
        no_stroke()
        ellipse(self.x + ox - self.size / 2,
                self.y + oy - self.size / 2,
                self.size, self.size)


def spawn_burst(particles, x, y, hue=None, count=30, speed=9, size=10):
    """Spawn a burst of colorful particles at (x, y)."""
    if hue is None:
        hue = random.random()
    for i in range(count):
        h = (hue + random.uniform(-0.1, 0.1)) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 0.9, 1.0)
        particles.append(Particle(x, y, r, g, b, speed=speed, size=size))


# ---------------------------------------------------------------------------
# Starfield
# ---------------------------------------------------------------------------
class Star:
    __slots__ = ('x', 'y', 'z', 'px', 'py')

    def __init__(self, w, h):
        self.reset(w, h, initial=True)

    def reset(self, w, h, initial=False):
        self.x  = random.uniform(-3, 3)
        self.y  = random.uniform(-2, 2)
        self.z  = random.random() if initial else 1.0
        self.px = 0
        self.py = 0

    def update(self, w, h, speed=0.012):
        cx, cy = w / 2, h / 2
        self.z -= speed
        if self.z <= 0:
            self.reset(w, h)
            return False
        self.px = cx + self.x * (cx / self.z)
        self.py = cy + self.y * (cy / self.z)
        return True

    def draw(self, w, h, ox=0, oy=0, brightness=0.6):
        sz = max(1.0, 2.5 / self.z)
        fill(1, 1, 1, brightness * (1 - self.z))
        no_stroke()
        ellipse(self.px + ox - sz / 2,
                self.py + oy - sz / 2,
                sz, sz)


# ---------------------------------------------------------------------------
# Transition overlay
# ---------------------------------------------------------------------------
class Transition:
    def __init__(self):
        self.alpha   = 0.0
        self.fading  = False   # True = alpha decreasing (black → clear)
        self.fade_in = False   # True = alpha increasing (clear → black)
        self.done    = False
        self._cb     = None

    def start_out(self, callback=None):
        """Fade screen to black, then call callback, then fade back."""
        self.alpha   = 0.0
        self.fade_in = True
        self.fading  = False
        self.done    = False
        self._cb     = callback

    def update(self):
        if self.fade_in:
            self.alpha = min(1.0, self.alpha + 0.06)
            if self.alpha >= 1.0:
                self.fade_in = False
                self.fading  = True
                if self._cb:
                    self._cb()
                    self._cb = None
        elif self.fading:
            self.alpha = max(0.0, self.alpha - 0.05)
            if self.alpha <= 0.0:
                self.fading = False
                self.done   = True

    @property
    def active(self):
        return self.fade_in or self.fading

    def draw(self):
        if self.alpha > 0:
            fill(0, 0, 0, self.alpha)
            no_stroke()
            # drawn over everything — caller must supply screen size


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------
class PCVREdTech(Scene):

    # ------------------------------------------------------------------ setup
    def setup(self):
        w, h          = self.size.w, self.size.h
        self.state    = S_SPLASH
        self.timer    = 0.0

        # User name (Pythonista UI text input is done via console_input helper)
        self.user_name = 'Coder'

        # Particles, stars, transition
        self.particles  = []
        self.stars      = [Star(w, h) for _ in range(80)]
        self.transition = Transition()

        # Screen shake
        self.shake      = 0.0
        self.shake_x    = 0.0
        self.shake_y    = 0.0

        # Flash overlay (white flash on button press)
        self.flash      = 0.0

        # Slide-in animation: 0 = slid in from right, 1 = fully on screen
        self.slide_t    = 0.0

        # Lesson index
        self.lesson_idx = 0

        # Buttons — recreated per scene in _make_buttons()
        self.buttons    = []

        # PCVR intro pulsing
        self.pulse_t    = 0.0

        # Warp Protocol game state
        self._game_reset()

        # Build initial button set
        self._make_buttons()

    # --------------------------------------------------------------- buttons
    def _make_buttons(self):
        w, h = self.size.w, self.size.h
        cx   = w / 2
        self.buttons = []

        if self.state == S_SPLASH:
            self.buttons.append(
                Button(cx, h * 0.22, 240, 54, 'TAP TO BEGIN →', color=(0.1, 0.8, 1))
            )

        elif self.state == S_ENTER_NAME:
            self.buttons.append(
                Button(cx, h * 0.25, 240, 54, "I'M READY →", color=(0.2, 1, 0.5))
            )

        elif self.state == S_PCVR_INTRO:
            self.buttons.append(
                Button(cx, h * 0.12, 260, 54, 'START LEARNING →', color=(0.1, 0.8, 1))
            )

        elif self.state == S_LESSON:
            lesson = LESSONS[self.lesson_idx]
            hue    = lesson['hue']
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            label = 'NEXT LESSON →' if self.lesson_idx < len(LESSONS) - 1 else 'PLAY WARP PROTOCOL →'
            self.buttons.append(
                Button(cx, h * 0.10, 280, 54, label, color=(r, g, b))
            )
            # Back button (only from lesson 1+)
            if self.lesson_idx > 0:
                self.buttons.append(
                    Button(cx - 130, h * 0.10, 100, 44, '← BACK', color=(0.6, 0.6, 0.6))
                )

        elif self.state == S_GAME_INTRO:
            self.buttons.append(
                Button(cx, h * 0.22, 240, 54, 'LAUNCH MISSION →', color=(1, 0.6, 0))
            )
            self.buttons.append(
                Button(cx, h * 0.12, 220, 44, '← BACK TO LESSONS', color=(0.5, 0.5, 0.5))
            )

        # S_GAME and S_GAMEOVER buttons drawn inline in draw_game / draw_gameover

    # -------------------------------------------------------------- game init
    def _game_reset(self):
        w, h = self.size.w, self.size.h
        self.g_player_y   = h / 2
        self.g_dy         = 0.0
        self.g_score      = 0
        self.g_health     = 3
        self.g_speed      = 7.0
        self.g_enemies    = []
        self.g_bullets    = []
        self.g_shards     = []
        self.g_trails     = []
        self.g_shield     = 0
        self.g_bull_mode  = 0
        self.g_frenzy     = 0
        self.g_warp_alpha = 0.0
        self.g_glitch     = 0
        self.g_theme_idx  = 0
        self.g_high_score = getattr(self, 'g_high_score', 0)
        self.g_stars      = [{'x': random.random() * w,
                               'y': random.random() * h,
                               's': random.uniform(2, 6)}
                             for _ in range(60)]

    # ------------------------------------------------------------------update
    def update(self):
        dt = self.dt
        self.timer += dt
        w, h = self.size.w, self.size.h

        # Stars
        for s in self.stars:
            speed = 0.008 if self.state == S_GAME else 0.014
            s.update(w, h, speed=speed)

        # Particles
        self.particles = [p for p in self.particles if p.update()]

        # Shake decay
        if self.shake > 0:
            self.shake *= 0.85
            self.shake_x = random.uniform(-self.shake, self.shake)
            self.shake_y = random.uniform(-self.shake, self.shake)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Flash decay
        if self.flash > 0:
            self.flash = max(0.0, self.flash - 0.07)

        # Transition
        self.transition.update()

        # Button pulse animation
        for btn in self.buttons:
            btn.pulse = 0.5 + 0.5 * math.sin(self.timer * 3.5)

        # Slide-in (0 → 1 over ~0.5 s)
        if self.slide_t < 1.0:
            self.slide_t = min(1.0, self.slide_t + dt * 2.2)

        # PCVR intro pulse
        if self.state == S_PCVR_INTRO:
            self.pulse_t += dt

        # Game update
        if self.state == S_GAME:
            self._game_update(w, h)

    # ------------------------------------------------------------------- draw
    def draw(self):
        w, h = self.size.w, self.size.h
        sx, sy = self.shake_x, self.shake_y

        # ---- background colour per state
        self._draw_background(w, h)

        # ---- starfield
        for s in self.stars:
            s.draw(w, h, ox=sx, oy=sy)

        # ---- particles
        for p in self.particles:
            p.draw(ox=sx, oy=sy)

        # ---- scene content
        if self.state == S_SPLASH:
            self._draw_splash(w, h, sx, sy)
        elif self.state == S_ENTER_NAME:
            self._draw_enter_name(w, h, sx, sy)
        elif self.state == S_PCVR_INTRO:
            self._draw_pcvr_intro(w, h, sx, sy)
        elif self.state == S_LESSON:
            self._draw_lesson(w, h, sx, sy)
        elif self.state == S_GAME_INTRO:
            self._draw_game_intro(w, h, sx, sy)
        elif self.state == S_GAME:
            self._draw_game(w, h, sx, sy)
        elif self.state == S_GAMEOVER:
            self._draw_gameover(w, h, sx, sy)

        # ---- buttons (not in game states — drawn inline)
        if self.state not in (S_GAME, S_GAMEOVER):
            for btn in self.buttons:
                btn.draw(shake_x=sx, shake_y=sy)

        # ---- white flash overlay
        if self.flash > 0:
            fill(1, 1, 1, self.flash * 0.55)
            no_stroke()
            rect(0, 0, w, h)

        # ---- transition overlay
        if self.transition.alpha > 0:
            fill(0, 0, 0, self.transition.alpha)
            no_stroke()
            rect(0, 0, w, h)

    # ---------------------------------------------------------- backgrounds
    def _draw_background(self, w, h):
        if self.state == S_SPLASH:
            background(0.02, 0.04, 0.12)

        elif self.state == S_ENTER_NAME:
            background(0.03, 0.06, 0.10)

        elif self.state == S_PCVR_INTRO:
            # Slowly shifting hue
            hv = 0.55 + 0.05 * math.sin(self.timer * 0.3)
            rb, gb, bb = colorsys.hsv_to_rgb(hv, 0.9, 0.07)
            background(rb, gb, bb)

        elif self.state == S_LESSON:
            hue   = LESSONS[self.lesson_idx]['hue']
            hv    = hue + 0.01 * math.sin(self.timer * 0.5)
            rb, gb, bb = colorsys.hsv_to_rgb(hv % 1.0, 0.85, 0.06)
            background(rb, gb, bb)

        elif self.state in (S_GAME_INTRO, S_GAMEOVER):
            background(0.05, 0.02, 0.12)

        elif self.state == S_GAME:
            theme = GAME_THEMES[self.g_theme_idx]
            rb, gb, bb = colorsys.hsv_to_rgb(
                (self.g_score * 0.00002) % 1.0, 0.7, theme['bg_mult'])
            background(rb, gb, bb)

        else:
            background(0, 0, 0)

    # ----------------------------------------------------------- splash scene
    def _draw_splash(self, w, h, sx, sy):
        cx, cy = w / 2 + sx, h / 2 + sy
        # Title — pulsing scale
        scale = 1.0 + 0.04 * math.sin(self.timer * 2.5)
        tint(0.1, 0.85, 1.0, 1)
        text('PCVR', FONT_TITLE,
             int(72 * scale), cx, cy + h * 0.22, alignment=5)
        tint(1, 1, 1, 0.9)
        text('EdTech', FONT_TITLE,
             int(42 * scale), cx, cy + h * 0.13, alignment=5)
        tint(0.6, 0.8, 1, 0.7)
        text('An Immersive Learning Experience', FONT_BODY,
             16, cx, cy + h * 0.06, alignment=5)
        # Decorative separator
        stroke(0.1, 0.8, 1, 0.4)
        stroke_weight(1)
        line(cx - 100, cy + h * 0.03, cx + 100, cy + h * 0.03)
        no_stroke()
        tint(1, 1, 1, 1)

    # -------------------------------------------------------- enter-name scene
    def _draw_enter_name(self, w, h, sx, sy):
        cx, cy = w / 2 + sx, h / 2 + sy
        # Slide offset
        slide_off = (1.0 - self._ease(self.slide_t)) * w
        x = cx + slide_off

        tint(0.2, 1, 0.6, 1)
        text('Hello, future VR Dev!', FONT_TITLE, 28, x, cy + h * 0.22, alignment=5)
        tint(1, 1, 1, 0.85)
        text('Your codename for this mission:', FONT_BODY, 18, x, cy + h * 0.14, alignment=5)
        # Name display box
        stroke(0.2, 1, 0.6, 0.7)
        stroke_weight(2)
        no_fill()
        rect(x - 130, cy + h * 0.06 - 22, 260, 44)
        no_stroke()
        tint(1, 1, 0.3, 1)
        text(self.user_name, FONT_MONO, 26, x, cy + h * 0.06, alignment=5)
        tint(0.7, 0.7, 0.7, 0.6)
        text('(tap the button to continue)', FONT_BODY, 14, x, cy - h * 0.01, alignment=5)
        tint(1, 1, 1, 1)

    # -------------------------------------------------------- PCVR intro scene
    def _draw_pcvr_intro(self, w, h, sx, sy):
        cx  = w / 2 + sx
        slide_off = (1.0 - self._ease(self.slide_t)) * w

        # Pulsating glow ring
        glow = 0.4 + 0.35 * math.sin(self.pulse_t * 2.8)
        no_fill()
        stroke(0.1, 0.7, 1, glow * 0.6)
        stroke_weight(3 + glow * 4)
        ellipse(cx - 90, h * 0.73 - 90, 180, 180)
        no_stroke()

        x = cx + slide_off
        tint(1, 1, 1, 1)
        text('Welcome,', FONT_BODY, 22, x, h * 0.88, alignment=5)
        scale = 1.0 + 0.04 * math.sin(self.pulse_t * 3)
        tint(0.1, 0.9, 1, 1)
        text(self.user_name + '!', FONT_TITLE, int(36 * scale), x, h * 0.81, alignment=5)

        tint(1, 1, 1, 0.9)
        text('PCVR = PC-based Virtual Reality', FONT_TITLE, 24, x, h * 0.72, alignment=5)

        bullets = [
            ('⚡', 'High-performance GPU rendering'),
            ('👁', 'Stereo head-mounted display'),
            ('🎮', '6DoF tracked controllers'),
            ('🌐', 'Room-scale positional tracking'),
        ]
        for i, (icon, desc) in enumerate(bullets):
            alpha = min(1.0, self.slide_t * 2 - i * 0.3)
            if alpha <= 0:
                continue
            tint(0.4, 0.9, 1, alpha)
            text(icon + '  ' + desc, FONT_BODY, 17,
                 x, h * 0.61 - i * 38, alignment=5)
        tint(1, 1, 1, 1)

    # -------------------------------------------------------------- lesson
    def _draw_lesson(self, w, h, sx, sy):
        lesson    = LESSONS[self.lesson_idx]
        hue       = lesson['hue']
        r, g, b   = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        slide_off = (1.0 - self._ease(self.slide_t)) * w
        cx        = w / 2 + sx

        # Header bar
        fill(r * 0.15, g * 0.15, b * 0.15, 0.85)
        no_stroke()
        rect(0, h - 90, w, 90)

        # Lesson counter
        tint(r, g, b, 0.7)
        text(f'Lesson {self.lesson_idx + 1} of {len(LESSONS)}',
             FONT_MONO_R, 13, cx + sx, h - 18, alignment=5)

        # Title (slide from right)
        x = cx + slide_off
        tint(r, g, b, 1)
        text(lesson['title'], FONT_TITLE, 28, x, h - 52, alignment=5)
        tint(1, 1, 1, 0.7)
        text(lesson['subtitle'], FONT_BODY, 15, x, h - 74, alignment=5)

        # Body lines — staggered fade-in
        for i, line_text in enumerate(lesson['lines']):
            delay = i * 0.12
            alpha = max(0.0, min(1.0, (self.slide_t - delay) * 4))
            if alpha <= 0:
                continue
            is_code = line_text.startswith(' ') or line_text.startswith('  ')
            if is_code:
                tint(0.4, 1, 0.6, alpha)
                text(line_text.strip(), FONT_MONO_R, 14,
                     x - 20, h * 0.78 - i * 30, alignment=5)
            else:
                tint(1, 1, 1, alpha)
                text(line_text, FONT_BODY, 16, x, h * 0.78 - i * 30, alignment=5)
        tint(1, 1, 1, 1)

    # ---------------------------------------------------------- game intro
    def _draw_game_intro(self, w, h, sx, sy):
        cx = w / 2 + sx
        slide_off = (1.0 - self._ease(self.slide_t)) * w
        x  = cx + slide_off

        scale = 1.0 + 0.05 * math.sin(self.timer * 2.2)
        tint(1, 0.7, 0.1, 1)
        text('WARP PROTOCOL', FONT_MONO, int(40 * scale), x, h * 0.78, alignment=5)
        tint(1, 1, 1, 0.8)
        text('The Arcade Demo', FONT_BODY, 20, x, h * 0.70, alignment=5)

        lines = [
            'Tap to JUMP and SHOOT',
            'Dodge enemy squares',
            'Collect power-ups:',
            '  BLUE = Shield  |  PINK = Health',
            '  GREEN = Bull Mode (triple shot)',
            '  YELLOW = +2000 pts',
            'Sector changes every 1000 pts',
        ]
        for i, ln in enumerate(lines):
            alpha = min(1.0, max(0.0, self.slide_t * 2.5 - i * 0.25))
            if alpha <= 0:
                continue
            tint(0.8, 0.9, 1, alpha)
            text(ln, FONT_MONO_R, 14, x, h * 0.56 - i * 28, alignment=5)

        tint(1, 1, 1, 1)
        if self.g_high_score > 0:
            tint(1, 0.85, 0.1, 0.9)
            text(f'BEST SYNC: {self.g_high_score}', FONT_MONO_R, 16,
                 x, h * 0.36, alignment=5)
        tint(1, 1, 1, 1)

    # ---------------------------------------------------------- game draw
    def _draw_game(self, w, h, sx, sy):
        theme = GAME_THEMES[self.g_theme_idx]
        gsx   = sx + (self.g_glitch * random.uniform(-3, 3) if self.g_glitch > 0 else 0)
        gsy   = sy + (self.g_glitch * random.uniform(-3, 3) if self.g_glitch > 0 else 0)

        # Game stars
        for gs in self.g_stars:
            gs['x'] = (gs['x'] - gs['s']) % w
            fill(1, 1, 1, 0.35)
            no_stroke()
            rect(gs['x'] + gsx, gs['y'] + gsy, 2, 2)

        # Trails
        pc = theme['p_color']
        for t in self.g_trails:
            fill(pc[0], pc[1], pc[2], t['a'] * 0.25)
            no_stroke()
            rect(100 + gsx, t['y'] - 15 + gsy, 30, 30)

        # Enemies
        ec = theme['e_color']
        for e in self.g_enemies:
            if e['type'] == 'bomber':
                fill(1, 1, 1)
                rect(e['x'] - 20 + gsx, e['y'] - 20 + gsy, 40, 40)
                stroke(1, 0, 0)
                stroke_weight(2)
                no_fill()
                rect(e['x'] - 23 + gsx, e['y'] - 23 + gsy, 46, 46)
                no_stroke()
            else:
                fill(*ec)
                rect(e['x'] - 20 + gsx, e['y'] - 20 + gsy, 40, 40)

        # Shards
        for s in self.g_shards:
            if   s['type'] == 'shield': fill(0, 0.6, 1)
            elif s['type'] == 'bull':   fill(0, 1, 0.4)
            elif s['type'] == 'health': fill(1, 0.3, 1)
            else:                       fill(1, 0.8, 0)
            no_stroke()
            rect(s['x'] + gsx, s['y'] + gsy, 24, 24)

        # Bullets
        bfill = (1, 1, 0) if self.g_bull_mode > 0 else (1, 1, 1)
        fill(*bfill)
        no_stroke()
        for b in self.g_bullets:
            rect(b['x'] + gsx, b['y'] + gsy, 30, 4)

        # Shield ring
        if self.g_shield > 0:
            stroke(0, 1, 1)
            stroke_weight(3)
            no_fill()
            ellipse(75 + gsx, self.g_player_y - 30 + gsy, 60, 60)
            no_stroke()

        # Player
        fill(*pc)
        no_stroke()
        rect(100 + gsx, self.g_player_y - 15 + gsy, 35, 35)

        # Warp flash
        if self.g_warp_alpha > 0:
            fill(1, 1, 1, self.g_warp_alpha)
            no_stroke()
            rect(0, 0, w, h)

        # Game particles
        for p in self.particles:
            p.draw(ox=gsx, oy=gsy)

        # HUD
        self._draw_game_hud(w, h, theme, gsx, gsy)

    def _draw_game_hud(self, w, h, theme, gsx, gsy):
        # Health bar
        fill(0.2, 0.2, 0.2, 0.55)
        no_stroke()
        rect(20 + gsx, h - 44 + gsy, 150, 16)
        hc = (0, 1, 0) if self.g_health > 1 else (1, 0, 0)
        fill(*hc)
        rect(20 + gsx, h - 44 + gsy, (self.g_health / 3) * 150, 16)

        tint(1, 1, 1, 1)
        text(str(self.g_score), FONT_MONO, 48,
             w / 2 + gsx, h - 80 + gsy, alignment=5)
        hazard = theme['hazard'] if theme['hazard'] else 'STABLE'
        text(f"{theme['name']} — {hazard}", FONT_MONO_R, 13,
             w / 2 + gsx, h - 115 + gsy, alignment=5)

        if self.g_frenzy > 0:
            tint(1, 0.8, 0, 1)
            text('!!! MARKET FRENZY !!!', FONT_MONO, 22,
                 w / 2 + gsx, h / 2 + gsy, alignment=5)
        tint(1, 1, 1, 1)

    # -------------------------------------------------------- game over draw
    def _draw_gameover(self, w, h, sx, sy):
        cx, cy = w / 2 + sx, h / 2 + sy
        scale  = 1.0 + 0.03 * math.sin(self.timer * 3)
        tint(1, 0.1, 0.1, 1)
        text('MISSION FAILED', FONT_MONO, int(38 * scale),
             cx, cy + 100, alignment=5)
        tint(1, 1, 1, 0.9)
        text(f'FINAL SYNC: {self.g_score}', FONT_MONO_R, 26,
             cx, cy + 50, alignment=5)
        if self.g_score >= self.g_high_score and self.g_score > 0:
            tint(1, 0.9, 0.1, 1)
            text('✦ NEW BEST SYNC! ✦', FONT_MONO, 20,
                 cx, cy + 20, alignment=5)
        tint(0.6, 0.8, 1, 0.8)
        text('TAP   →   RETRY MISSION', FONT_MONO_R, 18,
             cx, cy - 20, alignment=5)
        text('HOLD  →   RETURN TO LESSONS', FONT_MONO_R, 18,
             cx, cy - 50, alignment=5)
        tint(1, 1, 1, 1)

    # --------------------------------------------------------- game logic
    def _game_update(self, w, h):
        # Theme switching
        target = (self.g_score // 1000) % len(GAME_THEMES)
        if target != self.g_theme_idx:
            self.g_theme_idx = target
            self.g_warp_alpha = 1.0
            self.shake = 25
            spawn_burst(self.particles, w / 2, h / 2, count=40, speed=12)
            sound.play_effect('arcade:Powerup_3')

        if self.g_score > 0 and self.g_score % 10000 < 25:
            self.g_frenzy = 300
            sound.play_effect('digital:PowerUp6')

        if self.g_warp_alpha > 0: self.g_warp_alpha -= 0.05
        if self.g_bull_mode > 0:  self.g_bull_mode  -= 1
        if self.g_frenzy    > 0:  self.g_frenzy     -= 1
        if self.g_glitch    > 0:  self.g_glitch      -= 1

        theme = GAME_THEMES[self.g_theme_idx]

        if theme['hazard'] == 'gravity_well':
            centre = h / 2
            self.g_dy += 0.4 if self.g_player_y < centre else -0.4

        is_inverted = (self.g_score // 7000) % 2 == 1
        self.g_dy += 0.85 if is_inverted else -0.85
        self.g_player_y += self.g_dy

        # Trails
        self.g_trails.append({'y': self.g_player_y, 'a': 1.0})
        for t in self.g_trails[:]:
            t['a'] -= 0.08
            if t['a'] <= 0:
                self.g_trails.remove(t)

        self._game_spawn(w, h)
        self._game_process(w, h, theme)

        if self.g_score > self.g_high_score:
            self.g_high_score = self.g_score

        if self.g_player_y < 0 or self.g_player_y > h:
            self._game_die()

        self.g_speed += 0.0025

    def _game_spawn(self, w, h):
        if self.g_frenzy > 0:
            if random.random() < 0.25:
                self.g_shards.append({
                    'x': w, 'y': random.randint(50, int(h - 50)), 'type': 'coin'
                })
        else:
            if random.random() < 0.10:
                etype = random.choice(['std', 'std', 'seeker', 'bomber'])
                self.g_enemies.append({
                    'x': w, 'y': random.randint(50, int(h - 50)),
                    'type': etype, 'hp': 1
                })
            if random.random() < 0.025:
                stype = random.choice(['shield', 'bull', 'coin', 'health'])
                self.g_shards.append({
                    'x': w, 'y': random.randint(100, int(h - 100)), 'type': stype
                })

    def _game_process(self, w, h, theme):
        speed = self.g_speed

        for e in self.g_enemies[:]:
            spd = speed * 0.5 if theme['hazard'] == 'slow_field' else speed
            e['x'] -= spd
            if e['type'] == 'seeker':
                e['y'] += 3 if e['y'] < self.g_player_y else -3

            if abs(e['x'] - 100) < 35 and abs(e['y'] - self.g_player_y) < 35:
                if self.g_shield > 0:
                    self.g_shield = 0
                    self.g_enemies.remove(e)
                    self.shake = 25
                    self.g_glitch = 10
                    spawn_burst(self.particles, e['x'], e['y'],
                                hue=0.55, count=20)
                    sound.play_effect('arcade:Explosion_3')
                else:
                    self.g_health -= 1
                    self.g_enemies.remove(e)
                    self.shake = 30
                    self.g_glitch = 15
                    spawn_burst(self.particles, e['x'], e['y'],
                                hue=0.0, count=25)
                    sound.play_effect('arcade:Hit_1', volume=0.5)
                    if self.g_health <= 0:
                        self._game_die()
                        return
            elif e['x'] < -100:
                self.g_enemies.remove(e)

        for s in self.g_shards[:]:
            s['x'] -= speed
            if abs(s['x'] - 100) < 45 and abs(s['y'] - self.g_player_y) < 45:
                if   s['type'] == 'shield':
                    self.g_shield = 1
                    sound.play_effect('digital:PowerUp7')
                elif s['type'] == 'bull':
                    self.g_bull_mode = 350
                    sound.play_effect('digital:PowerUp8')
                elif s['type'] == 'health':
                    self.g_health = min(3, self.g_health + 1)
                    sound.play_effect('digital:PowerUp7')
                else:
                    self.g_score += 2000
                    sound.play_effect('digital:Coins3')
                spawn_burst(self.particles, s['x'], s['y'],
                            hue=0.15 if s['type'] == 'coin' else 0.6,
                            count=18)
                self.g_shards.remove(s)
            elif s['x'] < -60:
                self.g_shards.remove(s)

        for b in self.g_bullets[:]:
            b['x'] += 25
            if b['x'] > w:
                self.g_bullets.remove(b)
                continue
            for e in self.g_enemies[:]:
                if abs(b['x'] - e['x']) < 40 and abs(b['y'] - e['y']) < 40:
                    self.g_score += 250
                    spawn_burst(self.particles, e['x'], e['y'],
                                hue=theme['e_color'][0] * 0.33, count=15)
                    if e in self.g_enemies:  self.g_enemies.remove(e)
                    if b in self.g_bullets:  self.g_bullets.remove(b)
                    sound.play_effect('arcade:Hit_3', volume=0.3)
                    break

    def _game_die(self):
        if self.state == S_GAMEOVER:
            return
        self.state = S_GAMEOVER
        sound.stop_all_effects()
        sound.play_effect('arcade:Explosion_1')
        spawn_burst(self.particles,
                    self.size.w / 2, self.g_player_y,
                    hue=0.0, count=60, speed=14, size=14)
        self.shake = 40

    # ------------------------------------------------------- touch handling
    def touch_began(self, touch):
        tx, ty = touch.location

        # In-game tap
        if self.state == S_GAME:
            is_inverted = (self.g_score // 7000) % 2 == 1
            self.g_dy = -12 if is_inverted else 12
            self.g_bullets.append({'x': 135, 'y': self.g_player_y})
            if self.g_bull_mode > 0:
                self.g_bullets.append({'x': 135, 'y': self.g_player_y + 25})
                self.g_bullets.append({'x': 135, 'y': self.g_player_y - 25})
            sound.play_effect('arcade:Laser_2', volume=0.25)
            return

        # Game over — tap = retry, long hold is checked in touch_ended
        if self.state == S_GAMEOVER:
            self._touch_started_at = self.timer
            return

        # Check buttons
        for btn in self.buttons:
            if btn.hit(tx, ty):
                self._press_button(btn, tx, ty)
                return

    def touch_ended(self, touch):
        if self.state == S_GAMEOVER:
            hold_time = self.timer - getattr(self, '_touch_started_at', self.timer)
            if hold_time > 0.6:
                # Long hold → return to lessons
                self._transition_to(S_LESSON, sound_name='arcade:Powerup_1')
            else:
                # Short tap → retry
                self._game_reset()
                self.state = S_GAME
                sound.play_effect('digital:PowerUp6')
            return

    # ------------------------------------------------------- button press
    def _press_button(self, btn, tx, ty):
        btn.pulse = 1.0
        self.shake  = 18
        self.flash  = 0.9
        hue = random.random()
        spawn_burst(self.particles, tx, ty, hue=hue, count=35, speed=10, size=12)

        label = btn.label

        if label == 'TAP TO BEGIN →':
            self._transition_to(S_ENTER_NAME, 'digital:PowerUp6')

        elif label == "I'M READY →":
            self._transition_to(S_PCVR_INTRO, 'digital:PowerUp7')

        elif label == 'START LEARNING →':
            self.lesson_idx = 0
            self._transition_to(S_LESSON, 'arcade:Powerup_1')

        elif label == 'NEXT LESSON →':
            self.lesson_idx += 1
            self._transition_to(S_LESSON, 'arcade:Powerup_2')

        elif label == 'PLAY WARP PROTOCOL →':
            self._transition_to(S_GAME_INTRO, 'arcade:Powerup_3')

        elif label == 'LAUNCH MISSION →':
            self._game_reset()
            self._transition_to(S_GAME, 'digital:PowerUp8')

        elif label == '← BACK':
            self.lesson_idx -= 1
            self._transition_to(S_LESSON, 'arcade:Click_1')

        elif label == '← BACK TO LESSONS':
            self.lesson_idx = len(LESSONS) - 1
            self._transition_to(S_LESSON, 'arcade:Click_1')

    # ------------------------------------------------------- transitions
    def _transition_to(self, new_state, sound_name=None):
        if sound_name:
            try:
                sound.play_effect(sound_name)
            except Exception:
                pass

        def _apply():
            self.state    = new_state
            self.slide_t  = 0.0
            self._make_buttons()

        self.transition.start_out(callback=_apply)

    # ------------------------------------------------------- easing helper
    @staticmethod
    def _ease(t):
        """Cubic ease-out: fast start, smooth finish."""
        t = max(0.0, min(1.0, t))
        return 1.0 - (1.0 - t) ** 3


# ---------------------------------------------------------------------------
if __name__ == '__main__':
    run(PCVREdTech(), PORTRAIT)
