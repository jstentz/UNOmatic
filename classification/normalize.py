'''
Loop over the training data, and get the mean / stdev for each of the color channels
'''

import numpy as np
import cv2 as cv


infile = open('./top_data/images_train.csv', 'r')
image_size = (360, 360)
total_size = image_size[0] * image_size[1]

red_sum = 0
red_sum_squares = 0
green_sum = 0
green_sum_squares = 0
blue_sum = 0
blue_sum_squares = 0
num_images = 0

for line in infile.readlines()[1:]:
  path, _, _ = line.split(',')
  image = cv.imread(path) / 255
  image_red = image[:, :, 0]
  image_green = image[:, :, 1]
  image_blue = image[:, :, 2]

  red_sum += np.sum(image_red)
  green_sum += np.sum(image_green)
  blue_sum += np.sum(image_blue)

  red_sum_squares += np.sum(image_red ** 2)
  green_sum_squares += np.sum(image_green ** 2)
  blue_sum_squares += np.sum(image_blue ** 2)

  num_images += 1


red_mean = red_sum / (num_images * total_size)
green_mean = green_sum / (num_images * total_size)
blue_mean = blue_sum / (num_images * total_size)

red_std = np.sqrt((red_sum_squares / (num_images * total_size)) - (red_mean ** 2))
green_std = np.sqrt((green_sum_squares / (num_images * total_size)) - (green_mean ** 2))
blue_std = np.sqrt((blue_sum_squares / (num_images * total_size)) - (blue_mean ** 2))


print(f'Means: [{red_mean}, {green_mean}, {blue_mean}]')
print(f'Stdevs: [{red_std}, {green_std}, {blue_std}]')