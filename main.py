import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from scipy import ndimage
from utils import *


def RDP(normalised_set, curve_segment_queue, epsilon, contour):
    if len(curve_segment_queue) == 0:
        return np.array(normalised_set)

    P1_index = curve_segment_queue[0]["start"]
    farthest_from_P1_index = curve_segment_queue[0]["end"]

    farthest_from_P1 = contour[farthest_from_P1_index]
    P1 = contour[P1_index]

    # get the point that is farthest from the line connected (P1, farthest_from_P1)
    farthest_from_current_line = None
    farthest_idx = None
    farthest_distance = -1

    for n in range(P1_index + 1, farthest_from_P1_index):
        point = contour[n]
        d = np.abs(np.cross(farthest_from_P1 - P1, point - P1)) / np.linalg.norm(farthest_from_P1 - P1)
        if d > farthest_distance:
            farthest_from_current_line = point
            farthest_idx = n
            farthest_distance = d

    # dequeue the current curve segment
    curve_segment_queue.pop(0)
    # print("Farthest distance", farthest_distance)

    # if the farthest distance above epsilon then add two half segments to queue
    if farthest_distance >= epsilon:
        normalised_set.append(farthest_from_current_line)
        curve_segment_queue.append({"start": P1_index, "end": farthest_idx})
        curve_segment_queue.append({"start": farthest_idx, "end": farthest_from_P1_index})

    return RDP(normalised_set, curve_segment_queue, epsilon, contour)


def reorder_contour(contour, normalised_set):
    normalised_set_ordered = []

    for elem in contour:
        elem = np.squeeze(elem)
        for contour_point in normalised_set:
            if contour_point[0] == elem[0] and contour_point[1] == elem[1]:
                normalised_set_ordered.append(contour_point)
                break

    return np.array(normalised_set_ordered)


def get_normalised_set(contour, N, epsilon=20):
    centroid = np.mean(contour, axis=0)[0]

    P1, P1_index = compute_farthest_point(centroid, contour)
    contour = np.vstack((contour[P1_index:], contour[:P1_index]))

    farthest_from_P1, farthest_from_P1_index = compute_farthest_point(P1, contour)

    normalised_set = [P1, farthest_from_P1]
    curve_segment_queue = [{"start": 0, "end": farthest_from_P1_index},
                           {"start": farthest_from_P1_index, "end": len(contour) - 1}]

    normalised_set = RDP(normalised_set, curve_segment_queue, epsilon, contour)
    while len(normalised_set) < N:
        epsilon -= 3
        if epsilon < 0:
            break
        normalised_set = [P1, farthest_from_P1]
        curve_segment_queue = [{"start": 0, "end": farthest_from_P1_index},
                               {"start": farthest_from_P1_index, "end": len(contour) - 1}]
        normalised_set = RDP(normalised_set, curve_segment_queue, epsilon, contour)

    return postprocess_normalised_set(normalised_set, contour)


def get_normalised_contour_pipeline(img_path, N, decrease_method="angle"):
    # read image
    og_img = cv2.imread(img_path)
    gray_image = cv2.cvtColor(og_img, cv2.COLOR_BGR2GRAY)

    # fill in any holes
    img = ndimage.binary_fill_holes(gray_image).astype(np.uint8)

    # get initial set of contours
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    normalised_contour_ls = []
    normalised_contour_ls_w_comparison = []

    max_contour_length = max([len(contour) for contour in contours])
    contours = [contour for contour in contours if len(contour)>0.1*max_contour_length]

    for contour in contours:
        contour = np.squeeze(contour)

        normalised_set = get_normalised_set(contour, N)
        normalised_set_N = None

        if len(normalised_set) > N:
            if decrease_method == "angle":
                normalised_set_N = decrease_contour_length_angle(normalised_set, N)
            elif decrease_method == "straight":
                normalised_set_N = decrease_contour_length_straight(normalised_set, N)
            elif decrease_method == "area":
                normalised_set_N = decrease_contour_length_area(contour, normalised_set, N)

        elif len(normalised_set) < N:
            normalised_set_N = increase_contour_length(contour, normalised_set, N)

        normalised_contour_ls_w_comparison.append((normalised_set, normalised_set_N))

        if normalised_set_N is not None:
            normalised_set = normalised_set_N
        normalised_contour_ls.append(normalised_set)

    visualise_comparison(img_path, og_img, img, normalised_contour_ls_w_comparison, contours, N=N,
                         decrease_method=decrease_method)
    return gray_image, normalised_contour_ls


