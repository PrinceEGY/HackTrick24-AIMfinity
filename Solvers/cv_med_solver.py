import cv2 as cv
import numpy as np


def find_and_fill(
    source, template, threshold=0.5, auto_scale=(0.1, 1, 0.05), fill_size=5
):
    results = find_tepmlates(source, template, threshold, auto_scale)
    if len(results) == 0:
        return source
    result = max(results, key=lambda x: x[0])
    return np.array(content_aware_fill(source, result[1], fill_size)).tolist()


def find_tepmlates(source, template, threshold=0.5, auto_scale=(0.05, 0.5, 0.01)):
    tw, th = template.shape[1], template.shape[0]
    sw, sh = source.shape[1], source.shape[0]

    gray_source = cv.cvtColor(source, cv.COLOR_BGR2GRAY)
    gray_template = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

    results = []

    scale_min = auto_scale[0]
    scale_max = auto_scale[1]
    scale_step = auto_scale[2]
    for scale in np.arange(scale_min, scale_max, scale_step):
        resized_template = cv.resize(
            gray_template,
            (int(tw * scale), int(th * scale)),
            interpolation=cv.INTER_CUBIC,
        )

        result = _patch_find(gray_source, resized_template, threshold)
        if result[0] > threshold:
            results.append(result)
    return results


def _patch_find(gray_source, gray_template, threshold):
    tw, th = gray_template.shape[1], gray_template.shape[0]
    res = cv.matchTemplate(gray_source, gray_template, cv.TM_CCOEFF_NORMED)
    (_, max_val, _, max_loc) = cv.minMaxLoc(res)
    if max_val < threshold:
        return 0, []

    top_left = max_loc
    left = top_left[0]
    top = top_left[1]
    rectangle = [top_left, (left, top + th), (left + tw, top), (left + tw, top + th)]

    return max_val, rectangle


def content_aware_fill(image, rect, radius=5):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    mask[rect[0][1] : rect[3][1], rect[0][0] : rect[3][0]] = 255
    dst = cv.inpaint(image, mask, radius, cv.INPAINT_TELEA)
    return dst
