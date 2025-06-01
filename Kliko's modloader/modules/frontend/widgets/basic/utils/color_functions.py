import colorsys


def modify_hsv_from_hex(hex: str, dh: int = 0, ds: int = 0, dv: int = 0) -> str:
    original_hex: str = hex
    hex = hex.removeprefix("#")
    if len(hex) in {3, 4}: hex = f"{hex[0]*2}{hex[1]*2}{hex[2]*2}"
    if len(hex) < 0: raise ValueError(f"Invalid hex code: {original_hex}")

    r, g, b = int(hex[0:2], 16)/255, int(hex[2:4], 16)/255, int(hex[4:6], 16)/255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + dh / 360) % 1.0
    s = max(0, min(1, s + ds/100))
    v = max(0, min(1, v + dv/100))

    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"