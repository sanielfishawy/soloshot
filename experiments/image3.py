import tkinter as tk
import PIL.ImageTk
import PIL.Image


root = tk.Tk()

url = '/Users/Sani/dev/soloshot/data/test_data/test_images/photo.jpg'
i = PIL.Image.open(url)
i = i.resize((400,300))
p = PIL.ImageTk.PhotoImage(image=i)

_outer_frame = tk.Frame(root)
_outer_frame.grid(row=0, column=0)

_outer_canvas = tk.Canvas(_outer_frame, scrollregion=(0, 0, 1000, 1000), background='blue')
_outer_canvas.config(width=1000, height=800)

inner_canvas = tk.Canvas(master=_outer_canvas, bg='red')
_outer_canvas.create_image(0, 0, image=p, anchor='nw')
inner_canvas.create_image(0,0, image=p, anchor='nw')

_outer_canvas.create_window(100, 100, anchor='nw', height=300, width=300, window=inner_canvas)

_vbar = tk.Scrollbar(_outer_frame, orient=tk.VERTICAL)
_vbar.pack(side=tk.RIGHT, fill=tk.Y)
_vbar.config(command=_outer_canvas.yview)


_outer_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
_outer_canvas.config(yscrollcommand=_vbar.set)

tk.mainloop()


        # self._outer_canvas = tk.Canvas(self._outer_frame,
        #                                scrollregion=(0,
        #                                              0,
        #                                              self._get_first_photo_resize_width(),
        #                                              self._get_total_photo_height()),
        #                                background='blue')
        # self._outer_canvas.config(width=self._get_first_photo_resize_width(),
        #                           height=self._get_window_height())

        # self._vbar = tk.Scrollbar(self._outer_frame, orient=tk.VERTICAL)
        # self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        # self._vbar.config(command=self._outer_canvas.yview)

        # self._outer_canvas.create_image(0, 0, image=self._get_image_tk_of_resized_photos()[0], anchor='nw')

        # self._outer_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        # self._outer_canvas.config(yscrollcommand=self._vbar.set)