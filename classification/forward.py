'''
Runs one forward pass on an image and displays predicted class.

'''

# TODO: these should be separated from the trainer
from trainer import ConvNetwork
import torch
from PIL import Image
import torchvision.transforms as T
import cv2 as cv

# change these for a different model / different image to classify
image_name = './top_data/images_modified/top_278_140.jpg'
model_path = 'model.pth'

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

device = (
  "cuda"
  if torch.cuda.is_available()
  else "mps"
  if torch.backends.mps.is_available()
  else "cpu"
)


# TODO: this should be in a shared location somehow
img_size = (128, 128)
crop_size = (128, 128)
transform_img = T.Compose([
      T.ToTensor(), 
      T.CenterCrop(crop_size),  # Center crop to 256x256
      T.Resize(min(img_size[0], img_size[1]), antialias=True),  # Resize the smallest side to 256 pixels
      # T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), # Normalize each color dimension
      # T.Grayscale() # for grayscale
      ])

if __name__ == '__main__':
  # create the model
  model = ConvNetwork()
  model.load_state_dict(state_dict=torch.load(model_path))
  model.eval()

  # load the image
  image = Image.open(image_name).convert("RGB")

  # transform the image (need to add a dimension on the outside bc of batch size)
  image = transform_img(image).unsqueeze(0)


  # run the forward pass
  with torch.no_grad():
    label_idx = model(image).argmax(1).item()
    print(label_to_name[label_idx])

  # TODO: fix the coloring on this
  cv.imshow('Image', image.numpy()[0].transpose(1, 2, 0)[:, :, ::-1])
  cv.waitKey(0)
  cv.destroyAllWindows()