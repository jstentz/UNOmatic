import random

data_file_path = './top_data/all_images_modified.csv'
train_out_path = './top_data/images_train.csv'
valid_out_path = './top_data/images_valid.csv'
test_out_path = './top_data/images_test.csv'

valid_portion = 0.1
test_portion = 0.1
train_portion = 1 - valid_portion - test_portion

with open(data_file_path, 'r') as data_file:
  lines = data_file.readlines()
  first_line = lines[0]
  lines = lines[1:]
  random.shuffle(lines)

  train_count = int(train_portion * len(lines))
  valid_count = int(valid_portion * len(lines))
  test_count = int(test_portion * len(lines))

  train_set = lines[:train_count]
  valid_set = lines[train_count:valid_count + train_count]
  test_set = lines[train_count + valid_count:]


with open(train_out_path, 'w') as train_out:
  train_out.write(first_line)
  train_out.writelines(train_set)

with open(valid_out_path, 'w') as valid_out:
  valid_out.write(first_line)
  valid_out.writelines(valid_set)

with open(test_out_path, 'w') as test_out:
  test_out.write(first_line)
  test_out.writelines(test_set)