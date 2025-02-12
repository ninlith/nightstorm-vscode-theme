"""Color manipulation."""
# pylint: disable=invalid-name

import math


def cbrt(x):  # python >= 3.11 has math.cbrt
    """Return the cube root of x."""
    return math.copysign(abs(x)**(1/3), x)


def clamp(x, minimum=0, maximum=1):
    """Constrain x into an interval."""
    return max(minimum, min(maximum, x))


def linear_rgb_to_oklab(r, g, b):
    """Convert from linear RGB to Oklab."""
    # https://bottosson.github.io/posts/oklab/

    l = 0.4122214708*r + 0.5363325363*g + 0.0514459929*b
    m = 0.2119034982*r + 0.6806995451*g + 0.1073969566*b
    s = 0.0883024619*r + 0.2817188376*g + 0.6299787005*b

    l_ = cbrt(l)
    m_ = cbrt(m)
    s_ = cbrt(s)

    return (0.2104542553*l_ + 0.7936177850*m_ - 0.0040720468*s_,
            1.9779984951*l_ - 2.4285922050*m_ + 0.4505937099*s_,
            0.0259040371*l_ + 0.7827717662*m_ - 0.8086757660*s_)


def oklab_to_linear_rgb(L, a, b):
    """Convert from Oklab to linear RGB."""

    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b

    l = l_*l_*l_
    m = m_*m_*m_
    s = s_*s_*s_

    return (+4.0767416621*l - 3.3077115913*m + 0.2309699292*s,
            -1.2684380046*l + 2.6097574011*m - 0.3413193965*s,
            -0.0041960863*l - 0.7034186147*m + 1.7076147010*s)


def srgb_nonlinear_transform(x):
    """Convert a coordinate from linear RGB to sRGB."""
    if x >= 0.0031308:
        return clamp((1.055)*x**(1.0/2.4) - 0.055)
    return clamp(12.92*x)


def srgb_nonlinear_transform_inverse(x):
    """Convert a coordinate from sRGB to linear RGB."""
    if x >= 0.04045:
        return ((x + 0.055)/(1 + 0.055))**2.4
    return x/12.92


def lab_to_lch(L, a, b):
    """Convert from Lab-coordinates to polar form."""
    C = math.sqrt(a**2 + b**2)
    h = math.atan2(b, a)
    return L, C, h


def lch_to_lab(L, C, h):
    """Convert from polar form to Lab-coordinates."""
    a = C*math.cos(h)
    b = C*math.sin(h)
    return L, a, b


def hex_to_rgba(s: str) -> list[float]:
    """Convert from #rrggbb[aa] notation to RGBA coordinates."""
    return list(map(lambda x: int("".join(x), 16)/255,
                    zip(*[iter(f"{s[1:]:f<8}")]*2)))


def rgba_to_hex(coordinates: list[float]) -> str:
    """Convert from coordinates between 0 and 1 to hex notation."""
    return "#" + "".join(f"{round(v*255):0>2x}" for v in coordinates)


def hex_to_lch(s):
    """Convert from hex notation to LCh-coordinates."""
    *rgb, _ = hex_to_rgba(s)
    return lab_to_lch(*linear_rgb_to_oklab(*map(srgb_nonlinear_transform_inverse, rgb)))


def lch_to_hex(L, C, h):
    """Convert from LCh-coordinates to hex notation."""
    return rgba_to_hex(list(map(srgb_nonlinear_transform,
                                oklab_to_linear_rgb(*lch_to_lab(L, C, h)))))


def oklab_adjust(base_color, lightness_factor=1, chroma_factor=1, hue_addend=0):
    """Adjust lightness, chroma and/or hue."""
    L, C, h = hex_to_lch(base_color)
    L_adjusted = L * lightness_factor
    C_adjusted = C * chroma_factor
    h_adjusted = h + hue_addend

    # Ensure lighness and chroma are non-negative.
    L_adjusted = max(0, L_adjusted)
    C_adjusted = max(0, C_adjusted)

    # Convert back to linear RGB.
    L, a, b = lch_to_lab(L_adjusted, C_adjusted, h_adjusted)
    r, g, b = oklab_to_linear_rgb(L, a, b)

    # Clip to sRGB gamut.
    r = clamp(r)
    g = clamp(g)
    b = clamp(b)

    return rgba_to_hex(list(map(srgb_nonlinear_transform, [r, g, b])))
