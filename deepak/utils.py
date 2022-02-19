import matplotlib.pyplot as plt
import numpy as np
import cv2
import time
from collections import defaultdict

from houghLines import HoughLines, slope_close_to


def preprocess_top(gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred_cropped = blurred[:int(ROI_Y_RATIO*noisy_gray.shape[0]), :]
    (T, threshinv) = cv2.threshold(blurred_cropped, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)

    sobel_kernel_h = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    pf_thresh_h = cv2.filter2D(src=threshinv, ddepth=-1, kernel=sobel_kernel_h)
    return pf_thresh_h


def get_deviation(img):
    lines, acc_grid, thetas, rhos = HoughLines(img, 1, np.pi/(16*180), 300)
    sorted_lines = lines[np.argsort(lines[:, 0])]
    horizontal_lines = sorted_lines[slope_close_to(sorted_lines[:, 1], 90, tol=VERTICAL_SLOPE_TOL)]
    return 90-np.mean((180/np.pi)*horizontal_lines[:, 1])


def rotate(gray, theta):
    h, w = gray.shape
    M = cv2.getRotationMatrix2D((w/2, h/2), theta, 1)
    shifted = cv2.warpAffine(gray, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
    return shifted


def correct_tilt(gray):
    img_pr = preprocess_top(gray)
    deviation = get_deviation(img_pr)
    print('detected deviation:', deviation)

    gray_rot = rotate(gray, -deviation)
    return gray_rot
