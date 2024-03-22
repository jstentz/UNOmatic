import cv2 as cv
import numpy as np

import matplotlib.pyplot as plt
import matplotlib
import skimage
import skimage.measure
import skimage.color
import skimage.restoration
import skimage.filters
import skimage.morphology
import skimage.segmentation

# takes a color image
# returns a list of bounding boxes and black_and_white image
def findLetters(image):
  bboxes = []
  # print(bw.shape)
  # insert processing in here
  # one idea estimate noise ->denoise -> greyscale -> threshold -> morphology -> label -> skip small boxes 
  # this can be 10 to 15 lines of code using skimage functions

  bw = skimage.color.rgb2gray(image)
  image = skimage.restoration.denoise_tv_chambolle(bw)
  filter = skimage.filters.threshold_minimum(bw)
  bw = bw > filter
  
  # dilate to accentuate features
  selem = skimage.morphology.disk(radius=3)
  bw = np.logical_not(skimage.morphology.binary_dilation(np.logical_not(bw), selem))
  bw = skimage.morphology.opening(bw)
  labels = skimage.measure.label(bw, background=1)
  regions = skimage.measure.regionprops(labels, intensity_image=bw, cache=True)

  total_area = 0
  for region in regions:
    total_area += region.area
  avg_area = total_area / len(regions)

  for region in regions:
    if region.area > avg_area / 2:
      bboxes.append(region.bbox)
  return bboxes, bw

# zooms in at a point
def zoom_at(img, zoom, coord=None):
  cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
  rot_mat = cv.getRotationMatrix2D((cx,cy), 0, zoom)
  result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)
  return result

if __name__ == '__main__':
  image_path = './top_data/images_modified/top_1_0.jpg'
  image = cv.imread(image_path)

  # image_ski = skimage.img_as_float(skimage.io.imread(image_path))
  # bboxes, bw = findLetters(image_ski)

  # plt.figure()
  # plt.imshow(bw, cmap='gray')
  # for bbox in bboxes:
  #   minr, minc, maxr, maxc = bbox
  #   rect = matplotlib.patches.Rectangle((minc, minr), maxc - minc, maxr - minr,
  #                           fill=False, edgecolor='red', linewidth=2)
  #   plt.gca().add_patch(rect)
  # plt.savefig(f'{image_path[:-4]}_processed.jpg')

  # crop the image
  image = zoom_at(image, zoom=4, coord=None)

  gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

  cv.imshow('gray', gray)
  cv.waitKey(0)
  cv.destroyAllWindows()

  # find the maximum pixel in the image
  max_intensity = np.max(gray)

  percentage = .7

  # here, thresholded stores the mask applied, which is exactly what we want
  threshold = percentage * max_intensity
  _, thresholded = cv.threshold(gray, threshold, 255, cv.THRESH_BINARY)

  cv.imshow('thresholded', thresholded)
  cv.waitKey(0)
  cv.destroyAllWindows()

  edged = cv.Canny(thresholded, 30, 200)

  contours, hierarchy = cv.findContours(edged,  
    cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) 

  cv.imshow('Edges', edged)
  cv.waitKey(0)
  cv.destroyAllWindows()

  print("Number of Contours found = " + str(len(contours)))
  
  # -1 signifies drawing all contours 
  cv.drawContours(image, contours, -1, (0, 255, 0), 3) 

  cv.imshow('contours', image)
  cv.waitKey(0)
  cv.destroyAllWindows()

'''
Ideas:
 * Threshold based on the brightest pixel in the image (maybe some percentage of it?)
 * Use a mask to keep only the white parts of the image (again this could be done with percentage of brightest part)

'''