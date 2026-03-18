from typing import NamedTuple

import numpy as np
from scipy import optimize


class VennResult2(NamedTuple):
    """Result of a 2-circle Venn diagram distance calculation."""

    r_a: float  # radius of circle A
    r_b: float  # radius of circle B
    d_ab: float  # distance between the two circle centres


class VennResult3(NamedTuple):
    """Result of a 3-circle Venn diagram distance calculation."""

    r_a: float  # radius of circle A
    r_b: float  # radius of circle B
    r_c: float  # radius of circle C
    d_ab: float  # distance between the centres of circles A and B
    d_ac: float  # distance between the centres of circles A and C
    d_bc: float  # distance between the centres of circles B and C


def find_2venn_distance(area_a: float, area_b: float, area_ab: float) -> VennResult2:
    """
    Find the distance between two circles given their areas and the area of their intersection,
    taken from https://en.wikipedia.org/wiki/Lens_(geometry)

    Args:
        area_a (float): area of circle A
        area_b (float): area of circle B
        area_ab (float): area of intersection of circle A and circle B.
            May equal area_a or area_b when one circle is fully contained in the other.

    Returns:
        VennResult2: named tuple (r_a, r_b, d_ab) where r_a is the radius of circle A,
            r_b is the radius of circle B, and d_ab is the distance between the two centres.

    Raises:
        ValueError: if any area is negative, if the intersection exceeds either
            circle's area, or if the numerical solver fails to converge.
    """

    # Convert to float to ensure consistent comparisons
    area_a = float(area_a)
    area_b = float(area_b)
    area_ab = float(area_ab)

    # make sure inputs are valid
    if area_a < 0 or area_b < 0 or area_ab < 0:
        raise ValueError(
            f"All areas must be non-negative, got "
            f"area_a={area_a}, area_b={area_b}, area_ab={area_ab}."
        )
    if area_ab > area_a and not np.isclose(area_ab, area_a):
        raise ValueError(
            f"The intersection area (area_ab={area_ab}) cannot exceed "
            f"circle A (area_a={area_a}). "
            f"The overlap between two circles can never be larger than either circle."
        )
    if area_ab > area_b and not np.isclose(area_ab, area_b):
        raise ValueError(
            f"The intersection area (area_ab={area_ab}) cannot exceed "
            f"circle B (area_b={area_b}). "
            f"The overlap between two circles can never be larger than either circle."
        )

    # Clamp area_ab to handle floating-point imprecision for large integers
    area_ab = min(area_ab, area_a, area_b)

    R = np.sqrt(area_a / np.pi)  # radius of circle A
    r = np.sqrt(area_b / np.pi)  # radius of circle B

    # No overlap — circles are tangent
    if area_ab == 0:
        return VennResult2(R, r, R + r)

    # Full containment — one circle sits inside the other
    if np.isclose(area_ab, area_a) or np.isclose(area_ab, area_b):
        return VennResult2(R, r, abs(R - r))

    def func(d):
        part_1 = 2 * (
            1 / 4 * np.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))
        )
        part_2 = -(r**2) * np.arccos(np.clip((d**2 + r**2 - R**2) / (2 * d * r), -1, 1))
        part_3 = -(R**2) * np.arccos(np.clip((d**2 + R**2 - r**2) / (2 * d * R), -1, 1))

        return area_ab + part_1 + part_2 + part_3

    result = optimize.root(func, R + area_ab / area_a * r, method="hybr")

    if result.success:
        return VennResult2(R, r, float(result.x[0]))
    else:
        raise ValueError(
            f"Could not find a valid circle distance for "
            f"area_a={area_a}, area_b={area_b}, area_ab={area_ab}. "
            f"Check that the input areas are geometrically consistent."
        )


def find_3venn_distance(
    area_a: float,
    area_b: float,
    area_c: float,
    area_ab: float,
    area_ac: float,
    area_bc: float,
) -> VennResult3:
    """Find the distances between three circles given their areas and the areas of their pairwise intersections.
    This function uses the 2-circle distance function to calculate the radius of each circle and the distance between each pair of circles.
    Args:
        area_a:     Area of circle A.
        area_b:     Area of circle B.
        area_c:     Area of circle C.
        area_ab:    Area of the intersection of circles A and B.
        area_ac:    Area of the intersection of circles A and C.
        area_bc:    Area of the intersection of circles B and C.
    Returns:
        VennResult3: named tuple (r_a, r_b, r_c, d_ab, d_ac, d_bc) where r_a is the radius of circle A,
            r_b is the radius of circle B, r_c is the radius of circle C, and d_ab, d_ac, d_bc are the distances between the centres of the circles.
    Raises:
        ValueError: if any area is negative, if the intersection exceeds either
            circle's area, if the numerical solver fails to converge, or if the
            three pairwise distances do not satisfy the triangle inequality
            (meaning the three circles cannot be laid out in 2D).
    """

    # calculate the distance between each pair of circles using the 2-circle function
    try:
        result_ab = find_2venn_distance(area_a, area_b, area_ab)
    except ValueError as e:
        raise ValueError(
            f"Invalid areas for circles A and B: {e}"
        ) from e
    try:
        result_ac = find_2venn_distance(area_a, area_c, area_ac)
    except ValueError as e:
        raise ValueError(
            f"Invalid areas for circles A and C: {e}"
        ) from e
    try:
        result_bc = find_2venn_distance(area_b, area_c, area_bc)
    except ValueError as e:
        raise ValueError(
            f"Invalid areas for circles B and C: {e}"
        ) from e

    d_ab = result_ab.d_ab
    d_ac = result_ac.d_ab
    d_bc = result_bc.d_ab

    # Validate that the three pairwise distances form a valid triangle.
    # If they don't, the three circles cannot be positioned in 2D.
    tol = 1e-9 * max(d_ab, d_ac, d_bc, 1.0)
    if d_ab > d_ac + d_bc + tol:
        raise ValueError(
            f"The three pairwise distances do not form a valid triangle: "
            f"d_ab={d_ab:.6g} > d_ac + d_bc = {d_ac:.6g} + {d_bc:.6g} = {d_ac + d_bc:.6g}. "
            f"The overlaps (area_ab={area_ab}, area_ac={area_ac}, area_bc={area_bc}) "
            f"are geometrically inconsistent — these three circles cannot be laid out in 2D."
        )
    if d_ac > d_ab + d_bc + tol:
        raise ValueError(
            f"The three pairwise distances do not form a valid triangle: "
            f"d_ac={d_ac:.6g} > d_ab + d_bc = {d_ab:.6g} + {d_bc:.6g} = {d_ab + d_bc:.6g}. "
            f"The overlaps (area_ab={area_ab}, area_ac={area_ac}, area_bc={area_bc}) "
            f"are geometrically inconsistent — these three circles cannot be laid out in 2D."
        )
    if d_bc > d_ab + d_ac + tol:
        raise ValueError(
            f"The three pairwise distances do not form a valid triangle: "
            f"d_bc={d_bc:.6g} > d_ab + d_ac = {d_ab:.6g} + {d_ac:.6g} = {d_ab + d_ac:.6g}. "
            f"The overlaps (area_ab={area_ab}, area_ac={area_ac}, area_bc={area_bc}) "
            f"are geometrically inconsistent — these three circles cannot be laid out in 2D."
        )

    return VennResult3(
        r_a=result_ab.r_a,
        r_b=result_ab.r_b,
        r_c=result_ac.r_b,
        d_ab=d_ab,
        d_ac=d_ac,
        d_bc=d_bc,
    )
