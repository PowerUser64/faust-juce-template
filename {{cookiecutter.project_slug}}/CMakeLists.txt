cmake_minimum_required(VERSION 3.22)

project({{ cookiecutter.project_slug }} VERSION 0.1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------
# Dependencies
# -----------------

add_subdirectory(external/JUCE)

find_program(FAUST_EXECUTABLE faust REQUIRED)

# -----------------
# Faust JUCE plugin
# -----------------

juce_add_plugin({{ cookiecutter.project_slug }}
    COMPANY_NAME "{{ cookiecutter.author_name }}"
    IS_SYNTH {{ cookiecutter.is_synth | upper }}
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    FORMATS VST3 Standalone
    PLUGIN_MANUFACTURER_CODE {{ cookiecutter.manufacturer_code }}
    PLUGIN_CODE {{ cookiecutter.plugin_code }}
    PRODUCT_NAME "{{ cookiecutter.project_name }}")

juce_generate_juce_header({{ cookiecutter.project_slug }})

set(FAUST_DSP "${CMAKE_CURRENT_SOURCE_DIR}/meta.dsp")
set(FAUST_MAIN_DSP "${CMAKE_CURRENT_SOURCE_DIR}/main.dsp")
set(FAUST_ARCH_JUCE "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture/juce/juce-plugin.cpp")

set(FAUST_GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(FAUST_JUCE_PLUGIN_CPP "${FAUST_GENERATED_DIR}/FaustPluginProcessor.cpp")

file(MAKE_DIRECTORY "${FAUST_GENERATED_DIR}")

# The Faust JUCE architecture expects a Projucer-style include.
# Provide a shim in the build tree.
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/JuceLibraryCode")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/JuceLibraryCode/JuceHeader.h" "#pragma once\n#include <JuceHeader.h>\n")

add_custom_command(
    OUTPUT "${FAUST_JUCE_PLUGIN_CPP}"
    COMMAND "${FAUST_EXECUTABLE}"
        -i
        -uim
        -I "${CMAKE_CURRENT_SOURCE_DIR}"
        -A "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture"
        -a "${FAUST_ARCH_JUCE}"
        -o "${FAUST_JUCE_PLUGIN_CPP}"
        "${FAUST_DSP}"
    DEPENDS "${FAUST_DSP}" "${FAUST_MAIN_DSP}" "${FAUST_ARCH_JUCE}"
    VERBATIM)

set_source_files_properties("${FAUST_JUCE_PLUGIN_CPP}" PROPERTIES GENERATED TRUE)

target_sources({{ cookiecutter.project_slug }} PRIVATE "${FAUST_JUCE_PLUGIN_CPP}")

target_include_directories({{ cookiecutter.project_slug }}
    PRIVATE
        "${CMAKE_CURRENT_BINARY_DIR}"
        "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture")

target_compile_definitions({{ cookiecutter.project_slug }}
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        JUCE_DISABLE_CAUTIOUS_PARAMETER_ID_CHECKING=1
    PRIVATE
        MIDICTRL=1)

target_link_libraries({{ cookiecutter.project_slug }}
    PRIVATE
        juce::juce_audio_utils
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_lto_flags
        juce::juce_recommended_warning_flags)

# -----------------
# CLAP wrapper
# -----------------

option({{ cookiecutter.project_slug | upper | replace('-', '_') }}_BUILD_CLAP "Build CLAP plugin wrapper" ON)

if ({{ cookiecutter.project_slug | upper | replace('-', '_') }}_BUILD_CLAP)
    if (NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/external/clap-juce-extensions/CMakeLists.txt")
        message(FATAL_ERROR "Missing external/clap-juce-extensions. Run: git submodule update --init --recursive")
    endif()

    add_subdirectory(external/clap-juce-extensions EXCLUDE_FROM_ALL)

    clap_juce_extensions_plugin(TARGET {{ cookiecutter.project_slug }}
        CLAP_ID "{{ cookiecutter.clap_id }}"
        CLAP_FEATURES instrument{% if cookiecutter.is_synth == 'true' %} synthesizer{% endif %})
endif()
{% if cookiecutter.include_jack_app == 'true' %}
# -----------------
# JACK test app
# -----------------

option({{ cookiecutter.project_slug | upper | replace('-', '_') }}_BUILD_JACK "Build JACK MIDI test app" ON)

if ({{ cookiecutter.project_slug | upper | replace('-', '_') }}_BUILD_JACK AND UNIX AND NOT APPLE)
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(JACK REQUIRED jack)

    set(FAUST_ARCH_JACK "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture/jack-console.cpp")
    set(FAUST_JACK_CPP "${FAUST_GENERATED_DIR}/{{ cookiecutter.project_slug }}_jack.cpp")

    add_custom_command(
        OUTPUT "${FAUST_JACK_CPP}"
        COMMAND "${FAUST_EXECUTABLE}"
            -i
            -uim
            -I "${CMAKE_CURRENT_SOURCE_DIR}"
            -A "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture"
            -a "${FAUST_ARCH_JACK}"
            -o "${FAUST_JACK_CPP}"
            "${FAUST_DSP}"
        DEPENDS "${FAUST_DSP}" "${FAUST_MAIN_DSP}" "${FAUST_ARCH_JACK}"
        VERBATIM)

    add_executable({{ cookiecutter.project_slug }}_jack "${FAUST_JACK_CPP}")

    target_include_directories({{ cookiecutter.project_slug }}_jack
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/external/faust/architecture"
            ${JACK_INCLUDE_DIRS})

    target_compile_definitions({{ cookiecutter.project_slug }}_jack
        PRIVATE
            MIDICTRL=1)

    # Faust jack-console.cpp pulls in ALSA symbols when MIDICTRL is enabled.
    # Link to ALSA explicitly to satisfy snd_seq_* / snd_midi_* references.
    target_link_libraries({{ cookiecutter.project_slug }}_jack
        PRIVATE
            ${JACK_LIBRARIES}
            asound)
endif()
{% endif %}
