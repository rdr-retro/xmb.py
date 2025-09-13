import math, datetime, numpy as np
import pygame

MONTH_RGB = {
    1: (160,160,170), 2: (225,205,70), 3: (115,200,100), 4: (230,140,185),
    5: (60,140,80), 6: (170,145,225), 7: (130,185,235), 8: (60,110,220),
    9: (140,95,200), 10: (225,170,65), 11: (150,110,70), 12: (200,70,70),
}

def lerp(a, b, t): return a + (b - a) * t
def clamp(x, a, b): return max(a, min(b, x))

def hour_brightness(hour):
    if 0 <= hour < 4:  return 0.12
    if 4 <= hour < 6:  return lerp(0.12, 0.45, (hour-4)/2)
    if 6 <= hour < 9:  return lerp(0.45, 0.85, (hour-6)/3)
    if 9 <= hour < 12: return lerp(0.85, 1.00, (hour-9)/3)
    if 12<= hour < 16: return 1.00
    if 16<= hour < 18: return lerp(1.00, 0.75, (hour-16)/2)
    if 18<= hour < 20: return lerp(0.75, 0.35, (hour-18)/2)
    return 0.20

def month_color(now):
    m = now.month
    base = np.array(MONTH_RGB[m], dtype=float)
    day = now.day
    nxt = MONTH_RGB[1 if m == 12 else m + 1]
    nxt = np.array(nxt, dtype=float)
    if 12 <= day <= 27:
        t = clamp((day-12)/15.0, 0, 1)
        col = (1-t)*base + t*nxt
    else:
        col = base
    b = hour_brightness(now.hour)
    col = np.clip(col * (0.6 + 0.4*b), 0, 255)
    return tuple(col.astype(int))

def make_gradient(surface, top_rgb, bottom_rgb):
    W, H = surface.get_size()
    for y in range(H):
        t = y/(H-1)
        r = int(lerp(top_rgb[0], bottom_rgb[0], t))
        g = int(lerp(top_rgb[1], bottom_rgb[1], t))
        b = int(lerp(top_rgb[2], bottom_rgb[2], t))
        pygame.draw.line(surface, (r,g,b), (0,y), (W,y))

def render_multiline_text_surface(text, font, color, max_width):
    lines = []
    words = text.split()
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        test_surf = font.render(test_line, True, color)
        if test_surf.get_width() > max_width and current_line != '':
            lines.append(current_line)
            current_line = word + ' '
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    line_height = font.get_linesize()
    surface_width = max(font.size(line)[0] for line in lines)
    surface_height = line_height * len(lines)
    surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
    y = 0
    for line in lines:
        line_surf = font.render(line.strip(), True, color)
        surface.blit(line_surf, (0, y))
        y += line_height
    return surface

def catmull_rom(p0, p1, p2, p3, t):
    t2, t3 = t*t, t*t*t
    a = (-0.5*t3 + t2 - 0.5*t)
    b = ( 1.5*t3 - 2.5*t2 + 1.0)
    c = (-1.5*t3 + 2.0*t2 + 0.5*t)
    d = ( 0.5*t3 - 0.5*t2)
    x = a*p0[0] + b*p1[0] + c*p2[0] + d*p3[0]
    y = a*p0[1] + b*p1[1] + c*p2[1] + d*p3[1]
    return (x, y)

def sample_spline(ctrl, samples):
    pts = []
    n = len(ctrl)
    if n < 4: return ctrl
    segs = n - 3
    per_seg = max(2, samples // segs)
    for s in range(segs):
        p0, p1, p2, p3 = ctrl[s], ctrl[s+1], ctrl[s+2], ctrl[s+3]
        for i in range(per_seg):
            t = i / (per_seg - 1)
            pts.append(catmull_rom(p0, p1, p2, p3, t))
    return pts
