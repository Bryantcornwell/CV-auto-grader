import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
from collections import defaultdict
import sys

ROI_Y_RATIO = 600/2200
BINARY_THRESHOLD = 200
HOUGH_RHO_RES = 1/4
HOUGH_THETA_RES = np.pi/(4*180)
HOUGH_THRESHOLD = 300
VERTICAL_SLOPE_TOL = 15
RHO_MERGE_TOL = 10


def load_and_preprocess(fname):
    gray = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    blurred_cropped = blurred[int(ROI_Y_RATIO*gray.shape[0]):, :]
    (T, threshinv) = cv2.threshold(blurred_cropped, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY_INV)
    return threshinv


def slope_close_to(theta, theta_0, tol=5):
    # theta - rad
    # theta_0 - deg
    # tol - deg
    # deg angles range from [-90,90], theta is converted to this scale
    theta_1 = (180/np.pi)*theta.copy()
    theta_1[theta_1 > 90] = theta_1[theta_1 > 90]-180
    return np.isclose(theta_1, theta_0, atol=tol)


# def merge_lines(lines, ro_tol=2):  # TODO
#     # lines: nx2 matrix, first column is ro and second column is theta
#     # parallel lines
#     # keeps the left most line
#     # returns a mask that works on sorted lines on ro

#     sorted_ros = lines[:, 0]

#     mask = np.zeros(lines.shape[0], dtype=np.bool8)

#     if len(lines) == 0:
#         return mask

#     mask[0] = True
#     prev_ro = sorted_ros[0]

#     for i, ro in enumerate(sorted_ros[1:]):
#         i += 1
#         if np.isclose(ro, prev_ro, atol=ro_tol):
#             continue
#         else:
#             mask[i] = True
#             prev_ro = ro

#     return mask

def merge_lines(lines, min_gap=10):
    # lines: nx2 matrix, first column is ro and second column is theta
    # parallel lines
    # keeps the left most line
    # returns a mask that works on sorted lines on ro

    sorted_ros = lines[:, 0]

    mask = np.zeros(lines.shape[0], dtype=np.bool8)

    if len(lines) == 0:
        return mask

    mask[0] = True
    prev_ro = sorted_ros[0]
    prev_i = 0

    for i, ro in enumerate(sorted_ros[1:], start=1):
        gap = abs(ro-prev_ro)
        if gap > min_gap:
            # print(prev_i, i, prev_ro, ro, gap)
            mask[prev_i] = True
            mask[i] = True
        prev_ro, prev_i = ro, i

    mask[i] = True  # last line
    return mask


def get_vertical_lines(img):
    lines = np.abs(cv2.HoughLines(img, HOUGH_RHO_RES, HOUGH_THETA_RES, HOUGH_THRESHOLD).squeeze())
    sorted_lines = lines[np.argsort(lines[:, 0])]
    vertical_lines = sorted_lines[slope_close_to(sorted_lines[:, 1], 0, tol=VERTICAL_SLOPE_TOL)]
    vertical_lines_merged = vertical_lines[merge_lines(vertical_lines, min_gap=RHO_MERGE_TOL)]
    return vertical_lines_merged


def patches(img, vertical_lines, stack, sub_stack, col=None):
    y1, y2 = 0, img.shape[0]

    if sub_stack == 0:
        x1 = 0 if stack == 0 else int(vertical_lines[22*stack-1, 0])
        x2 = int(vertical_lines[22*stack, 0])
    elif sub_stack == 1:
        x1 = int(vertical_lines[22*stack, 0])
        x2 = int(vertical_lines[22*stack+2, 0])
    else:
        if col is None:
            x1 = int(vertical_lines[22*stack+2, 0])
            x2 = int(vertical_lines[22*stack+21, 0])
        else:
            x1 = int(vertical_lines[22*stack+2+4*col, 0])
            x2 = int(vertical_lines[22*stack+2+4*col+3, 0])

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


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Wrong args. Correct Usage: python grade.py form.jpg output.txt')
        sys.exit(1)
    else:
        im_fname = sys.argv[1]
        output_fname = sys.argv[2]

        img = load_and_preprocess(im_fname)
        vertical_lines = get_vertical_lines(img)
        answers = defaultdict(list)
        for stack in [0, 1, 2]:
            for col in [0, 1, 2, 3, 4]:
                p = patches(img, vertical_lines, stack=stack, sub_stack=2, col=col)
                qnum_start = 29*stack
                filled, cc = segment(p, min_width=20, min_intensity=180)  # TODO
                print(stack, col, len(filled))
                for i, f in enumerate(filled):
                    if f == 1:
                        q_num = qnum_start + i + 1
                        answers[q_num].append(col)

        written = {}
        for stack in [0, 1, 2]:
            p = patches(img, vertical_lines, stack=stack, sub_stack=0)
            qnum_start = 29*stack
            options_col_p = patches(img, vertical_lines, stack=stack, sub_stack=2, col=0)
            filled, cc = segment(options_col_p, min_width=25, min_intensity=180)  # TODO

            for i, c in enumerate(set(np.unique(cc))-{0}):
                s = np.nonzero(cc == c)[0]
                avg_intensity = np.mean(p[s[0]-9:s[-1]+9, 5:-5])  # TODO
                q_num = qnum_start + i + 1
                written[q_num] = avg_intensity > 4  # TODO

        answers_str = [
            f'{i} {"".join([chr(ord("A")+a) for a in anss])}{" x" if written[i] else ""}' for i,
            anss in sorted(answers.items())]

        with open(output_fname, 'w') as f:
            f.write('\n'.join(answers_str))
