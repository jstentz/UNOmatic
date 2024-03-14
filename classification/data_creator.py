'''
Takes in images and outputs different images based on distributions.
'''

import cv2 as cv
import numpy as np
import sys

from color_classifier import get_color


saturation_stdev = 0.2
brightness_stdev = 0.2
hue_stdev = 0.01

def change_saturation(image, factor):
  image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV).astype(np.float32)
  image_hsv[:, :, 1] *= factor
  image_hsv[:, :, 1] = np.clip(image_hsv[:, :, 1], 0, 255)
  return cv.cvtColor(image_hsv.astype(np.uint8), cv.COLOR_HSV2BGR)
  
def change_brightness(image, factor):
  image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV).astype(np.float32)
  image_hsv[:, :, 2] *= factor
  image_hsv[:, :, 2] = np.clip(image_hsv[:, :, 2], 0, 255)
  return cv.cvtColor(image_hsv.astype(np.uint8), cv.COLOR_HSV2BGR)

def change_hue(image, factor):
  image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV).astype(np.float32)
  image_hsv[:, :, 0] *= factor
  image_hsv[:, :, 0] = np.clip(image_hsv[:, :, 0], 0, 180)
  return cv.cvtColor(image_hsv.astype(np.uint8), cv.COLOR_HSV2BGR)
  

if __name__ == '__main__':
  image_path = sys.argv[1]
  image = cv.imread(image_path)

  for _ in range(50):
    brightness_factor = np.random.normal(loc=1.0, scale=brightness_stdev)
    saturation_factor = np.random.normal(loc=1.0, scale=saturation_stdev)
    hue_factor = np.random.normal(loc=1.0, scale=hue_stdev)
    image_new = change_hue(image, hue_factor)
    image_new = change_hue(image_new, hue_factor)
    image_new = change_hue(image_new, hue_factor)
    cv.imshow('img', image_new)
    print(get_color(image_new))
    cv.waitKey(0)
  cv.destroyAllWindows()