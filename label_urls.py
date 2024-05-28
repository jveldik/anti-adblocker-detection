import csv
import os.path
import tkinter as tk
from tkinter import Frame, Button, LEFT
from PIL import Image, ImageTk

def get_urls_to_label():
    # Check if there are already some urls labeled
    if os.path.exists("data/labeled_urls.csv"):
        with open("data/labeled_urls.csv", mode = 'r', newline = '') as file:
            nr_labeled_urls = sum(1 for line in file)
    else:
        nr_labeled_urls = 0
    # Read the stored URLs, starting after the last labeled url
    with open("data/stored_urls.csv", mode='r', newline='') as file:
        reader = csv.reader(file)
        return [(row[0], row[1]) for i, row in enumerate(reader) if i >= nr_labeled_urls]
    
def save_label(url, label):
    with open("data/labeled_urls.csv", "a", newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, label])

def get_label(url, original_label, root):
    frame = Frame(root)
    frame.pack()
    text = f"Does {url} use a visible anti adblocker? \n Choose invalid, when the site is not visible."
    text_label = tk.Label(frame, text=text, font=('Helvetica 15 bold'))
    text_label.pack()
    image = Image.open(f"data/screenshots/{url}.png")
    # Resize the image
    resize_image = image.resize((1400, 700))
    img = ImageTk.PhotoImage(resize_image)
    image_label = tk.Label(frame, image=img)
    image_label.image = img
    image_label.pack()

    def save_and_next_label(response_label):
        if original_label == "True" and response_label == "False":
            response_label = None  
        save_label(url, response_label)
        frame.destroy()
        process_urls(rows, root)
    
    yes_button = Button(frame, text="Yes (space)", command=lambda: save_and_next_label(True), font=('Helvetica 12'))
    yes_button.pack(side=LEFT)
    
    no_button = Button(frame, text="No (enter)", command=lambda: save_and_next_label(False), font=('Helvetica 12'))
    no_button.pack(side=LEFT)
    
    invalid_button = Button(frame, text="Invalid (backspace)", command=lambda: save_and_next_label(None), font=('Helvetica 12'))
    invalid_button.pack(side=LEFT)
    
    exit_button = Button(frame, text="Exit (e)", command=root.destroy, font=('Helvetica 12'))
    exit_button.pack(side=LEFT)

    root.bind('<space>', lambda e: save_and_next_label(True))
    root.bind('<Return>', lambda e: save_and_next_label(False))
    root.bind('<BackSpace>', lambda e: save_and_next_label(None))
    root.bind('<e>', lambda e: root.destroy())

def process_urls(rows, root):
    if rows:
        url, original_label = rows.pop(0)
        get_label(url, original_label, root)

root = tk.Tk()
root.focus_set()
rows = get_urls_to_label()
process_urls(rows, root)
root.eval('tk::PlaceWindow . center')
root.mainloop()

with open("data/labeled_urls.csv", "r") as file:
    nr_labeled_urls = sum(1 for line in file)
print(f"You have labeled {nr_labeled_urls} urls.")
