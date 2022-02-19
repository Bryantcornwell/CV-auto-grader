from houghLines import HoughLines, show_lines, slope_close_to, merge_lines

import matplotlib.pyplot as plt
import numpy as np
import cv2
import time
from collections import defaultdict
import sys

ROI_Y_RATIO = 600/2200
BINARY_THRESHOLD = 200

HOUGH_RHO_RES = 1/4
HOUGH_THETA_RES = np.pi/(4*180)
HOUGH_THRESHOLD = 300
VERTICAL_SLOPE_TOL = 15
RHO_MERGE_TOL = 10/1700

BOX_HEIGHT = 25  # needs to be a ratio (25/2200)
Y_GAP_BETWEEN_BOXES = 18  # needs to be a ratio (18/2200)
WRITTEN_AVG_INTENSITY_THRESH = 4
MIN_AVG_INTENSITY_SHADED_BOX = 160

ROT_HOUGH_RHO_RES = 1
ROT_HOUGH_THETA_RES = np.pi/(16*180)
ROT_HOUGH_THRESHOLD = 300


def preprocess_top(gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred_cropped = blurred[:int(ROI_Y_RATIO*gray.shape[0]), :]
    (T, threshinv) = cv2.threshold(blurred_cropped, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)

    sobel_kernel_h = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    pf_thresh_h = cv2.filter2D(src=threshinv, ddepth=-1, kernel=sobel_kernel_h)
    return pf_thresh_h


def get_deviation(img):
    lines, acc_grid, thetas, rhos = HoughLines(img, ROT_HOUGH_RHO_RES, ROT_HOUGH_THETA_RES, ROT_HOUGH_THRESHOLD)
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


def preprocess(gray, vertical_edges=False):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred_cropped = blurred[int(ROI_Y_RATIO*gray.shape[0]):, :]
    (T, threshinv) = cv2.threshold(blurred_cropped, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)

    if vertical_edges:
        sobel_kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]]).T
        pf = cv2.filter2D(src=threshinv, ddepth=-1, kernel=sobel_kernel)
        return pf
    return threshinv


def get_vertical_lines(img):
    lines, acc_grid, thetas, rhos = HoughLines(img, HOUGH_RHO_RES, HOUGH_THETA_RES, HOUGH_THRESHOLD)
    sorted_lines = lines[np.argsort(lines[:, 0])]
    vertical_lines = sorted_lines[slope_close_to(sorted_lines[:, 1], 0, tol=VERTICAL_SLOPE_TOL)]
    vertical_lines_merged = vertical_lines[merge_lines(vertical_lines, min_gap=int(RHO_MERGE_TOL*img.shape[1]))]
    return vertical_lines_merged


def patches(img, vertical_lines, stack, sub_stack, col=None):
    y1, y2 = 0, img.shape[0]

    if sub_stack == 0:
        x1 = 0 if stack == 0 else int(vertical_lines[12*stack-1, 0])
        x2 = int(vertical_lines[12*stack, 0])
    elif sub_stack == 1:
        x1 = int(vertical_lines[12*stack, 0])
        x2 = int(vertical_lines[12*stack+2, 0])
    else:
        if col is None:
            x1 = int(vertical_lines[12*stack+2, 0])
            x2 = int(vertical_lines[12*stack+11, 0])
        else:
            x1 = int(vertical_lines[12*stack+2+2*col, 0])
            x2 = int(vertical_lines[12*stack+2+2*col+1, 0])

    # print(x1,x2,y1,y2)
    return img[y1:y2, x1:x2]


def connected_components(data):
    labels = np.zeros_like(data).astype(np.uint64)
    n = 0
    for i in range(len(data[1:])):
        left = data[i-1]
        if data[i] != 0:
            if left == 0:
                n += 1
                labels[i] = n
            else:
                labels[i] = n

    return labels


