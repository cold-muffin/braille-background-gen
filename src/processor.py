import imageio.v3 as iio

def read_img(file_path):
  img = iio.imread(file_path)
  return img

def get_dim(img) -> tuple[int, int]:
  img_height, img_width = img.shape[:2]
  # Reverse to preserve order for rest of logic
  return img_width, img_height

def get_scale(img_width: int, img_height: int, ascii_width: int, ascii_height: int) -> tuple[float, float]:
  scale_x = img_width / ascii_width
  scale_y = img_height / ascii_height
  return scale_x, scale_y

def get_color_outp(
  scale_x: float,
  scale_y: float,
  img_width: int, 
  img_height: int, 
  ascii_lines: list[str],
  img
  ) -> list[str]:

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

  return colored_output