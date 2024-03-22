'''
Loops through images and makes sure they are labeled correctly.
'''

import cv2 as cv

data_path_in = './top_data/all_images_base.csv'
data_path_out = './top_data/all_images_base_fixed.csv'

data_in = open(data_path_in, 'r')
data_out = open(data_path_out, 'w')

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


lines = data_in.readlines()

# write the header
data_out.write(lines[0])

# loop over the rest of the lines
i = 0
for line in lines[1:]:
  path, label_name, label_idx = line.split(',')
  image = cv.imread(path)

  image = cv.flip(image, -1)

  cv.namedWindow('image')        # Create a named window
  cv.moveWindow('image', 1100,100)  # Move it to (40,30)
  cv.putText(image, label_name, (image.shape[0] // 2 - 50, image.shape[1] // 2), cv.FONT_HERSHEY_SIMPLEX , 2, (255, 255, 255), 2)
  cv.imshow('image', image)
  cv.waitKey(1)
  # cv.destroyAllWindows()

  label_idx = int(label_idx[:-1])
  new_label = input(f'{i}/{len(lines)} New label: ')
  
  i += 1

  while new_label != '' and new_label not in label_to_name:
    new_label = input(f'Previous label: {label_name}; New label: ')

  if new_label == '':
    data_out.write(line)
  else:
    new_label_idx = label_to_name.index(new_label)
    data_out.write(f'{path},{new_label},{new_label_idx}\n')
cv.destroyAllWindows()



data_in.close()
data_out.close()
