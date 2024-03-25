'''
Runs one forward pass on an image and displays predicted class.

'''

import torch
import torchvision.transforms as T
import numpy as np
from uno.utils import card_from_classification
from uno.card import Card


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
      T.CenterCrop(crop_size_both),  
      T.Resize(min(img_size_both[0], img_size_both[1]), antialias=True), 
      T.Normalize(mean=[0.30910959716333414, 0.34933955945842665, 0.36630898255700345], std=[0.2647768747410307, 0.2591489816780959, 0.27447192038728097]), # Normalize each color dimension
      ])

img_size_top = (224, 224)
crop_size_top = (224, 224)
transform_img_top = T.Compose([
      T.CenterCrop(crop_size_top),  
      T.Resize(min(img_size_top[0], img_size_top[1]), antialias=True), 
      T.Normalize(mean=[0.4367269728078398, 0.4910890673198487, 0.5517533993374586], std=[0.25033840810120556, 0.22346674305638875, 0.220343264947015]), # Normalize each color dimension
      ])

img_size_bot = (224, 224)
crop_size_bot = (224, 224)
transform_img_bot = T.Compose([
      T.CenterCrop(crop_size_bot),  
      T.Resize(min(img_size_bot[0], img_size_bot[1]), antialias=True), 
      T.Normalize(mean=[0.13969138640706788, 0.17492677541873866, 0.15068305555046435], std=[0.16648552270709308, 0.18993078271824135, 0.17560376684656742]), # Normalize each color dimension
      ])


def init_model(model_path: str, on_pi: bool):
  if on_pi:
    model = torch.load(model_path, map_location=torch.device('cpu')).to(device)
  else:
    model = torch.load(model_path).to(device)
  model.eval()
  return model

def get_card(card_model, color_model, image: np.ndarray, is_top_cam: bool = True) -> Card:
  # convert to pytorch tensor
  image = image.transpose(2,0,1)
  image = torch.from_numpy(image).to(device)
  # flip the top camera images to match training data
  if is_top_cam:
    image = torch.flip(image, [1, 2])
    image = transform_img_top(image).unsqueeze(0)
  else:
    image = transform_img_bot(image).unsqueeze(0)

  # run the forward pass to get card type
  with torch.no_grad():
    card_label_idx = card_model(image).argmax(1).item()
    color_label_idx = color_model(image).argmax(1).item()

  return card_label_idx, color_label_idx
