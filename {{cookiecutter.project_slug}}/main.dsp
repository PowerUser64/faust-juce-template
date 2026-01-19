import("stdfaust.lib");

// ============================================================================
// {{ cookiecutter.project_name }} - Main DSP
// ============================================================================
{% if cookiecutter.is_synth == 'true' %}
// MIDI/Polyphony (Faust standard polyphony parameters)
//
// The Faust polyphonic architectures detect per-voice parameters by name:
//   gate, freq (or key), gain (or vel/velocity)
//
// Use `vel` for per-note velocity, and reserve CC7 for master gain.

gate   = button("gate");
freq   = nentry("freq[unit:Hz]", 440, 20, 20000, 1);
vel    = nentry("vel", 1, 0, 1, 0.001);
master = nentry("gain[midi:ctrl 7]", 0.5, 0, 1, 0.001) : si.smoo;

// Pitch wheel in semitones converted to ratio.
// Use polySmooth so reused voices don't "sweep" when re-triggered.
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]", 0, -2, 2, 0.01)
        : si.polySmooth(gate, 0.999, 1));

// Envelope
attack  = hslider("[1]Attack", 0.01, 0.001, 2, 0.001);
decay   = hslider("[2]Decay", 0.1, 0.001, 2, 0.001);
sustain = hslider("[3]Sustain", 0.8, 0, 1, 0.01);
release = hslider("[4]Release", 0.2, 0.001, 4, 0.001);

env = en.adsr(attack, decay, sustain, release, gate);

// Simple sawtooth oscillator
oscillator = os.sawtooth(freq * bend);

// Output
process = oscillator * env * vel * master <: _, _;
{% else %}
// Simple effect example: stereo gain with smoothing

gain = hslider("Gain", 0.5, 0, 1, 0.01) : si.smoo;

process = _, _ : *(gain), *(gain);
{% endif %}
