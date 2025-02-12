"""Color manipulation tests."""

import math
import random
import pytest
from nightstorm.color_manipulation import (
    deopacify,
    opacify,
    rgba_to_hex,
    srgb_nonlinear_transform,
    srgb_nonlinear_transform_inverse,
    oklab_to_linear_rgb,
    linear_rgb_to_oklab,
    hex_to_lch,
    lch_to_hex,
)


def euclidean_distance(a, b):
    """Return the Euclidean distance between points a and b."""
    return math.sqrt(sum((ac - bc)**2 for ac, bc in zip(a, b)))


@pytest.mark.parametrize(
    "color, background, target, should_raise",
    [
        ("#ffffff", "#2c2c2c", "#a0a0a0", False),
        ("#07454a", "#e068d8", "#745791", False),
        ("#000000", "#ffffff", "#808080", False),
        ("#ffffff", "#ffffff", "#ffffff", False),
        ("#ff0000", "#00ff00", "#804000", True),
        ("#ffa500", "#800080", "#a0522d", True),
        ("#ffff00", "#000000", "#808000", True),
        ("#ffffff", "#ffffff", "#000000", True),
        ("#000000", "#808080", "#ffffff", True),
        ("#ffffff", "#808080", "#000000", True),
    ]
)
def test_deopacify(color, background, target, should_raise):
    """Test deopacify function."""
    if should_raise:
        with pytest.raises(ValueError):
            deopacify(color, background, target)
    else:
        result = deopacify(color, background, target)
        distance = euclidean_distance(*map(hex_to_lch, [
            opacify(result, background),
            target
        ]))
        assert math.isclose(0, distance, abs_tol=1e-02)


def test_conversions():
    """Test color conversion functions."""
    # pylint: disable=invalid-name
    random.seed(1)
    for _ in range(1000):
        x = random.random()
        y = random.random()
        z = random.random()
        xyz_hex = rgba_to_hex((x, y, z))

        # srgb <-> linear rgb
        assert math.isclose(x, srgb_nonlinear_transform_inverse(srgb_nonlinear_transform(x)))

        # linear rgb <-> oklab, ...
        x2, y2, z2 = oklab_to_linear_rgb(*linear_rgb_to_oklab(x, y, z))
        distance = euclidean_distance((x,y,z), (x2, y2, z2))
        assert math.isclose(0, distance, abs_tol=1e-06)
        assert all(lambda x: 0 <= x <= 1 for x in [x2, y2, z2, srgb_nonlinear_transform_inverse(x)])

        # hex_to_lch <-> lch_to_hex
        L, C, h = hex_to_lch(xyz_hex)
        assert xyz_hex == lch_to_hex(L, C, h)
