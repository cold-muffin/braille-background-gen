import imageio.v3 as iio
import subprocess
import numpy as np

def convert(path, width, dither, threshold, invert):
    result = subprocess.run(
        ["node", "run-braille.js", path, str(width), dither, str(threshold), "true" if invert else "false"],
        capture_output=True,
        text=True
    )
    return result.stdout

# --- Configuration ---
file_path = "images/mega_magearna.png"
ascii_width = 202
dither = "floydSteinberg"
invert = False

# --- Image Processing ---
img = iio.imread(file_path)
img_height, img_width = img.shape[:2]

# Generate Braille string from your Node script
raw = convert(file_path, ascii_width, dither, 100, invert)
ascii_lines = [line for line in raw.split("\n") if line.strip()] # Remove trailing empty lines
ascii_height = len(ascii_lines)

# --- Coordinate Mapping Logic ---
# Calculate how many image pixels are represented by one Braille character
scale_x = img_width / ascii_width
scale_y = img_height / ascii_height



colored_output = []

for ay, line in enumerate(ascii_lines):
    colored_line = []
    
    for ax, char in enumerate(line):
        # 1. Calculate the center point of the current Braille cell in the image
        # Adding 0.5 ensures we sample the middle of the block, not the edge.
        px = int((ax + 0.5) * scale_x)
        py = int((ay + 0.5) * scale_y)

        # 2. Guard against rounding overflow
        px = min(px, img_width - 1)
        py = min(py, img_height - 1)

        # 3. Extract RGBA values
        pixel = img[py, px]
        
        # 4. Handle Transparency (The "White Edge" Fix)
        # If the image has an Alpha channel and the pixel is transparent, 
        # we treat it as black (or background) to avoid white artifacts.
        if len(pixel) == 4:
            r, g, b, a = pixel
            if a < 128: # If more than 50% transparent
                r, g, b = 0, 0, 0 
        else:
            r, g, b = pixel[:3]

        # 5. Apply TrueColor ANSI escape codes
        colored_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        colored_line.append(colored_char)

    colored_output.append("".join(colored_line))

print("\n".join(colored_output))