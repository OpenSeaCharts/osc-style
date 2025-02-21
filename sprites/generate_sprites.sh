#!/usr/bin/env bash

rm -R tmp/svg

# Copy all SVG files to a temporary flat directory
mkdir -p tmp/svg
find svg -type f -exec cp {} tmp/svg/ \;

# Generate sprites, install spreet with `brew install flother/taps/spreet` or `cargo install spreet`
spreet --unique --recursive tmp/svg sprites
spreet --unique --recursive --ratio=2 tmp/svg sprites@2x

# Add the sdf field when the sprite name ends with _sdf
temp_file=$(mktemp)
jq 'walk(if type == "object" then with_entries(
    if (.key | endswith("_sdf")) then .value |= . + {"sdf": true} else . end
) else . end)' "sprites.json" > $temp_file
mv $temp_file "sprites.json"

jq 'walk(if type == "object" then with_entries(
    if (.key | endswith("_sdf")) then .value |= . + {"sdf": true} else . end
) else . end)' "sprites@2x.json" > $temp_file
mv $temp_file "sprites@2x.json"