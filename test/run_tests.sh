#!/bin/bash
current_dir=$(dirname "$(readlink -f "$0")")
script_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG="$current_dir"/deploy.cfg
# export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg
export KB_AUTH_TOKEN=`cat /kb/module/work/token`
export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH
# cd $script_dir/../test
# python -m nose --with-coverage --cover-package=NarrativeService --cover-html --cover-html-dir=/kb/module/work/cover_html --nocapture .
pytest \
    --cov=lib/NarrativeService \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    test
