'''
Takes in images and outputs different images based on distributions.
'''

import cv2 as cv
import numpy as np
import sys
import scipy
import os

from color_classifier import get_color

saturation_mean, saturation_stdev = 1.0, 0.1
brightness_mean, brightness_stdev = 1.0, 0.2
hue_mean, hue_stdev = 1.0, 0.01
zoom_mean, zoom_stdev = 1.0, 0.3
angle_mean, angle_stdev = 0.0, 1.0
coord_mean, coord_stdev = np.array([180, 180]), np.array([20, 20])

# number of generated images per image
N = 30

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


# use the coord to translate
def zoom_at(img, zoom, angle, coord=None):
  cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
  rot_mat = cv.getRotationMatrix2D((cx,cy), angle, zoom)
  result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)
  return result

def get_random_image(image):
  brightness_factor = np.random.normal(loc=brightness_mean, scale=brightness_stdev)
  saturation_factor = np.random.normal(loc=saturation_mean, scale=saturation_stdev)
  hue_factor = np.random.normal(loc=hue_mean, scale=hue_stdev)
  image_new = change_brightness(image, brightness_factor)
  image_new = change_saturation(image_new, saturation_factor)
  image_new = change_hue(image_new, hue_factor)
  image_new = zoom_at(image_new, 
                      zoom=scipy.stats.halfnorm.rvs(loc=zoom_mean, scale=zoom_stdev, size=1)[0],
                      angle=scipy.stats.halfnorm.rvs(loc=angle_mean, scale=angle_stdev, size=1)[0],
                      coord=np.random.normal(loc=coord_mean, scale=coord_stdev))
  return image_new

def flip_image(image):
  return image[::-1, ::-1]


if __name__ == '__main__':

  # path to a file with a bunch of labeled images
  infile_path = './bot_data/all_images_base.csv'
  outfile_path = './bot_data/all_images_modified.csv'
  infile = open(infile_path, 'r')
  outfile = open(outfile_path, 'w')

  out_images_path = './bot_data/images_modified'

  lines = infile.readlines()

  # write the header in the new file
  outfile.write(lines[0])

  for line in lines[1:]:
    image_path, label_name, label_idx = line[:-1].split(',')

    # load the image
    # image = flip_image(cv.imread(image_path))
    image = cv.imread(image_path) # don't flip for bottom images

    new_image_path = os.path.join(out_images_path, f'{os.path.basename(image_path).removesuffix(".jpg")}_{0}.jpg')

    # write the initial image 
    cv.imwrite(new_image_path, image)

    # save this in the csv file
    outfile.write(f'{new_image_path},{label_name},{label_idx}\n')

    for n in range(1, N):
      new_image = get_random_image(image)
      new_image_path = os.path.join(out_images_path, f'{os.path.basename(image_path).removesuffix(".jpg")}_{n}.jpg')


      # cv.imshow('test', new_image)
      # cv.waitKey(0)
      # cv.destroyAllWindows()
      # write the new image 
      cv.imwrite(new_image_path, new_image)

      # save this in the csv file
      outfile.write(f'{new_image_path},{label_name},{label_idx}\n')


  infile.close()
  outfile.close()
