import tkinter as tk

class ScrollableCanvas:
    '''A canvas that can be added to a tkinter layout as a widget that has
       scrollbars to allow it to be viewed in a fixed sized scrollview that is
       smaller than the size of the canvas'''

    def __init__(self,
                 master,
                 canvas_width,
                 canvas_height,
                 scrollview_width,
                 scrollview_height
                ):
        self._master = master
        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._scrollview_width = scrollview_width
        self._scrollview_height = scrollview_height

        # lazy init
        self._frame = None
        self._canvas = None
        self._vbar = None
        self._hbar = None

    def get_canvas(self) -> tk.Canvas:
        self._frame = tk.Frame(self._master)
        self._frame.grid(row=0, column=0)

        self._canvas = tk.Canvas(
            self._frame,
            scrollregion=(
                0,
                0,
                self._canvas_width,
                self._canvas_height,
            ),
            background='blue'
        )

        self._canvas.config(
            width=self._scrollview_width,
            height=self._scrollview_height,
        )

        self._vbar = tk.Scrollbar(self._frame, orient=tk.VERTICAL)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._vbar.config(command=self._canvas.yview)

        self._hbar = tk.Scrollbar(self._frame, orient=tk.HORIZONTAL)
        self._hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._hbar.config(command=self._canvas.xview)

        self._canvas.pack(
            side=tk.LEFT,
            expand=True,
            fill=tk.BOTH,
        )
        self._canvas.config(
            yscrollcommand=self._vbar.set,
            xscrollcommand=self._hbar.set,
        )

        return self._canvas
