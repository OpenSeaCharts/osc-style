#!/usr/bin/env bash

rm -R tmp

# Copy all SVG files to a temporary flat directory
mkdir -p tmp/svg tmp/svg1x tmp/svg2x
find svg -type f -exec cp {} tmp/svg/ \;

# install with `sudo apt-get install librsvg2-bin`
for old in tmp/svg/*; do
    new="./tmp/svg1x/$(basename "$old")"
    rsvg-convert "$old" -a -f svg -w 20 -o "$new"
done
for old in tmp/svg/*; do
    new="./tmp/svg2x/$(basename "$old")"
    rsvg-convert "$old" -a -f svg -w 20 -d 192 -p 192 -o "$new"
done

# Generate sprites, install spreet with `brew install flother/taps/spreet` or `cargo install spreet`
spreet --unique --recursive tmp/svg1x sprites
spreet --unique --recursive --ratio=2 tmp/svg2x sprites@2x

# Add the sdf field when the sprite name ends with _sdf
temp_file=$(mktemp)
jq 'walk(if type == "object" then with_entries(
    if (.key | endswith("_sdf")) then .value |= . + {"sdf": true} else . end
) else . end)' "sprites.json" > $temp_file
mv $temp_file "sprites.json"

#jq 'walk(if type == "object" then with_entries(
#    if (.key | endswith("_sdf")) then .value |= . + {"sdf": true} else . end
#) else . end)' "sprites@2x.json" > $temp_file
#mv $temp_file "sprites@2x.json"