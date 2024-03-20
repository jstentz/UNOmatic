import cv2 as cv
import numpy as np

# zooms in at a point
def zoom_at(img, zoom, coord=None):
  cy, cx = [ i/2 for i in img.shape[:-1] ] if coord is None else coord[::-1]
  rot_mat = cv.getRotationMatrix2D((cx,cy), 0, zoom)
  result = cv.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv.INTER_LINEAR)
  return result

if __name__ == '__main__':
  image = cv.imread('./top_data/images_modified/top_1_0.jpg')

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