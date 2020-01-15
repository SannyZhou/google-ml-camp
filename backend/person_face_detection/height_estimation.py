import numpy as np
import pickle


def line_intersect(m1, b1, m2, b2):
    if m1 == m2:
        print("These lines are parallel!!!")
        return None
    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1
    return x, y


def intersection_point(a1, a2, b1, b2):
    slope_A = (a2[1] - a1[1]) / (a2[0] - a1[0])
    slope_B = (b2[1] - b1[1]) / (b2[0] - b1[0])
    y_int_A = a1[1] - slope_A * a1[0]
    y_int_B = b1[1] - slope_B * b1[0]
    return line_intersect(slope_A, y_int_A, slope_B, y_int_B)


def height_estimate(person_top, person_bottom, height_parameters):
    reference_top = height_parameters['reference_top']
    reference_bottom = height_parameters['reference_bottom']
    vanishing_points = height_parameters['vanishing_points']
    point_on_vl = intersection_point(reference_bottom, person_bottom, vanishing_points[0], vanishing_points[1])
    person_height_point = intersection_point(reference_top, reference_bottom, person_top, point_on_vl)
    object_height = 2.1
    person_height = object_height * (
            np.linalg.norm(np.array(person_height_point) - np.array(reference_bottom)) * 1.0 / np.linalg.norm(
        np.array(reference_top) - np.array(reference_bottom)))
    return person_height

#
# parameters = pickle.load(open('parameters.pkl', 'rb'), encoding='iso-8859-1')
# height = height_estimation(person_top, person_bottom, parameters)
