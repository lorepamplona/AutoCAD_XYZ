import os
import glob
from pyautocad import Autocad, APoint
import ctypes
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import simpledialog
import re


color_indices = [1, 2, 3, 4, 5, 6, 70, 80, 90, 10, 110, 120, 130, 140, 150, 160, 170, 180, 190, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

class ProgressDialog(tk.Toplevel):
    def __init__(self, parent, title, message, max_value):
        super().__init__(parent)
        self.title(title)

        self.label = tk.Label(self, text=message)
        self.label.pack(padx=20, pady=10)

        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate", maximum=max_value)
        self.progressbar.pack(padx=20, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.disable_close)

    def disable_close(self):
        pass

    def update_progress(self, value, message):
        self.progressbar["value"] = value
        self.label.config(text=message)
        self.update_idletasks()




def create_text(acad, x, y, z, height, prefix, layer, integer_part, decimal_part, sign):
    # Create the integer part of the text
    integer_text = acad.model.AddText(integer_part, APoint(x, y, z), height)
    integer_text.Layer = layer.Name

    # If the sign is negative, create the negative sign text below the integer part
    if sign == "-":
        negative_sign_text = acad.model.AddText(sign, APoint(x, y, z - height), height)
        negative_sign_text.Layer = layer.Name

    # Create the decimal part of the text
    decimal_text = acad.model.AddText(decimal_part, APoint(x + height * len(integer_part), y, z), 0.78 * height)
    decimal_text.Layer = layer.Name

    return integer_text, decimal_text
def create_layer(acad, layer_name, color_index):
    layers = acad.doc.Layers
    layer = layers.Add(layer_name)
    layer.color = color_index
    return layer

def get_or_create_layer(acad, layer_name, color_index):
    layers = acad.doc.Layers
    for layer in layers:
        if layer.Name == layer_name:
            return layer
    return create_layer(acad, layer_name, color_index)


def create_text_label(acad, x, y, z, height, layer):
    z_str = f"{z:.1f}"
    
    # Extract the sign, integer part, and decimal part
    match = re.match(r"(-?)(\d+)(\.\d)?", z_str)
    sign, integer_part, decimal_part = match.groups()

    # Add %%U before and after the integer part if there is a negative sign
    if sign == "-":
        integer_part = f"%%U{integer_part}%%U"

    # Create a text for the integer part
    int_text = acad.model.AddText(integer_part, APoint(x, y, z), height)
    int_text.Layer = layer.Name

    # Calculate the width of the integer part text
    int_text_min, int_text_max = APoint(0, 0, 0), APoint(0, 0, 0)
    int_text.GetBoundingBox(int_text_min, int_text_max)
    int_text_width = int_text_max[0] - int_text_min[0]

    # Create a text for the decimal part
    decimal_text = acad.model.AddText(decimal_part[1:], APoint(x + int_text_width + 3, y - 1, z), height * 0.75)
    decimal_text.Layer = layer.Name

    return int_text, decimal_text


def load_xyz_files(folder_path, height, prefix):
    # Connect to AutoCAD
    acad = Autocad()
    acad.prompt("Connected to AutoCAD...")
    
    # Get a list of all .xyz files in the folder
    os.chdir(folder_path)
    xyz_files = glob.glob("*.xyz")

    root = tk.Tk()
    root.withdraw()

    progress_dialog = ProgressDialog(root, "Progress", "Processing files...", len(xyz_files))
    progress_dialog.update()

    # Iterate through all .xyz files and process them
    for index, xyz_file in enumerate(xyz_files):
        acad.prompt(f"Processing {xyz_file}...")
        print(f"Processing {xyz_file}...")
        progress_dialog.update_progress(index, f"Processing {xyz_file}...")

        try:
            with open(xyz_file, 'r') as file:
                text_objects = []
                for line in file:
                    # Parse the coordinates
                    x, y, z = map(float, line.strip().split())

                    # Determine the layer name and color index
                    layer_name = f"{prefix}_{int(z)}"
                    color_index = color_indices[abs(int(z)) % len(color_indices)]

                    # Get or create the layer
                    layer = get_or_create_layer(acad, layer_name, color_index)

                    # Create text labels in AutoCAD
                    #create_text_label(acad, x, y, z, height, layer)
                    text_objects.extend(create_text_label(acad, x, y, z, height, layer))
                # Add all text objects to the AutoCAD model space at once
                for text_object in text_objects:
                    acad.model.AddObject(text_object, text_object.ObjectID)
                    text_object.Layer = layer.Name

        except Exception as error:
            print("Error:", error)

        acad.doc.Utility.Prompt("Desenhando profundidades...")
        acad.doc.Utility.Prompt("Obrigado por usar XYZIN.")

    progress_dialog.update_progress(len(xyz_files), "Completed!")
    messagebox.showinfo("Completed", "All .xyz files have been processed.")
    progress_dialog.destroy()
    root.destroy()

    acad.prompt("Finished processing all .xyz files.")

def get_user_input(prompt):
    root = tk.Tk()
    root.withdraw()
    return simpledialog.askfloat("Input", prompt)

if __name__ == "__main__":
    script_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_directory, "xyz")  # Change this to the path of your folder containing .xyz files
    prefix = "CHD_"  # Change this to the desired prefix

    height = get_user_input("Altura do texto: ")

    if height is not None:
        load_xyz_files(folder_path, height, prefix)
    else:
        print("Invalid input. Please enter a valid number.")
        exit()

