import tkinter as tk

root = tk.Tk()
root.title("4:3 Window")
root.geometry("800x600")
root.resizable(True, True)
root.configure(bg="black")
root.wm_aspect(4, 3, 4, 3)
root.mainloop()