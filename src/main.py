import subprocess

def convert(path, width=100, dither="floydSteinberg", threshold=127, invert=False):
    result = subprocess.run(
        [
            "node", "run-braille.js",
            path,
            str(width),
            dither,
            str(threshold),
            "true" if invert else "false"
        ],
        capture_output=True,
        text=True
    )
    return result.stdout

ascii_art = convert(
    "data/mega_magearna.png",
    width=150,
    dither="atkinson",
    threshold=100,
    invert=True
)

print(ascii_art)
