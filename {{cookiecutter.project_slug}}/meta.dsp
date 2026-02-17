declare name "{{ cookiecutter.project_name }}";
declare author "{{ cookiecutter.author_name }}";
declare version "0.1.0";
declare description "{{ cookiecutter.project_description }}";
{% if cookiecutter.is_synth == 'true' %}
declare options "[midi:on][nvoices:{{ cookiecutter.nvoices }}]";
{% endif %}
import("stdfaust.lib");

process = library("main.dsp").process;
