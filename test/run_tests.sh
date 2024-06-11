#!/bin/bash
current_dir=$(dirname "$(readlink -f "$0")")
script_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG="$current_dir"/deploy.cfg
if [ -f /kb/module/work/token ]; then
    echo "exporting token to KB_AUTH_TOKEN"
    export KB_AUTH_TOKEN=`cat /kb/module/work/token`
else
    echo "no token file, KB_AUTH_TOKEN is unset."
fi
export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH

unit_only="--ignore=test/integration"

# Include integration tests if run as "run_tests.sh integration", or
# if there's an SDK_CALLBACK_URL given. That env var is a signal
# that we're in kb-sdk test.
if [ "$1" = "integration" ] || [ -n "$SDK_CALLBACK_URL" ]; then
    unit_only=""
fi

pytest \
    --cov=lib/NarrativeService \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    test $unit_only
