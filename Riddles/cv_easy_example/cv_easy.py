import cv2 as cv
import numpy as np
from collections import Counter


def reorder_shards(shredded_image, no_cols=12):
    batch_size = 64
    num_batches = shredded_image.shape[1] // batch_size
    batches = [
        shredded_image[:, i * batch_size : (i + 1) * batch_size, :]
        for i in range(num_batches)
    ]
    order = [0]
    j = 0
    curr_patch = 0
    while j < len(batches) - 1:
        mn, indx = 999999, 0
        for i in range(len(batches)):
            if i in order:
                continue
            diff = calc_hist_dist(batches[curr_patch], batches[i], no_cols)
            if diff < mn:
                mn = diff
                indx = i
        order.append(indx)
        curr_patch = indx
        j += 1
    return order, batches


def calc_hist_dist(batch1, batch2, no_cols):
    H1, H2 = calc_hist(batch1, no_cols, beign=False), calc_hist(batch2, no_cols)
    return np.linalg.norm(H1 - H2)


def calc_hist(
    batch,
    no_cols,
    beign=True,
):
    if beign:
        hist = cv.calcHist(
            [batch[:, :no_cols, :].flatten()], [0], None, [256], [0, 256]
        ).squeeze()
    else:
        hist = cv.calcHist(
            [batch[:, -no_cols:, :].flatten()], [0], None, [256], [0, 256]
        ).squeeze()

    return hist
