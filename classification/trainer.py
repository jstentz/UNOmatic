import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
import torchvision.models as models
from torch.utils.data import Dataset
import torchvision.transforms as T
from PIL import Image
import pandas as pd
import argparse
import wandb
import cv2 as cv
import numpy as np

# don't crop the image at all
img_size = (224, 224)
crop_size = (360, 360)

# card type
# num_labels = 15

# card color
num_labels = 5

# Get cpu, gpu or mps device for training.
device = (
  "cuda"
  if torch.cuda.is_available()
  else "mps"
  if torch.backends.mps.is_available()
  else "cpu"
)

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

class CsvImageDataset(Dataset):
  def __init__(self, csv_file, transform=None):
    self.data_frame = pd.read_csv(csv_file)
    self.transform = transform

  def __len__(self):
    return len(self.data_frame)

  def __getitem__(self, idx):
    if idx >= self.__len__(): raise IndexError()
    img_name = self.data_frame.loc[idx, "image"]
    image = Image.open(img_name).convert("RGB")  # Assuming RGB images
    label = self.data_frame.loc[idx, "label_idx"]
    label_name = self.data_frame.loc[idx, 'label']

    if self.transform:
      image = self.transform(image)

    # cv.imshow('test', np.array(image).transpose(1, 2, 0))
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return image, label, label_name

def get_data(batch_size):
    
    # transform all bottom images
    transform_img = T.Compose([
      T.ToTensor(), 
      T.CenterCrop(crop_size),  
      T.Resize(min(img_size[0], img_size[1]), antialias=True),  # Resize the smallest side to 256 pixels
      # these are the stats for the combined data
      T.Normalize(mean=[0.30910959716333414, 0.34933955945842665, 0.36630898255700345], std=[0.2647768747410307, 0.2591489816780959, 0.27447192038728097]), # Normalize each color dimension
      # TODO: I wonder if grayscale will actually help
      # T.Grayscale(), # for grayscale
      # T.Normalize(0.5, 0.2),
      ])

    # transform for top images
    # transform_img = T.Compose([
    #   T.ToTensor(), 
    #   T.CenterCrop(crop_size),  # Center crop to 256x256
    #   T.Resize(min(img_size[0], img_size[1]), antialias=True),  # Resize the smallest side to 256 pixels
    #   # TODO: should actually get the stats on the data to fill in these values
    #   T.Normalize(mean=[0.4367269728078398, 0.4910890673198487, 0.5517533993374586], std=[0.25033840810120556, 0.22346674305638875, 0.220343264947015]), # Normalize each color dimension
    #   # TODO: I wonder if grayscale will actually help
    #   # T.Grayscale(), # for grayscale
    #   # T.Normalize(0.5, 0.2),
    #   ])
    train_data = CsvImageDataset(
      csv_file='./data/images_train_color.csv',
      transform=transform_img,
    )
    test_data = CsvImageDataset(
      csv_file='./data/images_test_color.csv',
      transform=transform_img,
    )
    val_data = CsvImageDataset(
      csv_file='./data/images_valid_color.csv',
      transform=transform_img,
    )

    train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)
    val_dataloader = DataLoader(val_data, batch_size=batch_size)
    
    for X, y, _ in train_dataloader:
      print(f"Shape of X [B, C, H, W]: {X.shape}")
      print(f"Shape of y: {y.shape} {y.dtype}")
      break

    # print('here!')

    return train_dataloader, test_dataloader, val_dataloader

class NeuralNetwork(nn.Module):
  def __init__(self):
    super().__init__()
    self.flatten = nn.Flatten()
    # First layer input size must be the dimension of the image
    self.linear_relu_stack = nn.Sequential(
      nn.Linear(img_size[0] * img_size[1] * 3, 512),
      # nn.Linear(img_size[0] * img_size[1], 512), # for grayscale
      nn.ReLU(),
      nn.Linear(512, 512),
      nn.ReLU(),
      nn.Linear(512, num_labels)
    )

  def forward(self, x):
    x = self.flatten(x)
    logits = self.linear_relu_stack(x)
    return logits
    
