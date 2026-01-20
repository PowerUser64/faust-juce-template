# DISCLAIMER

Here be dragons!

- This project was written by opencode and claude opus 4.5.
- The purpose of this is to get out of the way and let you write synthesizers with Faust, NOT to be a research project.

# Faust + JUCE Plugin Template

A lightweight [cookiecutter](https://github.com/cookiecutter/cookiecutter) template for creating audio plugins using Faust and JUCE.

## Features

- **No Projucer** - Pure CMake build system
- **Multiple formats** - Builds VST3, Standalone, and CLAP
- **Optional JACK app** - Linux JACK test application
- **Polyphonic synth support** - Standard Faust MIDI/polyphony conventions
- **Modern C++17** - Uses JUCE 8.x
- **Automatic setup** - Post-generation hook configures git submodules and Faust

## Requirements

- CMake 3.22+
- Ninja (recommended) or Make
- Faust compiler (`faust` in PATH)
- C++17 compiler (GCC, Clang, MSVC)
- Git
- Python 3.x with cookiecutter: `pip install cookiecutter`

## Usage

```bash
# Generate a new project
cookiecutter /path/to/faust-juce-template

# Or from a git repo
cookiecutter gh:yourusername/faust-juce-template
```

The post-generation hook will automatically:
1. Initialize a git repository
2. Add JUCE as a submodule (checked out to v8.0.4)
3. Add clap-juce-extensions as a submodule
4. Copy Faust architecture files (if `faust` is in PATH)

You'll be prompted for:

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Human-readable project name | My Synth |
| `project_slug` | Directory/target name (auto-generated) | my-synth |
| `project_description` | Short description | A Faust synthesizer plugin |
| `author_name` | Your name or company | Your Name |
| `author_short` | 3-letter abbreviation (auto-generated) | YOU |
| `clap_vendor` | CLAP vendor string (auto-generated) | yourname |
| `clap_id` | CLAP plugin ID (auto-generated) | audio.yourname.mysynth |
| `plugin_code` | 4-char JUCE plugin code (auto-generated) | Mys1 |
| `manufacturer_code` | 4-char manufacturer code (auto-generated) | YOUa |
| `nvoices` | Number of polyphonic voices | 16 |
| `is_synth` | Is this a synthesizer? | true |
| `include_jack_app` | Include JACK test app (Linux)? | true |

## After Generation

If Faust is installed and in your PATH, everything is set up automatically:

```bash
cd my-synth
cmake -S . -B build -G Ninja
cmake --build build -j
```

If Faust architecture files weren't copied automatically, you'll need to do it manually:

```bash
mkdir -p external/faust
cp -r $(faust --archdir) external/faust/architecture
```

## Project Structure

```
my-synth/
├── CMakeLists.txt           # Build configuration
├── my-synth.dsp             # Faust wrapper (metadata + imports main.dsp)
├── main.dsp                 # Your DSP code goes here
├── AGENTS.md                # Notes for AI agents / developers
├── .gitignore
└── external/                # Dependencies (set up by post-gen hook)
    ├── JUCE/                # Git submodule
    ├── clap-juce-extensions/ # Git submodule
    └── faust/
        └── architecture/    # Copied from system Faust installation
```

## Customization

Edit `main.dsp` to implement your DSP. The wrapper file (`<project_slug>.dsp`) handles metadata and imports.

For synths, follow Faust polyphony conventions:
- `gate` - Note on/off trigger
- `freq` - Note frequency in Hz
- `vel` - Velocity (0-1)
- Use `[midi:ctrl N]` for CC mapping
- Use `[midi:pitchwheel]` for pitch bend

## License

This template is provided as-is. Generated projects are yours to license as you see fit.
