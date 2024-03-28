# import cv2 as cv
# import numpy as np

# num_rows = 7
# num_cols = 10

# image = cv.imread('images/UNO-Zeros.png')

# width, height, channels = image.shape
# card_width = width / num_cols
# card_height = height / num_rows

# colors = ['red', 'yellow', 'blue', 'green']

# def transparent(image: np.ndarray):
#   image = cv.cvtColor(image, cv.COLOR_BGR2BGRA)
  
#   # Extract the individual channels (B, G, R, A)
#   b, g, r, a = cv.split(image)

  

#   # Find black pixels (where R, G, and B values are all 0)
#   black_pixels = (r < 20) & (g < 20) & (b < 20)
#   corner_pixels = np.zeros_like(black_pixels)
#   corner_pixels[:int(card_height//8), :int(card_width//8)] = 1
#   corner_pixels[:int(card_height//8), int(card_width*7//8):] = 1
#   corner_pixels[int(card_height*7//8):, :int(card_width//8)] = 1
#   corner_pixels[int(card_height*7//8):, int(card_width*7//8):] = 1

#   # Set alpha channel value to 0 for black pixels
#   a[np.logical_and(black_pixels, corner_pixels)] = 0

#   # Merge the channels back together
#   bgra_image = cv.merge([b, g, r, a])
#   return bgra_image

# # get all the normal cards
# # for row in range(4):
# #   for col in range(9):
# #     num = col + 1
# #     color = colors[row]
# #     sx = int(col * card_width)
# #     sy = int(row * card_height)
# #     ex = int((col + 1) * card_width)
# #     ey = int((row + 1) * card_height)
# #     card_image = image[sy:ey, sx:ex]
# #     card_image = transparent(card_image)
# #     cv.imwrite(f'images/{color}_{num}.png', card_image)

# # get others
# row = 0
# for col in range(4):
#   color = colors[col % 4]
#   sx = int(col * card_width)
#   sy = int(row * card_height)
#   ex = int((col + 1) * card_width)
#   ey = int((row + 1) * card_height)
#   card_image = image[sy:ey, sx:ex]
#   card_image = transparent(card_image)
#   cv.imwrite(f'images/{color}_test{col}.png', card_image)



