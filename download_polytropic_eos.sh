#!/bin/bash

# Note: this is specific to macOS
# See the EOS at http://www.computational-relativity.org/eos/
# Define the EOS names
POLYTROPIC_EOS_NAMES=("2B" "2H" "ALF2" "ENG" "H4" "MPA1" "MS1" "MS1b" "SLy")

# Loop through each EOS name and download the corresponding file
for EOS_NAME in "${POLYTROPIC_EOS_NAMES[@]}"; do
    FILE_URL="http://www.computational-relativity.org/assets/eos/EOS_${EOS_NAME}.txt"
    OUTPUT_FILE="${EOS_NAME}.txt"
    curl -o "$OUTPUT_FILE" "$FILE_URL"
done
