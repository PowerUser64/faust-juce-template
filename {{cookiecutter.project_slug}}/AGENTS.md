# Agent Notes ({{ cookiecutter.project_slug }})

This directory builds a **Faust + JUCE** {% if cookiecutter.is_synth == 'true' %}polyphonic synth{% else %}audio effect{% endif %} plugin called **{{ cookiecutter.project_name }}**.

## Project Goals / Key Decisions

- **No Projucer**; everything is **CMake**.
- Targets built:
  - **Standalone** (JUCE)
  - **VST3** (JUCE)
  - **CLAP** (via clap-juce-extensions)
{%- if cookiecutter.include_jack_app == 'true' %}
  - **JACK test app** on Linux (`{{ cookiecutter.project_slug }}_jack`) using Faust `jack-console.cpp`.
{%- endif %}
- Vendor/manufacturer: **{{ cookiecutter.author_short }}**.
- CLAP ID: `{{ cookiecutter.clap_id }}`.
{%- if cookiecutter.is_synth == 'true' %}
- Default polyphony: **{{ cookiecutter.nvoices }} voices**.
{%- endif %}

## How to Build

From `{{ cookiecutter.project_slug }}/`:

```sh
# make sure nested submodules are present (CLAP wrapper)
git submodule update --init --recursive

# configure + build
cmake -S . -B build -G Ninja
cmake --build build -j
```

### Common build artifacts (Linux)

- Standalone: `build/{{ cookiecutter.project_slug }}_artefacts/Debug/Standalone/{{ cookiecutter.project_slug }}`
- VST3: `build/{{ cookiecutter.project_slug }}_artefacts/Debug/VST3/{{ cookiecutter.project_slug }}.vst3`
- CLAP: `build/{{ cookiecutter.project_slug }}_artefacts/Debug/CLAP/{{ cookiecutter.project_slug }}.clap`
{%- if cookiecutter.include_jack_app == 'true' %}
- JACK test app: `build/{{ cookiecutter.project_slug }}_jack`
{%- endif %}

Quick smoke run:

```sh
timeout 2 build/{{ cookiecutter.project_slug }}_artefacts/Debug/Standalone/{{ cookiecutter.project_slug }}
```
{% if cookiecutter.is_synth == 'true' %}
## MIDI + Polyphony (Faust-side)

The Faust code is written to match Faust's standard polyphony conventions:

- Per-voice parameters:
  - `gate`
  - `freq` (Hz)
  - `vel` (0..1)
- Global control:
  - `master` is mapped to MIDI CC7: `gain[midi:ctrl 7]`
- Pitch wheel:
  - `bend[midi:pitchwheel]` is used as a ratio multiplier.
  - Use `si.polySmooth(gate, ...)` to avoid pitch "sweeps" when reusing voices.

Important: `freq` must *not* be reused as a helper function name in the DSP, otherwise Faust will error with `multiple definitions of symbol 'freq'`.

The wrapper DSP `{{ cookiecutter.project_slug }}.dsp` explicitly enables Faust MIDI + polyphony via metadata:

- `declare options "[midi:on][nvoices:{{ cookiecutter.nvoices }}]";`
{% endif %}
## JUCE MIDI Path

The build defines `MIDICTRL=1`, so the Faust JUCE architecture uses `juce-midi.h` and decodes `juce::MidiBuffer`.

## CLAP Wrapper

CLAP is built via the git submodule:

- `external/clap-juce-extensions`

CMake enables it by default with `{{ cookiecutter.project_slug | upper | replace('-', '_') }}_BUILD_CLAP`.

## Lessons / Gotchas

- **JUCE debug assertion spam in Standalone**:
  - JUCE asserts in `juce_AudioProcessor.cpp` when parameter IDs exceed 31 chars or collide when trimmed (AAX safety checks).
  - Faust's JUCE parameter IDs are hierarchical paths and can easily exceed 31 chars.
  - We silence these checks by defining:
    - `JUCE_DISABLE_CAUTIOUS_PARAMETER_ID_CHECKING=1`
  - This is acceptable if you are not shipping AAX.

- **VST3 build hard error about VST2 migration**:
  - JUCE defaults `JUCE_VST3_CAN_REPLACE_VST2=1` which triggers a compile-time `#error` in the VST3 client.
  - We disable it in `CMakeLists.txt`:
    - `JUCE_VST3_CAN_REPLACE_VST2=0`
{% if cookiecutter.include_jack_app == 'true' %}
- **JACK test app link failure**:
  - When `MIDICTRL=1`, Faust's `jack-console.cpp` can reference ALSA sequencer symbols.
  - Link `asound` in addition to `jack`.
{% endif %}