# custom network for Q2.9
class ConvNetwork(nn.Module):
  def __init__(self):
    super().__init__()

    # params
    self.in_dims = 1
    self.num_filters1 = 8
    self.num_filters2 = 16
    self.linear_dims1 = 128
    self.linear_dims2 = 64


    # image_size x image_size x 3
    self.conv1 = nn.Conv2d(self.in_dims, self.num_filters1, kernel_size=(3,3), stride=1, padding=1)

    # image_size x image_size x 16
    self.act1 = nn.ReLU()

    # image_size x image_size x 16
    self.conv2 = nn.Conv2d(self.num_filters1, self.num_filters2, kernel_size=(3,3), stride=1, padding=1)
    
    # image_size x image_size x 32
    self.act2 = nn.ReLU()

    
    self.pool1 = nn.MaxPool2d(kernel_size=(2, 2), stride=2)

    # image_size / 2 x image_size / 2 x 32

    # TODO: I think this is prob too big, cuz that is a lot of params and for what
    self.flat = nn.Flatten()
    self.fc1 = nn.Linear((img_size[0] // 2) * (img_size[1] // 2)  * self.num_filters2, self.linear_dims1)
    self.act3 = nn.ReLU()

    # TODO: add dropout here?

    self.fc2 = nn.Linear(self.linear_dims1, self.linear_dims2)
    self.act4 = nn.ReLU()

    # self.dropout = nn.Dropout(p=0.2)

    self.fc3 = nn.Linear(self.linear_dims2, num_labels)

  def forward(self, x):
    # input 3x32x32, output 32x32x32
    x = self.act1(self.conv1(x))
    # input 32x32x32, output 32x32x32
    x = self.act2(self.conv2(x))
    # input 32x32x32, output 32x16x16
    x = self.pool1(x)
    # input 32x16x16, output 8192
    x = self.flat(x)
    # input 8192, output 512
    x = self.act3(self.fc1(x))

    x = self.act4(self.fc2(x))
    # input 512, output 10
    # x = self.dropout(x)

    x = self.fc3(x)
    return x
  
# class ResNetClassifier(nn.Module):
#   def __init__(self):
#     super().__init__()
#     self.resnet = models.resnet18(pretrained=True)
#     self.fc = nn.Linear(self.resnet.fc.out_features, num_labels)

def train_one_epoch(dataloader, model, loss_fn, optimizer, t):
  # need to use t to calculate the number of examples trained on so far 

  size = len(dataloader.dataset)
  batch_size = dataloader.batch_size
  model.train()

  # we've seen this number of examples from previous epochs
  examples_seen = t * size

  # loops over the data set a full time but does the updates based on the batch size
  # one epoch means you train on the full training dataset one time
  for batch, (X, y, _) in enumerate(dataloader):
    X, y = X.to(device), y.to(device)

    pred = model(X)
    loss = loss_fn(pred, y)

    loss.backward()
    optimizer.step()
    optimizer.zero_grad()

    loss = loss.item() / batch_size # compute average loss
    current = (batch + 1) * dataloader.batch_size

    # update and log info to wandb
    examples_seen += y.size(dim=0)
    # wandb.log({'loss': loss, 'examples_seen': examples_seen})
    

    # I think wandb.log will always increment x axis, so I'm not really sure how to make per example?
    # I just have to log everything I care about here and change what the x-axis is on the website I think

    if batch % 100 == 0:
      print(f"Train loss = {loss:>7f}  [{current:>5d}/{size:>5d}]")
        
def evaluate(dataloader, dataname, model, loss_fn, is_last_epoch):
  size = len(dataloader.dataset)
  num_batches = len(dataloader)
  model.eval()
  avg_loss, correct = 0, 0
  with torch.no_grad():
    for batch, (X, y, label_names) in enumerate(dataloader):
      X, y = X.to(device), y.to(device)
      pred = model(X)
      avg_loss += loss_fn(pred, y).item()
      correct += (pred.argmax(1) == y).type(torch.float).sum().item()

      # log some incorrect images
      incorrect_loc = torch.where(pred.argmax(1) != y)
      if is_last_epoch and incorrect_loc[0].size(dim=0) > 0:
        images = []
        for i, image in enumerate(X[incorrect_loc]):
          images.append(wandb.Image(image, caption=label_to_name[pred.argmax(1)[incorrect_loc][i]]))
        wandb.log({f'incorrect_examples_{dataname}': images})
          
      # log some example images
      # if batch == 0 and is_last_epoch:
      #   preds = [label_to_name(l) for l in pred.argmax(1)]
      #   images = []
      #   for i in range(len(X)):
      #     images.append(wandb.Image(X[i], caption=f'{preds[i]} / {label_names[i]}'))

      #     # log this as a list of wandb image objects
      #     # just for this question, turn off normalizing in the transform
      #   wandb.log({f'examples_{dataname}': images})
  avg_loss /= size
  correct /= size
  print(f"{dataname} accuracy = {(100*correct):>0.3f}%, {dataname} avg loss = {avg_loss:>8f}")
  return avg_loss, correct
    
def main(n_epochs, batch_size, learning_rate):
  print(f"Using {device} device")
  train_dataloader, test_dataloader, val_dataloader = get_data(batch_size)
  
  # model = NeuralNetwork().to(device)
  # model = ConvNetwork().to(device)
  # model = models.AlexNet(num_labels).to(device) # requires 224 x 224 images



  # load untrained resnet model
  model = models.resnet18(pretrained=True)

  # Freeze all layers
  # for param in model.parameters():
  #   param.requires_grad = False

  # Modify the last layer for your classification task
  num_ftrs = model.fc.in_features
  model.fc = nn.Sequential(
      nn.Linear(num_ftrs, 512),  # Add a linear layer
      nn.ReLU(),  # Add ReLU activation
      nn.Linear(512, num_labels)  # Output layer for 15 classes
  )

  model = model.to(device)

  print(model)

  loss_fn = nn.CrossEntropyLoss()
  optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
  # optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=0.0001, betas=(.9, .999), eps=1e-8)

  
  for t in range(n_epochs):
    print(f"\nEpoch {t+1}\n-------------------------------")
    train_one_epoch(train_dataloader, model, loss_fn, optimizer, t)
    train_loss, train_acc = evaluate(train_dataloader, "Train", model, loss_fn, t == n_epochs - 1)
    test_loss, test_acc = evaluate(test_dataloader, "Test", model, loss_fn, t == n_epochs - 1)
    # extra_test_loss, extra_test_acc = evaluate(extra_test_dataloader, "Extra Test", model, loss_fn, t == n_epochs - 1)
    val_loss, val_acc = evaluate(val_dataloader, "Val", model, loss_fn, t == n_epochs - 1)

    # don't need to log the epoch number since that should just happen automatically with step
    wandb.log({'train_loss': train_loss, 
                'train_acc': train_acc, 
                'test_loss': test_loss, 
                'test_acc': test_acc,
                'val_loss': val_loss,
                'val_acc': val_acc,
                'epoch': t})
  print("Done!")

  # Save the model
  torch.save(model, "model.pth")
  print("Saved PyTorch Model State to model.pth")

  # Load the model (just for the sake of example)
  # model = NeuralNetwork().to(device)
  # model.load_state_dict(torch.load("model.pth"))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'UNO Card Classifier')
  parser.add_argument('--n_epochs', default=5, help='The number of training epochs', type=int)
  parser.add_argument('--batch_size', default=8, help='The batch size', type=int)
  parser.add_argument('--learning_rate', default=1e-3, help='The learning rate for the optimizer', type=float)

  args = parser.parse_args()

  wandb.login()

  run = wandb.init(
    # Set the project where this run will be logged
    project='capstone',
    # Track hyperparameters and run metadata
    config={
      'learning_rate': args.learning_rate,
      'batch_size': args.batch_size,
      'epochs': args.n_epochs,
    },
  )

      
  main(args.n_epochs, args.batch_size, args.learning_rate)


'''
Notes:
 * try separating data before creating new data, make sure one of each image type is in training data
 * look into ResNet
 * experiment with different optimizers and batch sizes
 * https://pytorch.org/hub/pytorch_vision_resnet/
 * torchvision.models.resnet module
 * could remove the head or could just try to train the whole thing


 * SGD seems to work better
 * SGD:
  * best test acc seen on unfrozen network, pretrained=True, batch_size = 8, lr = 0.001 is 98.507% after 4 epochs
  * best test acc seen on frozen network, pretrained=True, batch_size = 8, lr = 0.001 is 82.5% after 6 epochs
  * best test acc seen on unfrozen network, pretrained=False, batch_size = 8, lr = 0.001 is ___% after _ epochs

if this fails, try with the pretrained model and fine tune it

need to fix the color classifier on the bottom camera
consider cropping it to ignore the black on the side for the bottom camera (don't do this for the top camera)


when to save the model: https://nicjac.dev/posts/identify-best-model/
'''