from typing import List
import tkinter as tk
from base import Base
from tag_position_analyzer import TagPositionAnalyzer
from circumcircles import Circumcircles

def render_base(
        canvas: tk.Canvas,
        base: Base,
):
    gps_dot = add_circle(
        canvas=canvas,
        center=base.get_x_y_gps_position(),
        radius=1,
        fill='red',
        outline='red',
    )

    gps_error_circle = add_circle(
        canvas=canvas,
        center=base.get_x_y_gps_position(),
        radius=base.get_base_gps_error_circle_radius_pixels(),
        outline='red',
    )

    actual_pos_marker = add_square(
        canvas=canvas,
        center=base.get_actual_x_y_position(),
        radius=1,
        fill='red',
        outline='red',
    )
    return (
        gps_dot,
        gps_error_circle,
        actual_pos_marker,
    )

def render_tag_position_analyzer_frames(
        canvas: tk.Canvas,
        tag_position_analyzer: TagPositionAnalyzer,
        frames,
):
    for frame in frames:
        add_circle(
            canvas=canvas,
            center=tag_position_analyzer.get_early_position(frame),
            radius=2,
            fill='yellow',
            outline='yellow'
        )
        add_circle(
            canvas=canvas,
            center=tag_position_analyzer.get_late_position(frame),
            radius=2,
            fill='yellow',
            outline='yellow'
        )

def render_circumcircles(
        canvas: tk.Canvas,
        circumcircles: List[Circumcircles],
):
    r = []
    for circumcircle in circumcircles:
        for circle in [circumcircle.get_c1_low_def(), circumcircle.get_c2_low_def()]:
            r.append(
                canvas.create_line(
                    *circle.coords,
                    fill='yellow',
                    smooth=True,
                )
            )

def add_circle(
        canvas: tk.Canvas,
        center,
        radius,
        **kargs,
):
    return canvas.create_oval(
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
        **kargs
    )

def add_square(
        canvas: tk.Canvas,
        center,
        radius,
        **kargs,
):
    return canvas.create_rectangle(
        center[0] - radius,
        center[1] - radius,
        center[0] + radius,
        center[1] + radius,
        **kargs
    )
