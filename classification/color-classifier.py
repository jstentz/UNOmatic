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
  lower_yellow = np.array([25, 100, 100])
  upper_yellow = np.array([35, 255, 255])

  # Create a mask to extract yellow regions
  yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

  # Calculate average intensity after applying yellow mask
  yellow_intensity = calculate_average_intensity(image, yellow_mask)

  # Define range for red color in HSV
  lower_red = np.array([0, 100, 100])
  upper_red = np.array([10, 255, 200])

  # Create a mask to extract red regions
  red_mask = cv2.inRange(hsv_image, lower_red, upper_red)

  # Calculate average intensity after applying red mask
  red_intensity = calculate_average_intensity(image, red_mask)

  # Define range for blue color in HSV
  lower_blue = np.array([90, 100, 100])
  upper_blue = np.array([150, 255, 255])

  # Create a mask to extract blue regions
  blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

  # Calculate average intensity after applying blue mask
  blue_intensity = calculate_average_intensity(image, blue_mask)

  # Define range for red color in HSV
  lower_green = np.array([40, 100, 100])
  upper_green = np.array([80, 255, 255])

  # Create a mask to extract green regions
  green_mask = cv2.inRange(hsv_image, lower_green, upper_green)

  # Calculate average intensity after applying green mask
  green_intensity = calculate_average_intensity(image, green_mask)

  intensities = [red_intensity, green_intensity, blue_intensity, yellow_intensity]
  labels = ['red', 'green', 'blue', 'yellow']
  label = max(zip(intensities, labels), key=lambda x: x[0])[1]
  return label


if __name__ == '__main__':
  images_dir = 'top_data/'
  image_names = os.listdir(images_dir)


  for image_name in sorted(image_names, key=lambda x: int(x.removesuffix('.jpg')[x.find('_')+1:])):
    image_path = os.path.join(images_dir, image_name)

    # Read the image
    image = cv2.imread(image_path)
    label = get_color(image)

    cv2.imshow(label, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()