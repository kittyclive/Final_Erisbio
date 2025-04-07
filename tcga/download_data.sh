#!/bin/bash

# Number of parallel downloads (adjust as needed)
PARALLEL_DOWNLOADS=8

# Download files in parallel
echo "$@" | xargs -n 1 -P $PARALLEL_DOWNLOADS ./gdc_distributions/gdc-client-mac download -d ./data