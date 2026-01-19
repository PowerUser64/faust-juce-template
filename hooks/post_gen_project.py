#!/usr/bin/env python3
"""
Post-generation hook for faust-juce-template.

This script runs after cookiecutter generates the project.
It initializes git, sets up submodules, and copies Faust architecture files.
"""

import os
import shutil
import subprocess
import sys


def run_command(cmd, check=True, capture=True):
    """Run a shell command and optionally check for errors."""
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        if capture:
            print(f"  Warning: {result.stderr.strip()}")
        return False
    return result if capture else True


def get_faust_archdir():
    """Get the Faust architecture directory from the faust command."""
    try:
        result = subprocess.run(
            ["faust", "--archdir"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


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

    # Copy Faust architecture files
    print("\nSetting up Faust architecture files...")
    faust_archdir = get_faust_archdir()
    faust_dest = os.path.join("external", "faust", "architecture")

    if faust_archdir and os.path.isdir(faust_archdir):
        print(f"  Found Faust architecture at: {faust_archdir}")
        print(f"  Copying to: {faust_dest}")
        os.makedirs(os.path.dirname(faust_dest), exist_ok=True)
        if os.path.exists(faust_dest):
            shutil.rmtree(faust_dest)
        shutil.copytree(faust_archdir, faust_dest)
        print("  Faust architecture files copied successfully!")
        faust_setup_complete = True
    else:
        print("  Warning: Could not find Faust installation.")
        print("  You will need to manually copy the architecture files.")
        faust_setup_complete = False

    # Print completion message
    print(f"\n{'=' * 60}")
    print(f"Project '{project_slug}' created successfully!")
    print(f"{'=' * 60}")

    if faust_setup_complete:
        print(f"""
All dependencies are set up! You can now build:

    cd {project_slug}
    cmake -S . -B build -G Ninja
    cmake --build build -j

Then test it:

    ./build/{project_slug}_artefacts/Debug/Standalone/{project_slug}
""")
    else:
        print(f"""
Almost done! You need to copy Faust architecture files:

    mkdir -p external/faust
    cp -r /path/to/faust/architecture external/faust/

    # Or if faust is installed elsewhere:
    cp -r $(faust --archdir) external/faust/architecture

Then build:

    cmake -S . -B build -G Ninja
    cmake --build build -j
""")

    print("Happy coding!\n")


if __name__ == "__main__":
    main()
