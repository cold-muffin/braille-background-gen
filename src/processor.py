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
        
        y0 = int(asc_y * scale_y)
        y1 = max(y0 + 1, int((asc_y + 1) * scale_y))

        for asc_x, char in enumerate(line):
            x0 = int(asc_x * scale_x)
            x1 = max(x0 + 1, int((asc_x + 1) * scale_x))

            # Reset totals for this block
            total_r, total_g, total_b, weight = 0.0, 0.0, 0.0, 0.0

            # Get the block of pixels and cast to float to prevent overflow
            block = img[y0:min(y1, img_height), x0:min(x1, img_width)].astype(float)
            
            # Efficiently process the block
            for row in block:
                for pixel in row:
                    if len(pixel) == 4:
                        r, g, b, a = pixel
                        if a > 0:
                            total_r += r * a
                            total_g += g * a
                            total_b += b * a
                            weight += a
                    else:
                        r, g, b = pixel[:3]
                        total_r += r
                        total_g += g
                        total_b += b
                        weight += 1.0 # Standard weight for non-alpha

            if weight > 0:
                # If using alpha weighting, the max value is 255
                # If weight was based on 1.0 (non-alpha), we divide by count
                if len(img.shape) == 3 and img.shape[2] == 4:
                    r, g, b = int(total_r / weight), int(total_g / weight), int(total_b / weight)
                else:
                    count = block.shape[0] * block.shape[1]
                    r, g, b = int(total_r / count), int(total_g / count), int(total_b / count)
            else:
                r = g = b = 0 

            # Clamp values to 0-255 just to be safe before ANSI conversion
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            
            colored_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            colored_line.append(colored_char)

        colored_output.append("".join(colored_line))

    return colored_output