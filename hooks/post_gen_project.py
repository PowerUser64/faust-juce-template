#!/usr/bin/env python3
"""
Post-generation hook for faust-juce-template.

This script runs after cookiecutter generates the project.
It initializes git and sets up submodules.
"""

import os
import subprocess
import sys


def run_command(cmd, check=True):
    """Run a shell command and optionally check for errors."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  Warning: {result.stderr.strip()}")
        return False
    return True


def main():
    project_slug = "{{ cookiecutter.project_slug }}"
    juce_repo = "{{ cookiecutter._juce_repo }}"
    juce_tag = "{{ cookiecutter._juce_tag }}"
    clap_repo = "{{ cookiecutter._clap_ext_repo }}"

    print(f"\n{'=' * 60}")
    print(f"Setting up {project_slug}")
    print(f"{'=' * 60}\n")

    # Check if we're in a git repo already
    in_git = os.path.exists(".git")

    if not in_git:
        print("Initializing git repository...")
        run_command(["git", "init"])

    # Create external directory
    os.makedirs("external", exist_ok=True)

    print("\nAdding git submodules...")
    print("  (This may take a few minutes for JUCE)")

    # Add JUCE submodule
    print(f"\n  Adding JUCE from {juce_repo}...")
    if run_command(
        ["git", "submodule", "add", juce_repo, "external/JUCE"], check=False
    ):
        # Checkout specific tag
        print(f"  Checking out JUCE {juce_tag}...")
        run_command(["git", "-C", "external/JUCE", "checkout", juce_tag], check=False)

    # Add clap-juce-extensions submodule
    print(f"\n  Adding clap-juce-extensions from {clap_repo}...")
    run_command(
        ["git", "submodule", "add", clap_repo, "external/clap-juce-extensions"],
        check=False,
    )

    # Initialize nested submodules (clap-juce-extensions has its own)
    print("\n  Initializing nested submodules...")
    run_command(["git", "submodule", "update", "--init", "--recursive"], check=False)

    print(f"""
{"=" * 60}
Project '{project_slug}' created successfully!
{"=" * 60}

Next steps:

1. Copy Faust architecture files:
   mkdir -p external/faust
   cp -r /path/to/faust/architecture external/faust/

   Or if you have Faust installed:
   cp -r $(faust --archdir) external/faust/architecture

2. Build the project:
   cmake -S . -B build -G Ninja
   cmake --build build -j

3. Test it:
   ./build/{project_slug}_artefacts/Debug/Standalone/{project_slug}

Happy coding!
""")


if __name__ == "__main__":
    main()
