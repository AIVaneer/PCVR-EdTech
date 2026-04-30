/*
============================================================
 PCVR Code Raiders Sound System
============================================================
 Works on iPhone and desktop using Web Audio API.
 Must be unlocked by user interaction.
============================================================
*/

const PCVRSound = {
  ctx: null,
  ready: false,
  muted: false,

  unlock: function () {
    if (this.ready) return;

    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
      this.ready = true;

      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.frequency.value = 1;
      gain.gain.value = 0.001;

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + 0.01);
    } catch (e) {
      console.log("Sound unlock failed:", e);
    }
  },

  tone: function (freq, duration, type, volume) {
    if (!this.ready || this.muted || !this.ctx) return;

    duration = duration || 0.15;
    type = type || "sine";
    volume = volume || 0.1;

    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.value = freq;

      gain.gain.setValueAtTime(volume, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(
        0.001,
        this.ctx.currentTime + duration
      );

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.log("Sound tone failed:", e);
    }
  },

  click: function () {
    this.tone(500, 0.05, "square", 0.05);
  },

  correct: function () {
    this.tone(600, 0.1, "sine", 0.09);
    setTimeout(() => this.tone(900, 0.12, "sine", 0.09), 90);
  },

  wrong: function () {
    this.tone(200, 0.2, "sawtooth", 0.08);
  },

  reward: function () {
    this.tone(700, 0.1, "triangle", 0.08);
    setTimeout(() => this.tone(900, 0.1, "triangle", 0.08), 100);
    setTimeout(() => this.tone(1200, 0.15, "triangle", 0.08), 200);
  },

  toggleMute: function () {
    this.muted = !this.muted;
    return this.muted;
  }
};