def segment(p, min_width, min_intensity):
    '''
    '''
    data = np.sum(p, axis=1)/p.shape[1]
    data_thresh = data.copy()
    data_thresh[data_thresh < 20] = 0
    cc = connected_components(data_thresh)

    # remove components with width less than min_width
    labels = set(np.unique(cc))-{0}
    for c in labels:
        if cc[cc == c].shape[0] < min_width:
            cc[cc == c] = 0

    labels = set(np.unique(cc))-{0}

    # calculate average intensity of each component
    avg_intensity = np.zeros(len(labels))
    for i, c in enumerate(labels):
        avg_intensity[i] = np.mean(data_thresh[cc == c])

    # map components with intensity less than min_intensity as 0 (unfilled) otherwise 1 (filled)
    return [1 if i > min_intensity else 0 for i in avg_intensity], cc


def get_answers(img, vertical_lines):
    answers = defaultdict(list)
    for stack in [0, 1, 2]:  # iterating over 3 stacks
        for col in [0, 1, 2, 3, 4]:  # iterating over A, B, C, D, E columns
            p = patches(img, vertical_lines, stack=stack, sub_stack=2, col=col)
            qnum_start = 29*stack
            filled, cc = segment(p, min_width=BOX_HEIGHT, min_intensity=MIN_AVG_INTENSITY_SHADED_BOX)
            # print(stack, col, len(filled))
            for i, f in enumerate(filled):
                if f == 1:  # if the box is shaded, f is 1, 0 otherwise
                    q_num = qnum_start + i + 1
                    answers[q_num].append(col)
    return answers


def get_written(img, vertical_lines):
    '''
    '''
    written = {}
    for stack in [0, 1, 2]:
        p = patches(img, vertical_lines, stack=stack, sub_stack=0)
        qnum_start = 29*stack
        options_col_p = patches(img, vertical_lines, stack=stack, sub_stack=2, col=0)
        filled, cc = segment(options_col_p, min_width=BOX_HEIGHT, min_intensity=MIN_AVG_INTENSITY_SHADED_BOX)

        for i, c in enumerate(set(np.unique(cc))-{0}):
            s = np.nonzero(cc == c)[0]  # indexes (y) of pixels from start to end of the box (in vertical direction)

            # extend the y boundaries to include half the gap between the boxes, both up and down
            margin = int(Y_GAP_BETWEEN_BOXES/2)
            y1, y2 = s[0]-margin, s[-1]+margin

            # reduce the boundaries horizontally to exclude box boudaries that sometimes leak into this patch.
            x1, x2 = 5, -5

            avg_intensity = np.mean(p[y1:y2, x1:x2])
            q_num = qnum_start + i + 1
            written[q_num] = avg_intensity > WRITTEN_AVG_INTENSITY_THRESH
    return written


def answer_str(qnum, answers, written):
    return f'{qnum} {"".join([chr(ord("A")+a) for a in answers])}{" x" if written[qnum] else ""}'


def write_to_file(answers, written, output_fname=None):
    answers_str = [answer_str(i, anss, written) for i, anss in sorted(answers.items())]

    if output_fname:
        with open(output_fname, 'w') as f:
            f.write('\n'.join(answers_str))
    return answers_str


def compare_answers(groundtruth_file, answers_strs):
    with open('../test-images/a-30_groundtruth.txt') as f:
        groundturth = f.read().split('\n')
    return groundturth == answers_strs


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Wrong args. Correct Usage: python grade.py form.jpg output.txt')
        sys.exit(1)

    im_fname = sys.argv[1]
    output_fname = sys.argv[2]

    img = cv2.imread(im_fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_processed = preprocess(gray)
    vlines = get_vertical_lines(img_processed)
    if vlines.shape[0] != 36:
        raise Exception(f'found {vlines.shape[0]} vertical lines, expecting 36.')

    answers = get_answers(img_processed, vlines)
    written = get_written(img_processed, vlines)
    answers_strs = write_to_file(answers, written, output_fname)
