'''
This file is used to crop images from an already-existing UNO dataset
'''

import os
import cv2 as cv
import numpy as np

# just exit to prevent me from being dumb and overwriting my data
exit()

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

label_to_name = [
  '0',
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  'skip',
  'reverse',
  'plus2',
  'wild',
  'plus4'
]

set_type = 'train'
train_images_dir = f'UNO-dataset/{set_type}/images'
train_labels_dir = f'UNO-dataset/{set_type}/labels'

# how many pixels of buffer when cropping
buffer = 5

# add header to csv file we're recording
images_dir = f'./data/images'
csv_file_name = f'./data/images_{set_type}.csv'
csv_file = open(csv_file_name, 'w')
csv_file.write('image,label,label_idx\n')

sorted_images = sorted(os.listdir(train_images_dir))
sorted_labels = sorted(os.listdir(train_labels_dir))

# count the number of images we've created

# TODO: change this to count + 1 from previous iteration
count = 0

for image_path, label_path in zip(sorted_images, sorted_labels):
  image_path = os.path.join(train_images_dir, image_path)
  label_path = os.path.join(train_labels_dir, label_path)

  # grab the labels
  with open(label_path, 'r') as labelfile:
    labels = labelfile.readlines()

  # grab the image
  image = cv.imread(image_path)

  for line in labels:
    label_data = line.strip().split(' ')
    x_center, y_center, width, height = map(float, label_data[1:])
    x_min = int((x_center - width / 2) * image.shape[1])
    y_min = int((y_center - height / 2) * image.shape[0])
    x_max = int((x_center + width / 2) * image.shape[1])
    y_max = int((y_center + height / 2) * image.shape[0])

    # NOTE: if I only want to save the top image (the most visible one), then move the file saving to after the for loop? I think?
    cropped_img = image[max(y_min-buffer, 0):min(y_max+buffer, image.shape[0]-1), 
                        max(x_min-buffer, 0):min(x_max+buffer, image.shape[1]-1)]
    label_idx = label_conversion[int(label_data[0])]
    label = label_to_name[label_idx]

    # save the image to the training set
    path = os.path.join(images_dir, f'img_{count}.jpg')
    print(count)
    cv.imwrite(path, cropped_img)

    # add to the csv file
    csv_file.write(f'{path},{label},{label_idx}\n')

    # update counter for image names
    count += 1

    # cv.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
    # cv.putText(image, label_data[0], (x_min, y_min - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

csv_file.close()