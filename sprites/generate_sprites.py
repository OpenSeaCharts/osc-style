import os
import shutil
import subprocess
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

def check_tool(tool_name):
    """Check if a tool is available in the system path."""
    if shutil.which(tool_name) is None:
        print(f"Error: '{tool_name}' is not installed or not in PATH.")
        sys.exit(1)

def convert_svg(args):
    """Helper function for parallel execution of rsvg-convert."""
    input_file, output_file, width, dpi = args
    
    cmd = [
        "rsvg-convert",
        str(input_file),
        "-a",
        "-f", "svg",
        "-w", str(width),
        "-o", str(output_file)
    ]
    
    if dpi:
        cmd.extend(["-d", str(dpi), "-p", str(dpi)])
        
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file.name}: {e.stderr.decode()}")
        raise

def process_json(json_path):
    """Add 'sdf': true to entries ending with _sdf."""
    if not json_path.exists():
        print(f"Warning: {json_path} does not exist.")
        return

    print(f"Processing {json_path.name}...")
    
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Recursive function to walk the JSON and add sdf flag
    def walk(obj):
        if isinstance(obj, dict):
            # If this object represents a sprite (has width, height, etc) 
            # and the key (passed from parent loop) ends in _sdf, we modify it.
            # However, the structure is usually { "icon_name": { "width": ... } }
            # So we iterate the dict.
            for k, v in obj.items():
                if isinstance(v, dict):
                    if k.endswith("_sdf"):
                        v["sdf"] = True
                    walk(v)
        elif isinstance(obj, list):
            for x in obj:
                walk(x)

    # The original jq command was:
    # walk(if type == "object" then with_entries(if (.key | endswith("_sdf")) then .value |= . + {"sdf": true} else . end) else . end)
    # This implies it looks at keys in objects.
    
    walk(data)

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    # Check dependencies
    check_tool("rsvg-convert")
    check_tool("spreet")

    # Define paths
    base_dir = Path(__file__).parent.resolve()
    svg_dir = base_dir / "svg"
    build_dir = base_dir / "build"
    build_svg_dir = build_dir / "svg"
    build_svg1x_dir = build_dir / "svg1x"
    build_svg2x_dir = build_dir / "svg2x"
    
    # Clean up and create directories
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    for d in [build_svg_dir, build_svg1x_dir, build_svg2x_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print("Collecting SVGs...")
    # Copy all SVG files to a temporary flat directory
    svg_files = []
    for svg_file in svg_dir.rglob("*"):
        if svg_file.is_file() and svg_file.suffix.lower() == ".svg":
            dest = build_svg_dir / svg_file.name
            shutil.copy2(svg_file, dest)
            svg_files.append(dest)

    if not svg_files:
        print("No SVG files found.")
        return

    print(f"Found {len(svg_files)} SVGs.")

    # Prepare tasks for parallel execution
    tasks_1x = []
    tasks_2x = []
    
    for svg_file in svg_files:
        # 1x: width 26
        tasks_1x.append((svg_file, build_svg1x_dir / svg_file.name, 26, None))
        # 2x: width 26, dpi 52 (effectively double resolution for rsvg-convert if dimensions are physical, 
        # but here we set width explicitly. The original script used -d 52 -p 52.
        # rsvg-convert default dpi is 96. 
        # If we set width to 26, it scales to 26px.
        # The original script: rsvg-convert "$old" -a -f svg -w 26 -d 52 -p 52 -o "$new"
        # If we set DPI to 52 (lower than 96), and width to 26... wait.
        # Usually 2x means double size. 
        # If I set -w 26, the output width is 26 pixels (or units).
        # If I change DPI, it affects how physical units (mm, in) map to pixels.
        # But if the input is unitless or pixels, DPI might not matter unless we are rasterizing?
        # But we are outputting SVG (-f svg).
        # Let's stick exactly to the original command arguments to be safe.
        tasks_2x.append((svg_file, build_svg2x_dir / svg_file.name, 26, 52))

    print("Converting SVGs (1x)...")
    with ThreadPoolExecutor() as executor:
        list(executor.map(convert_svg, tasks_1x))

    print("Converting SVGs (2x)...")
    with ThreadPoolExecutor() as executor:
        list(executor.map(convert_svg, tasks_2x))

    print("Generating sprites...")
    try:
        # spreet --unique --recursive build/svg1x sprites
        subprocess.run(["spreet", "--unique", "--recursive", str(build_svg1x_dir), str(base_dir / "sprites")], check=True)
        
        # spreet --unique --recursive --ratio=2 build/svg2x sprites@2x
        subprocess.run(["spreet", "--unique", "--recursive", "--ratio=2", str(build_svg2x_dir), str(base_dir / "sprites@2x")], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error generating sprites: {e}")
        sys.exit(1)

    print("Post-processing JSON...")
    process_json(base_dir / "sprites.json")
    process_json(base_dir / "sprites@2x.json")

    print("Done.")

if __name__ == "__main__":
    main()
