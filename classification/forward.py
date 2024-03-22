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

device = (
  "cuda"
  if torch.cuda.is_available()
  else "mps"
  if torch.backends.mps.is_available()
  else "cpu"
)


# TODO: this should be in a shared location somehow
img_size = (224, 224)
crop_size = (224, 224)
transform_img = T.Compose([
      # T.ToTensor(), 
      T.CenterCrop(crop_size),  # Center crop to 256x256
      T.Resize(min(img_size[0], img_size[1]), antialias=True),  # Resize the smallest side to 256 pixels
      T.Normalize(mean=[0.4367269728078398, 0.4910890673198487, 0.5517533993374586], std=[0.25033840810120556, 0.22346674305638875, 0.220343264947015]), # Normalize each color dimension
      ])

def get_model(model_path):
  model = torch.load(model_path)
  model.eval()
  return model

def forward(model, image_path):
  # load the image
  image = Image.open(image_path).convert("RGB")

  image = T.ToTensor()(image).to(device)
  image = torch.flip(image, [1, 2])
  image = transform_img(image).unsqueeze(0)

  # run the forward pass
  with torch.no_grad():
    label_idx = model(image).argmax(1).item()
    result = label_to_name[label_idx]
  return result
