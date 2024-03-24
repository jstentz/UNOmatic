'''
Script for finding the color of an image.
'''

import cv2
import numpy as np
import os


def calculate_average_intensity(image, mask):
  masked_image = cv2.bitwise_and(image, image, mask=mask)
  masked_gray = cv2.cvtColor(masked_image, cv2.COLOR_BGR2GRAY)
  total_intensity = np.sum(masked_gray)
  size = image.shape[0] * image.shape[1]
  average_intensity = total_intensity / size
  return average_intensity

def get_color(image):

  # Convert the image from BGR to HSV color space
  hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

  # Define range for yellow color in HSV
  lower_yellow = np.array([25, 150, 20])
  upper_yellow = np.array([35, 255, 255])

  # Create a mask to extract yellow regions
  yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

  # Calculate average intensity after applying yellow mask
  yellow_intensity = calculate_average_intensity(image, yellow_mask)

  # Define range for red color in HSV
  lower_red_1 = np.array([0, 150, 20])
  upper_red_1 = np.array([10, 255, 200])
  lower_red_2 = np.array([170, 150, 20])
  upper_red_2 = np.array([180, 255, 200])
  # Create a mask to extract red regions
  red_mask_1 = cv2.inRange(hsv_image, lower_red_1, upper_red_1)
  red_mask_2 = cv2.inRange(hsv_image, lower_red_2, upper_red_2)

  # Calculate average intensity after applying red mask
  red_intensity = calculate_average_intensity(image, red_mask_1 + red_mask_2)

  # Define range for blue color in HSV
  lower_blue = np.array([90, 150, 20])
  upper_blue = np.array([150, 255, 255])

  # Create a mask to extract blue regions
  blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

  # Calculate average intensity after applying blue mask
  blue_intensity = calculate_average_intensity(image, blue_mask)

  # Define range for red color in HSV
  lower_green = np.array([40, 150, 20])
  upper_green = np.array([80, 255, 255])

  # Create a mask to extract green regions
  green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

  # Calculate average intensity after applying green mask
  green_intensity = calculate_average_intensity(image, green_mask)

  intensities = [red_intensity, yellow_intensity, green_intensity, blue_intensity]
  labels = ['red', 'yellow', 'green', 'blue']
  label = max(zip(intensities, labels), key=lambda x: x[0])[1]
  return label, labels.index(label)


if __name__ == '__main__':
  infile = open('./data/all_images_base.csv', 'r')
  outfile = open('./data/all_images_base_color.csv', 'w')


  outfile.write('image,label,label_idx\n')
  
  lines = infile.readlines()[1:]

  for line in lines:
    path, _, _ = line.split(',')
    image = cv2.imread(path)
    label, label_idx = get_color(image)
    outfile.write(f'{path},{label},{label_idx}\n')

  infile.close()
  outfile.close()
  # image_names = os.listdir(images_dir)


  # for image_name in sorted(image_names, key=lambda x: int(x.removesuffix('.jpg')[x.find('_')+1:])):
  #   image_path = os.path.join(images_dir, image_name)

  #   # Read the image
  #   image = cv2.imread(image_path)
  #   label = get_color(image)

  #   cv2.imshow(label, image)
  #   cv2.waitKey(0)
  #   cv2.destroyAllWindows()