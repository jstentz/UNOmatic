'''
This file is used to crop images from an already-existing UNO dataset
'''

# dictionary that converts their labels into my labels
label_conversion = {
  0:  0,
  1:  1,
  7:  2,
  8:  3,
  9:  4,
  10: 5,
  11: 6,
  12: 7,
  13: 8,
  14: 9,
  5: 10,
  4: 11,
  3: 12,
  6: 13,
  2: 14,
}

import os
import cv2 as cv

train_images_dir = 'UNO-dataset/train/images'
train_labels_dir = 'UNO-dataset/train/labels'

if __name__ == '__main__':

  sorted_images = sorted(os.listdir(train_images_dir))
  sorted_labels = sorted(os.listdir(train_labels_dir))

  for image_path, label_path in zip(sorted_images, sorted_labels):
    image_path = os.path.join(train_images_dir, image_path)
    label_path = os.path.join(train_labels_dir, label_path)

    # grab the first label 
    with open(label_path, 'r') as labelfile:
      labels = labelfile.readlines()

    # grab the first image
    image = cv.imread(image_path)


    for line in labels:
      label_data = line.strip().split(' ')
      x_center, y_center, width, height = map(float, label_data[1:])
      x_min = int((x_center - width / 2) * image.shape[1])
      y_min = int((y_center - height / 2) * image.shape[0])
      x_max = int((x_center + width / 2) * image.shape[1])
      y_max = int((y_center + height / 2) * image.shape[0])
      cv.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
      cv.putText(image, label_data[0], (x_min, y_min - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the image
    cv.imshow('Object Detection', image)
    cv.waitKey(0)
  cv.destroyAllWindows()

