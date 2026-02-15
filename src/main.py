import subprocess
import imageio.v3 as iio

def convert(path, width, dither, threshold, invert):
    result = subprocess.run(
        ["node", "run-braille.js", path, str(width), dither, str(threshold), "true" if invert else "false"],
        capture_output=True,
        text=True
    )
    return result.stdout

file_path = "data/sceptile-mega.png"
ascii_width = 50
dither = "atkinson"
invert = False

# Load image pixels
img = iio.imread(file_path)
img_height, img_width, _ = img.shape

# Generate ASCII art
raw = convert(file_path, ascii_width, dither, 100, invert)

ascii_lines = raw.split("\n")
ascii_height = len(ascii_lines)

# Compute scaling
scale_x = img_width / ascii_width
scale_y = img_height / ascii_height

colored_output = []

for ay, line in enumerate(ascii_lines):
    colored_line = []
    for ax, char in enumerate(line):
        # Map ASCII coordinate → image pixel
        px = int(ax * scale_x)
        py = int(ay * scale_y)

        r, g, b = img[py, px][:3]

        colored_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        colored_line.append(colored_char)

    colored_output.append("".join(colored_line))

print("\n".join(colored_output))