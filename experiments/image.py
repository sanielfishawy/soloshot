import sys, os
sys.path.insert(0, os.getcwd())
import PIL.Image 
import PIL.ImageFilter as IF
import PIL
import tkinter as tk

im_path = os.getcwd() + '/data/images/will.jpg'


i = PIL.Image.open(im_path)
tki = tk.PhotoImage(i)

b = i.filter(IF.DETAIL)

b 