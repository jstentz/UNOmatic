import os

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

image_path = './top_data/images/'

infile_path = './top_data/top_data_labels.csv'
outfile_path = 'data_labels.csv'

infile = open(infile_path, 'r')
outfile = open(outfile_path, 'w')

# write the header
outfile.write('image,label,label_idx\n')

for line in infile.readlines():
  path, label_idx = line.split(',')
  label_idx = int(label_idx)
  # print(image_path, path.removeprefix('top_data/'))
  new_path = os.path.join(image_path, path.removeprefix('top_data/'))
  label = label_to_name[label_idx]

  outfile.write(f'{new_path},{label},{label_idx}\n')


infile.close()
outfile.close()

