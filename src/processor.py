import imageio.v3 as iio
import numpy as np

def autocrop(image_path, output_path):
  img = iio.imread(image_path)
  
  if img.shape[2] == 4:
    alpha_mask = img[:, :, 3] >= 128
  else:
    # If no alpha, treat all pixels as opaque
    alpha_mask = np.ones(img.shape[:2], dtype=bool)

  color_mask = np.any(img[:, :, :3] < 255, axis=2)
  final_mask = alpha_mask & color_mask
  coords = np.argwhere(final_mask)

  if coords.size == 0:
    #print("Image is entirely empty or white!")
    return

  y_min, x_min = coords.min(axis=0)
  y_max, x_max = coords.max(axis=0)

  cropped_img = img[y_min:y_max+1, x_min:x_max+1]

  iio.imwrite(output_path, cropped_img)
  #print(f"Cropped from {img.shape[:2]} to {cropped_img.shape[:2]}")

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

  colored_output: list[str] = []

  for asc_y, line in enumerate(ascii_lines):
    colored_line: list[str] = []
    
    for asc_x, char in enumerate(line):
      # Scale pixel to ascii position (and get center)
      pix_x = int((asc_x + 0.5) * scale_x)
      pix_y = int((asc_y + 0.5) * scale_y)

      # Clamp in case of floating point rounding error
      pix_x = min(pix_x, img_width - 1)
      pix_y = min(pix_y, img_height - 1)

      # Extract RGBA values
      pixel = img[pix_y, pix_x]
      
      # Handle Transparency (The "White Edge" Fix)
      # If the image has an Alpha channel and the pixel is transparent, 
      # we treat it as black (or background) to avoid white artifacts.
      if len(pixel) == 4:
          r, g, b, a = pixel
          if a < 128: # If more than 50% transparent
              r, g, b = 0, 0, 0 
      else:
          r, g, b = pixel[:3]

      # Apply TrueColor ANSI escape codes
      colored_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
      colored_line.append(colored_char)

    colored_output.append("".join(colored_line))

  return colored_output