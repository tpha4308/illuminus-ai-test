import numpy as np
from scipy.spatial import cKDTree


def calculate_total_area(contour):
    m = len(contour)
    total_area = 0
    for i in range(m - 1):
        a = contour[i]
        b = contour[i + 1]
        total_area += (a[0] * b[1] - b[0] * a[1])
    return 0.5 * np.abs(total_area)


def find_closest_point_kdtree(point, contour):
    # Build a kd-tree from the contour points
    kdtree = cKDTree(contour)

    # Query the kd-tree to find the nearest neighbor of the current point
    _, closest_idx = kdtree.query(point, k=1, distance_upper_bound=float('inf'))

    # Retrieve the closest point and its index
    closest_point = contour[closest_idx]

    return closest_point, closest_idx


def check_exists(point, contour):
    # Check if point exists in contour

    for contour_point in contour:
        if contour_point[0] == point[0] and contour_point[1] == point[1]:
            return True
    return False


def postprocess_normalised_set(normalised_set, contour):
    reordered = reorder_contour(contour, normalised_set)

    # remove duplicates, if any
    normalised_set_dup_removed = []
    for contour_point in reordered:
        exists = False
        for elem in normalised_set_dup_removed:
            if contour_point[0] == elem[0] and contour_point[1] == elem[1]:
                exists = True
                break
        if not exists:
            normalised_set_dup_removed.append(contour_point)

    return np.array(normalised_set_dup_removed)


def increase_contour_length(contour, normalised_set, N):
    while len(normalised_set) < N:

        normalised_set = np.vstack((normalised_set, normalised_set[0]))

        max_d = float('-inf')
        to_add = None

        for i in range(len(normalised_set) - 1):
            p1 = normalised_set[i]
            p2 = normalised_set[i + 1]

            point_in_middle = np.array([(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2])
            p3, actual_contour_point_in_middle_index = find_closest_point_kdtree(point_in_middle, contour)

            d = np.linalg.norm(p2 - p1)
            if d > max_d and not check_exists(p3, normalised_set):
                max_d = d
                to_add = p3

        normalised_set = normalised_set[:-1]

        new_normalised_set = np.vstack((normalised_set, to_add))

        normalised_set = postprocess_normalised_set(new_normalised_set, contour)

    return normalised_set


def reorder_contour(contour, normalised_set):
    # reorder the contour points in normalised set to match the ordering in contour

    normalised_set_ordered = []

    for elem in contour:
        elem = np.squeeze(elem)
        for contour_point in normalised_set:
            if contour_point[0] == elem[0] and contour_point[1] == elem[1]:
                normalised_set_ordered.append(contour_point)
                break

    return np.array(normalised_set_ordered)


def compute_farthest_point(current_point, contours):
    farthest_point = None
    farthest_distance = -1
    farthest_idx = None
    for i, contour_point in enumerate(contours):
        distance_from_current_point = np.linalg.norm(current_point - contour_point)
        if distance_from_current_point > farthest_distance:
            farthest_point = contour_point
            farthest_distance = distance_from_current_point
            farthest_idx = i

    return farthest_point, farthest_idx


def decrease_contour_length_straight(normalised_set, N):
    while len(normalised_set) > N:

        normalised_set_circular = np.vstack((normalised_set, normalised_set[:2]))
        min_d = float('inf')
        to_remove_idx = 0

        for i in range(0, len(normalised_set_circular) - 2, 1):
            p1 = normalised_set_circular[i]
            p2 = normalised_set_circular[i + 2]
            p3 = normalised_set_circular[i + 1]

            d = np.abs(np.cross(p2 - p1, p1 - p3)) / np.linalg.norm(p2 - p1)
            if d < min_d:

                min_d = d
                to_remove_idx = i + 1
                if to_remove_idx >= len(normalised_set):
                    to_remove_idx = (i + 1) - len(normalised_set)

        normalised_set = np.array([normalised_set[i] for i in range(len(normalised_set)) if i != to_remove_idx])

    return normalised_set


def decrease_contour_length_angle(normalised_set, N):
    while len(normalised_set) > N:

        normalised_set_circular = np.vstack((normalised_set, normalised_set[:2]))
        min_angle = float('inf')
        to_remove_idx = 0

        for i in range(0, len(normalised_set_circular) - 2, 1):
            p1 = normalised_set_circular[i]
            p2 = normalised_set_circular[i + 2]
            p3 = normalised_set_circular[i + 1]

            angle = get_angle(p1, p3, p2)
            if angle < min_angle:

                min_angle = angle
                to_remove_idx = i + 1
                if to_remove_idx >= len(normalised_set):
                    to_remove_idx = (i + 1) - len(normalised_set)

        normalised_set = np.array([normalised_set[i] for i in range(len(normalised_set)) if i != to_remove_idx])

    return normalised_set


def decrease_contour_length_area(contour, normalised_set, N):
    # Remove the contour points that results in the least changes in total area when removed

    og_area = calculate_total_area(contour)

    while len(normalised_set) > N:

        min_diff = float('inf')
        chosen_new_normalised_set = None

        for i in range(len(normalised_set)):
            # Remove ith contour point
            new_normalised_set = np.vstack((normalised_set[:i], normalised_set[i + 1:]))

            # Compute new area with ith contour point removed
            new_area = calculate_total_area(new_normalised_set)
            diff_from_og_area = np.abs(new_area - og_area)

            if diff_from_og_area < min_diff:
                min_diff = diff_from_og_area
                chosen_new_normalised_set = new_normalised_set

        normalised_set = chosen_new_normalised_set

    return normalised_set


def get_angle(p1, p3, p2):
    # Compute angle bounded by (p1, p3, p2)

    v0 = np.array(p1) - np.array(p3)
    v1 = np.array(p2) - np.array(p3)

    angle = np.math.atan2(np.linalg.det([v0, v1]), np.dot(v0, v1))
    return np.degrees(angle)