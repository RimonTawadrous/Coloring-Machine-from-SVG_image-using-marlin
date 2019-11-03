import tkinter as tk
import svg2gcode
from svg2gcode import generate_gcode
from tkinter import font  as tkfont
from tkinter import messagebox
from PIL import ImageTk, Image

extension = ''

class EntryWithSet(tk.Entry):
    def __init__(self, master, *args, **kwargs):
        tk.Entry.__init__(self, master, *args, **kwargs, width=50)
    def set(self, text_string):
        self.delete('0', 'end')
        self.insert('0', text_string)
    def get_text(self):
        return self.get()

class PyraApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.geometry("400x150+300+300")
        self.title("PyraMakerz")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        page_name = Window.__name__
        frame = Window(parent=container, controller=self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class Window(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.filename = tk.StringVar()
        label = tk.Label(self, text="Welcom to\nPyraMakerz Drawing Bot", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        #canvas = tk.Canvas(self, width=300, height=300)
        #canvas.pack()
        #
        #img = Image.open("C:/Users/Goda/Desktop/pyra_GUI/logo.png")
        #img.show()
        #render = ImageTk.PhotoImage(img)
        #canvas.create_image(0, 0, image=render, anchor=tk.NW)
        #panel = tk.Label(self, image=render)
        #img.image = render
        #panel.place(relx = 0.5, rely = 0.5)

        #lb_kindOfImage =  tk.Label(self, text="select image format")
        #lb_kindOfImage.pack()
        #var = tk.IntVar()
        #R1 = tk.Radiobutton(self, text="svg", variable=var, value=1 )
        #R1.pack(side = 'top')
        #R2 = tk.Radiobutton(self, text="png", variable=var, value=2)
        #R2.pack(side = 'top')

flag = False

def browse():
    global extension, flag
    from tkinter import filedialog
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select A \
            File",filetype = (("svg","*.svg"),\
                              #("png","*.png"),\
                              #("All Files","*.*")\
                               ))
    entry.set(filename)
    extension = entry.get_text()[-3:]
    if len(extension) >0:
        flag = True

def generate():
    global flag
    if flag:
        generate_gcode(entry.get_text())
        print("i am in")
    else:
        messagebox.showwarning("Warning", "Please select an image first")

if __name__ == "__main__":
    app = PyraApp()
    entry = EntryWithSet(app)
    entry.place(relx = 0.4, rely = 0.7, anchor = 's')
    tk.Button(app, text="Browse", command=browse).place(relx = 0.9, rely = 0.7, anchor = 's')
    tk.Button(app, text="Generate gcode", command=generate).place(relx = 0.85, rely = 0.85, anchor = 'center')
    app.mainloop()