from typing import Iterable
import tkinter as tk
import PIL.Image

class PhotoRenderer:

    def __init__(self, photos: Iterable[PIL.Image.Image], height=None):
        '''
        :type:
        '''

        if isinstance(photos, list):
            self.photos = photos
        else:
            self.photos = [photos]

        self.root = tk.Tk()

        if height is None:
            self.height = self.root.winfo_screenheight() - 75

        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0)

        self.canvas = tk.Canvas(self.frame, scrollregion=(0, 0, 500, 2*self.height))

        self.hbar = tk.Scrollbar(self.frame ,orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.vbar.config(command=self.canvas.yview)

        self.canvas.config(width=300, height=self.height)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.root.mainloop()

    def _resize_photos(self):
        pass

    def _get_aspect_ratio(self, photo: PIL.Image.Image):
        return photo.width / photo.height



PhotoRenderer([])