def visualise_comparison(img_path, og_img, img, normalised_contour_ls_w_comparison, og_contour_ls, N, decrease_method):
    fig, axs = plt.subplots(len(normalised_contour_ls_w_comparison), 3,
                            figsize=(15, 6*len(normalised_contour_ls_w_comparison)))

    for i in range(len(normalised_contour_ls_w_comparison)):
        og_contour = np.squeeze(og_contour_ls[i])
        normalised_set_RDP, normalised_set_N = normalised_contour_ls_w_comparison[i]

        ax_0 = axs[0]
        ax_1 = axs[1]
        ax_2 = axs[2]
        if len(normalised_contour_ls_w_comparison) > 1:
            ax_0 = axs[i, 0]
            ax_1 = axs[i, 1]
            ax_2 = axs[i, 2]

        ax_0.imshow(og_img)
        ax_0.plot([p[0] for p in og_contour], [p[1] for p in og_contour], marker='s', c="orange")
        ax_0.set_xlabel(f"N = {len(og_contour)}")

        ax_1.imshow(img, cmap="gray")
        ax_1.set_xlabel(f"N = {len(normalised_set_RDP)}")
        normalised_set_RDP_ = np.vstack((normalised_set_RDP, normalised_set_RDP[0]))
        ax_1.plot([p[0] for p in normalised_set_RDP_], [p[1] for p in normalised_set_RDP_], marker='s', c="orange")

        ax_2.imshow(img, cmap="gray")

        if normalised_set_N is None:
            normalised_set_N = normalised_set_RDP
        ax_2.set_xlabel(f"N = {len(normalised_set_N)}")
        normalised_set_N_ = np.vstack((normalised_set_N, normalised_set_N[0]))
        ax_2.plot([p[0] for p in normalised_set_N_], [p[1] for p in normalised_set_N_], marker='s', c="orange")

    cols = ["Original image &\n contours", "Filled holes &\nRDP contours", "Final normalisation"]

    col_axs = axs
    if len(normalised_contour_ls_w_comparison) > 1:
        col_axs = axs[0]
    for ax, col in zip(col_axs, cols):
        ax.set_title(col)

    img_name = img_path.split('.')[0].split('/')[-1]
    fig.suptitle(f"Contour normalisation, desired N = {N}\nDecrease method: {decrease_method}")
    fig.tight_layout()
    plt.savefig(f"{img_name}_comparison_{decrease_method}.png")


# def visualise_contour(img_path, og_img, contour_ls, original=False):
#     colour = (23, 166, 209)
#     img_w_contour = cv2.drawContours(og_img.copy(), contour_ls, -1, color=colour, thickness=2, lineType=cv2.LINE_AA)
#     img_name = img_path.split('.')[0].split('/')[-1]
#
#     for contour in contour_ls:
#         contour = np.squeeze(contour)
#         for point in contour:
#             img_w_contour = cv2.circle(img=img_w_contour, center=point, radius=2, color=colour, thickness=3)
#
#     if original:
#         cv2.imwrite(f'{img_name}_original.png', img_w_contour)
#     else:
#         cv2.imwrite(f'{img_name}_normalised_2.png', img_w_contour)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--img_path', type=str, help='Path to binary image')
    parser.add_argument('--N', type=int, help='Pre-determined contour length')
    parser.add_argument('--decrease_method', type=str, help='Path to binary image', default="angle")

    # TODO: add help here

    args = parser.parse_args()
    img_path = args.img_path
    N = args.N
    decrease_method = args.decrease_method

    print(img_path, N, decrease_method)

    normalised_contour_ls = get_normalised_contour_pipeline(img_path, N, decrease_method)
