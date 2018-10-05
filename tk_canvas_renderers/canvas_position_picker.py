import tkinter as tk

class CanvasPositionPicker:

    def __init__(self,
                 canvas: tk.Canvas,
                 width,
                 height,
                ):
        self._canvas = canvas
        self._width = width
        self._height = height

        self._axes_color = 'blue'
        self._crosshair_color = 'red'
        self._crosshair_len = 8
        self._crosshair_thickness = 2
        self._crosshair_font = ('Helvetica', 13, 'bold')

        self._vert_crosshair = None
        self._horiz_crosshair = None
        self._crosshair_text = None

        self._selected_pos_x = None
        self._selected_pos_y = None

        self._setup_ui()

    def _setup_ui(self):
        x_axis = self._canvas.create_line(0,
                                          self._get_center_y(),
                                          self._width,
                                          self._get_center_y(),
                                          fill=self._axes_color,
                                         )
        self._canvas.tag_raise(x_axis)

        y_axis = self._canvas.create_line(self._get_center_x(),
                                          0,
                                          self._get_center_x(),
                                          self._height,
                                          fill=self._axes_color,
                                         )
        self._canvas.tag_raise(y_axis)

        self._canvas.bind('<Button-1>', self._left_click)

    def _get_center_x(self):
        return int(self._width / 2)

    def _get_center_y(self):
        return int(self._height / 2)

    def _left_click(self, event):
        self._selected_pos_x = event.x
        self._selected_pos_y = event.y
        self._upate_crosshairs()
        self._canvas.update()

    def _get_selected_point(self):
        return (self._selected_pos_x - self._get_center_x(),
                self._get_center_y() - self._selected_pos_y)

    def _upate_crosshairs(self):
        self._canvas.coords(self._get_horiz_crosshair(), *self._get_horiz_crosshair_coords())
        self._canvas.coords(self._get_vert_crosshair(), *self._get_vert_crosshair_coords())
        self._canvas.coords(self._get_crosshair_text(),
                            self._selected_pos_x + 10,
                            self._selected_pos_y + 5,
                           )
        self._canvas.itemconfig(self._get_crosshair_text(),
                                text=str(self._get_selected_point()))

    def _get_horiz_crosshair_coords(self):
        return [self._selected_pos_x - self._crosshair_len, self._selected_pos_y,
                self._selected_pos_x + self._crosshair_len, self._selected_pos_y]

    def _get_vert_crosshair_coords(self):
        return [self._selected_pos_x, self._selected_pos_y- self._crosshair_len,
                self._selected_pos_x, self._selected_pos_y + self._crosshair_len]

    def _get_horiz_crosshair(self):
        if self._horiz_crosshair is None:
            self._horiz_crosshair = self._canvas.create_line(*self._get_horiz_crosshair_coords(),
                                                             fill=self._crosshair_color,
                                                             width=self._crosshair_thickness,
                                                            )
            self._canvas.tag_raise(self._horiz_crosshair)
        return self._horiz_crosshair

    def _get_vert_crosshair(self):
        if self._vert_crosshair is None:
            self._vert_crosshair = self._canvas.create_line(*self._get_vert_crosshair_coords(),
                                                            fill=self._crosshair_color,
                                                            width=self._crosshair_thickness,
                                                           )
            self._canvas.tag_raise(self._vert_crosshair)
        return self._vert_crosshair

    def _get_crosshair_text(self):
        if self._crosshair_text is None:
            self._crosshair_text = self._canvas.create_text(self._selected_pos_x,
                                                            self._selected_pos_y,
                                                            text=str(self._get_selected_point()),
                                                            fill=self._crosshair_color,
                                                            anchor=tk.NW,
                                                            font=self._crosshair_font,
                                                           )
            self._canvas.tag_raise(self._crosshair_text)
        return self._crosshair_text
