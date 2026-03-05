from typing import NamedTuple

import numpy as np
from scipy import optimize


class VennResult(NamedTuple):
    """Result of a 2-circle Venn diagram distance calculation."""
    R: float  # radius of circle A
    r: float  # radius of circle B
    d: float  # distance between the two circle centres


def find_2venn_distance(area_a: float, area_b: float, area_ab: float) -> VennResult:
    """
    Find the distance between two circles given their areas and the area of their intersection,
    taken from https://en.wikipedia.org/wiki/Lens_(geometry)

    Args:
        area_a (float): area of circle A
        area_b (float): area of circle B
        area_ab (float): area of intersection of circle A and circle B.
            May equal area_a or area_b when one circle is fully contained in the other.

    Returns:
        VennResult: named tuple (R, r, d) where R is the radius of circle A,
            r is the radius of circle B, and d is the distance between the two centres.

    Raises:
        ValueError: if any area is negative, if the intersection exceeds either
            circle's area, or if the numerical solver fails to converge.
    """

    # make sure inputs are valid
    if area_a < 0 or area_b < 0 or area_ab < 0:
        raise ValueError("Areas must be positive")
    if area_ab > area_a or area_ab > area_b:
        raise ValueError("Intersection area must be less than or equal to the area of each circle")

    R = np.sqrt(area_a / np.pi)  # radius of circle A
    r = np.sqrt(area_b / np.pi)  # radius of circle B

    # No overlap — circles are tangent
    if area_ab == 0:
        return VennResult(R, r, R + r)

    # Full containment — one circle sits inside the other
    if area_ab == area_a or area_ab == area_b:
        return VennResult(R, r, abs(R - r))

    def func(d):
        part_1 = 2 * (1 / 4 * np.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R)))
        part_2 = -r**2 * np.arccos(np.clip((d**2 + r**2 - R**2) / (2 * d * r), -1, 1))
        part_3 = -R**2 * np.arccos(np.clip((d**2 + R**2 - r**2) / (2 * d * R), -1, 1))

        return area_ab + part_1 + part_2 + part_3

    result = optimize.root(func, R + area_ab / area_a * r, method='hybr')

    if result.success:
        return VennResult(R, r, float(result.x[0]))
    else:
        raise ValueError("Optimization failed")