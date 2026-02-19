import subprocess
import math

from .processor import autocrop, read_img, get_dim, get_scale, get_color_outp

def convert(path, width, dither, threshold, invert):
    result = subprocess.run(
        ["node", "run-braille.js", path, str(width), dither, str(threshold), "true" if invert else "false"],
        capture_output=True,
        text=True
    )
    return result.stdout

terminal_width = 202
terminal_height = 58-3

# --- Configuration ---
file_path = "images/mega_blaziken.png"
read_path = "data/outp.png"
ascii_width = terminal_width
dither = "floydSteinberg"
invert = False

autocrop(file_path, read_path)

img = read_img(read_path)
dim_x, dim_y = get_dim(img)

projected_ascii_height = math.ceil(ascii_width/(dim_x*2/dim_y))
if projected_ascii_height > terminal_height:
    ascii_width = math.floor(ascii_width * (terminal_height/projected_ascii_height))

raw = convert(read_path, ascii_width, dither, 199, invert)
ascii_lines = [line for line in raw.split("\n") if line.strip()] # Remove trailing empty lines
ascii_height = len(ascii_lines)

scale_x, scale_y = get_scale(dim_x, dim_y, ascii_width, ascii_height)
color_outp = get_color_outp(scale_x, scale_y, dim_x, dim_y, ascii_lines, img)

print("\n".join(color_outp))