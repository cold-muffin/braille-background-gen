import subprocess
import math
from dotenv import load_dotenv
from os import getenv
import sys
from pathlib import Path

from .processor import autocrop, read_img, get_dim, get_scale, get_color_outp

def convert(path, width, dither, threshold, invert):
    result = subprocess.run(
        ["node", "run-braille.js", path, str(width), dither, str(threshold), "true" if invert else "false"],
        capture_output=True,
        text=True
    )
    return result.stdout

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        terminal_width = int(sys.argv[1])
        terminal_height = int(sys.argv[2])-3
    else:
        raise ValueError("Please specify terminal width and height")

    # Read .env
    load_dotenv()

    PATH_TO_IMAGE_FILE=getenv("PATH_TO_IMAGE_FILE")
    DITHER=getenv("DITHER")
    THRESHOLD=getenv("TRESHOLD")
    INVERT=getenv("INVERT")
    MEMOIZATION=getenv("MEMOIZATION")

    if not PATH_TO_IMAGE_FILE:
        raise ValueError("No path to image file specified")

    file_path = PATH_TO_IMAGE_FILE
    dither = DITHER or "floydSteinberg"
    threshold = int(THRESHOLD or "100")

    if INVERT and INVERT not in ["true", "false"]:
        raise ValueError("Got INVERT as non-boolean value")
    elif INVERT == "true":
        invert = True
    else:
        invert = False
    
    if MEMOIZATION and MEMOIZATION not in ["true", "false"]:
        raise ValueError("Got INVERT as non-boolean value")
    elif MEMOIZATION == "true":
        memoization = True
    else:
        memoization = False

    if memoization:
        cache_path = Path(f"data/{".".join(file_path.split("/")[-1].split(".")[:-1])}")
        if not cache_path.exists():
            #print("Creating cache path...")
            with open(cache_path, "a") as f:
                f.write("\n".join([file_path, str(dither), str(threshold), str(invert), str(terminal_width), str(terminal_height)]))

    read_path = f"data/{file_path.split("/")[-1]}"
    ascii_width = terminal_width

    autocrop(file_path, read_path)

    img = read_img(read_path)
    dim_x, dim_y = get_dim(img)

    projected_ascii_height = math.ceil(ascii_width/(dim_x*2/dim_y))
    if projected_ascii_height > terminal_height:
        ascii_width = math.floor(ascii_width * (terminal_height/projected_ascii_height))

    raw = convert(read_path, ascii_width, dither, threshold, invert)
    ascii_lines = [line for line in raw.split("\n") if line.strip()] # Remove trailing empty lines
    ascii_height = len(ascii_lines)

    scale_x, scale_y = get_scale(dim_x, dim_y, ascii_width, ascii_height)
    color_outp = get_color_outp(scale_x, scale_y, dim_x, dim_y, ascii_lines, img)

    print("\n".join(color_outp))