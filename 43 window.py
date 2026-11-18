# Import Python's built-in libraries and give it a shorter name tk
import tkinter as tk

aspect_ratio = 4/3

# creates the main application window
root = tk.Tk()

# sets the dimensions and the title of the window
root.title("My  first window at 4:3")
root.geometry("800x600")
root.configure(bg="black")

resizing = False

def main_aspect_ratio(event):
    global resizing
    if resizing:
        return

    if event.widget  != root:
        return

    correct_height = int (width / apect_ratio)

    if abs(height - correct_height) > 2:
        resizing = True
        root.geometry(f"{width}x{correct_height}")
        resizing = False

# Bind the aspect ratio function to the window's configure event
root.bind("<Configure>", main_aspect_ratio)

#Start the main event loop
root.mainloop()