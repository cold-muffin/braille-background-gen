import subprocess

from .processor import read_img, get_dim, get_scale, get_color_outp

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

raw = convert(file_path, ascii_width, dither, 100, invert)
ascii_lines = [line for line in raw.split("\n") if line.strip()] # Remove trailing empty lines
ascii_height = len(ascii_lines)

img = read_img(file_path)
dim_x, dim_y = get_dim(img)
scale_x, scale_y = get_scale(dim_x, dim_y, ascii_width, ascii_height)
color_outp = get_color_outp(scale_x, scale_y, dim_x, dim_y, ascii_lines, img)

print("\n".join(color_outp))