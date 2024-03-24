'''
Runs one forward pass on an image and displays predicted class.

'''

# TODO: these should be separated from the trainer
from trainer import ConvNetwork
import torch
from PIL import Image
import torchvision.transforms as T
import cv2 as cv
import numpy as np

# change these for a different model / different image to classify
image_name = './top_data/images_modified/top_278_140.jpg'
# image_name = './top_data/test_image.jpg'
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

label_to_color = [
  'red',
  'yellow',
  'green',
  'blue',
  'none'
]

device = (
  "cuda"
  if torch.cuda.is_available()
  else "mps"
  if torch.backends.mps.is_available()
  else "cpu"
)


# TODO: this should be in a shared location somehow
img_size_both = (224, 224)
crop_size_both = (360, 360)
transform_img_both = T.Compose([
      # T.ToTensor(), 
      T.CenterCrop(crop_size_both),  # Center crop to 256x256
      T.Resize(min(img_size_both[0], img_size_both[1]), antialias=True),  # Resize the smallest side to 256 pixels
      T.Normalize(mean=[0.30910959716333414, 0.34933955945842665, 0.36630898255700345], std=[0.2647768747410307, 0.2591489816780959, 0.27447192038728097]), # Normalize each color dimension
      ])

<<<<<<< Updated upstream
img_size_top = (224, 224)
crop_size_top = (224, 224)
transform_img_top = T.Compose([
      # T.ToTensor(), 
      T.CenterCrop(crop_size_top),  # Center crop to 256x256
      T.Resize(min(img_size_top[0], img_size_top[1]), antialias=True),  # Resize the smallest side to 256 pixels
      T.Normalize(mean=[0.4367269728078398, 0.4910890673198487, 0.5517533993374586], std=[0.25033840810120556, 0.22346674305638875, 0.220343264947015]), # Normalize each color dimension
      ])

img_size_bot = (224, 224)
crop_size_bot = (224, 224)
transform_img_bot = T.Compose([
      # T.ToTensor(), 
      T.CenterCrop(crop_size_bot),  # Center crop to 256x256
      T.Resize(min(img_size_bot[0], img_size_bot[1]), antialias=True),  # Resize the smallest side to 256 pixels
      T.Normalize(mean=[0.13969138640706788, 0.17492677541873866, 0.15068305555046435], std=[0.16648552270709308, 0.18993078271824135, 0.17560376684656742]), # Normalize each color dimension
      ])


def init_model(model_path: str, on_pi: bool):
  if on_pi:
    model = torch.load(model_path, map_location=torch.device('cpu'))
  else:
    model = torch.load(model_path)
  model.eval()
  return model

def get_card(card_model, color_model, is_top: bool, image: np.ndarray):
  # convert to pytorch tensor
  image = image.transpose(2,0,1)
  image = torch.from_numpy(image)
  # flip the top camera images to match training data
  if is_top:
    image = torch.flip(image, [1, 2])
    image = transform_img_top(image).unsqueeze(0)
  else:
    image = transform_img_bot(image).unsqueeze(0)

  # run the forward pass to get card type
  with torch.no_grad():
    card_label_idx = card_model(image).argmax(1).item()
    card_label = label_to_name[card_label_idx]

    # TODO: only run color model if non-wild / non-plus4
    color_label_idx = color_model(image).argmax(1).item()
    color_label = label_to_color[color_label_idx]

  return color_label, card_label
