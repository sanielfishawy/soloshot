import tkinter as tk
import PIL.ImageTk
import PIL.Image

root = tk.Tk()
canvas = tk.Canvas(root, width=800, height=600, bg='blue')

url = '/Users/Sani/dev/soloshot/data/test_data/test_images/photo.jpg'
i = PIL.Image.open(url)
i = i.resize((400,300))
p = PIL.ImageTk.PhotoImage(image=i)


canvas.create_image(0,0, image=p, anchor='nw')
canvas.create_line(50,50,300,300)
canvas.pack()
tk.mainloop()