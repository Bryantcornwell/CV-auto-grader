import numpy as np
# import matplotlib.pyplot as plt


def HoughLines(img, rho_res, theta_res, votes_threshold):
    # img - binary image, where edges are 1 and others are 0
    # rho_res - resolution of rho for the accumulator grid
    # theta_res - resolution of theta for the accumulator grid in radians
    # votes_threshold - return lines that have more than votes_threshold votes

    # grid thetas ranging from 0 to pi (pi exclusive)
    thetas = np.arange(0, np.pi, theta_res)
    thetas_idxs = np.arange(0, len(thetas))

    # grid rhos ranging from -diag to diag where diag = sqrt(w^2+h^2)
    diag = np.ceil(np.linalg.norm(img.shape[:2]))
    print('diag', diag)
    rhos = np.arange(-diag, diag+rho_res, rho_res)

    # create accumulator grid
    num_thetas, num_rhos = thetas.shape[0], rhos.shape[0]
    acc_grid = np.zeros((num_rhos, num_thetas), dtype=np.uint64)

    cos_thetas = np.cos(thetas)
    sin_thetas = np.sin(thetas)

    # for each edge pixel (pixel == 1)
    for y, x in zip(*np.nonzero(img)):
        # calculate rho for each theta and update accumulator grid
        rho = x*cos_thetas + y*sin_thetas
        rho_idxs = np.digitize(rho, bins=rhos)-1
        acc_grid[rho_idxs, thetas_idxs] += 1

    # apply threshold
    rho_idxs, theta_idxs = np.nonzero(acc_grid > votes_threshold)
    lines = np.array(list(zip(rhos[rho_idxs], thetas[theta_idxs])))
    return lines, acc_grid, thetas, rhos

# lines, acc_grid, thetas, rhos = HoughLines(pf, 1/4, np.pi/(4*180), 200)
# threshinv.shape, acc_grid.shape, len(lines)


# def show_lines(img, lines, title='img'):
#     fig, axes = plt.subplots(figsize=(10, 16))
#     axes.imshow(img, cmap='gray')
#     d = max(img.shape)
#     for rho, theta in lines:
#         dx = np.cos(theta)
#         dy = np.sin(theta)
#         x0 = dx*rho
#         y0 = dy*rho
#         # (x0,y0) is a point on the line
#         # print(x0,y0)
#         x1 = int(x0 + d*(-dy))
#         y1 = int(y0 + d*(dx))
#         x2 = int(x0 - d*(-dy))
#         y2 = int(y0 - d*(dx))
#         # print(x1,y1,x2,y2)
#         axes.plot([x1, x2], [y1, y2], '-.', color='red', alpha=0.7)
#     axes.set_xlim(0, img.shape[1])  # x is cols
#     axes.set_ylim(img.shape[0], 0)  # y is rows
#     axes.set_title(title)


def slope_close_to(theta, theta_0, tol=5):
    # theta - rad
    # theta_0 - deg
    # tol - deg
    # deg angles range from [-90,90], theta is converted to this scale
    theta_1 = (180/np.pi)*theta.copy()
    theta_1[theta_1 > 90] = 180-theta_1[theta_1 > 90]
    return np.isclose(theta_1, theta_0, atol=tol)


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
