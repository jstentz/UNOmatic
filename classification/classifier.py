import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.utils.data import Dataset
import torchvision.transforms as T
from PIL import Image
import pandas as pd
import argparse
import wandb

img_size = (64,64)
num_labels = 15

# Get cpu, gpu or mps device for training.
device = (
  "cuda"
  if torch.cuda.is_available()
  else "mps"
  if torch.backends.mps.is_available()
  else "cpu"
)

# def label_to_name(label):
#   return ['parrot', 'narwhal', 'axolotl'][label]

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

    return image, label, label_name

def get_data(batch_size):
    transform_img = T.Compose([
      T.ToTensor(), 
      T.Resize(min(img_size[0], img_size[1]), antialias=True),  # Resize the smallest side to 256 pixels
      T.CenterCrop(img_size),  # Center crop to 256x256
      T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), # Normalize each color dimension
      # T.Grayscale() # for grayscale
      ])
    train_data = CsvImageDataset(
      csv_file='./data/images_train.csv',
      transform=transform_img,
    )
    test_data = CsvImageDataset(
      csv_file='./data/images_test.csv',
      transform=transform_img,
    )
    val_data = CsvImageDataset(
      csv_file='./data/images_valid.csv',
      transform=transform_img,
    )

    train_dataloader = DataLoader(train_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)
    val_dataloader = DataLoader(val_data, batch_size=batch_size)

    for X, y, _ in train_dataloader:
      print(f"Shape of X [B, C, H, W]: {X.shape}")
      print(f"Shape of y: {y.shape} {y.dtype}")
      break
    
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
    self.conv1 = nn.Conv2d(3, 16, kernel_size=(3,3), stride=1, padding=1)
    self.act1 = nn.ReLU()

    self.conv2 = nn.Conv2d(16, 32, kernel_size=(3,3), stride=1, padding=1)
    self.act2 = nn.ReLU()
    self.pool2 = nn.MaxPool2d(kernel_size=(2, 2))

    self.flat = nn.Flatten()

    self.fc3 = nn.Linear(524288, 512)
    self.act3 = nn.ReLU()

    self.fc4 = nn.Linear(512, 10)

  def forward(self, x):
    # input 3x32x32, output 32x32x32
    x = self.act1(self.conv1(x))
    # input 32x32x32, output 32x32x32
    x = self.act2(self.conv2(x))
    # input 32x32x32, output 32x16x16
    x = self.pool2(x)
    # input 32x16x16, output 8192
    x = self.flat(x)
    # input 8192, output 512
    x = self.act3(self.fc3(x))
    # input 512, output 10
    x = self.fc4(x)
    return x

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

    if batch % 10 == 0:
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
  print(f"{dataname} accuracy = {(100*correct):>0.1f}%, {dataname} avg loss = {avg_loss:>8f}")
  return avg_loss, correct
    
def main(n_epochs, batch_size, learning_rate):
  print(f"Using {device} device")
  train_dataloader, test_dataloader, val_dataloader = get_data(batch_size)
  
  model = NeuralNetwork().to(device)
  # model = ConvNetwork().to(device)
  print(model)
  loss_fn = nn.CrossEntropyLoss()
  optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
  # optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)

  
  for t in range(n_epochs):
    print(f"\nEpoch {t+1}\n-------------------------------")
    train_one_epoch(train_dataloader, model, loss_fn, optimizer, t)
    train_loss, train_acc = evaluate(train_dataloader, "Train", model, loss_fn, t == n_epochs - 1)
    test_loss, test_acc = evaluate(test_dataloader, "Test", model, loss_fn, t == n_epochs - 1)
    val_loss, val_acc = evaluate(val_dataloader, "Val", model, loss_fn, t == n_epochs - 1)

    # don't need to log the epoch number since that should just happen automatically with step
    # wandb.log({'train_loss': train_loss, 
    #             'train_acc': train_acc, 
    #             'test_loss': test_loss, 
    #             'test_acc': test_acc,
    #             'val_loss': val_loss,
    #             'val_acc': val_acc,
    #             'epoch': t})
  print("Done!")

  # Save the model
  torch.save(model.state_dict(), "model.pth")
  print("Saved PyTorch Model State to model.pth")

  # Load the model (just for the sake of example)
  model = NeuralNetwork().to(device)
  model.load_state_dict(torch.load("model.pth"))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description = 'UNO Card Classifier')
  parser.add_argument('--n_epochs', default=5, help='The number of training epochs', type=int)
  parser.add_argument('--batch_size', default=8, help='The batch size', type=int)
  parser.add_argument('--learning_rate', default=1e-3, help='The learning rate for the optimizer', type=float)

  args = parser.parse_args()

  # wandb.login()

  # run = wandb.init(
  #   # Set the project where this run will be logged
  #   project='capstone',
  #   # Track hyperparameters and run metadata
  #   config={
  #     'learning_rate': args.learning_rate,
  #     'batch_size': args.batch_size,
  #     'epochs': args.n_epochs,
  #   },
  # )

      
  main(args.n_epochs, args.batch_size, args.learning_rate)
