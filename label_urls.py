import csv
import tkinter as tk
from tkinter import Frame, PhotoImage, Button, LEFT, BOTH
from PIL import Image,ImageTk
import os.path

def get_urls_to_label():
    # Check if there are already some urls labeled
    if os.path.exists("data/labeled_urls.csv"):
        # Read the last URL from labeled_urls.csv
        with open("data/labeled_urls.csv", mode = 'r', newline = '') as file:
            reader = csv.reader(file)
            last_labeled_url = [row for row in reader][-1][0]
        # Read the URLs from stored_urls.csv, starting after the last labeled URL
        with open("data/stored_urls.csv", mode = 'r', newline = '') as file:
            reader = csv.reader(file)
            while next(reader)[0] != last_labeled_url:
                pass
            return [row for row in reader if row[1]]
    else:
        # Make a csv file to store labeled urls
        with open("data/labeled_urls.csv", "w", newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "AntiAdblocker"])
        with open("data/stored_urls.csv", mode = 'r', newline = '') as file:
            reader = csv.reader(file)
            # Skip the header
            next(reader)
            return [row for row in reader if row[1]]

def save_label(url, label):
    with open("data/labeled_urls.csv", "a", newline = '') as file:
        writer = csv.writer(file)
        writer.writerow([url, label])

def get_label(url, redirect, root):
    frame = Frame(root)
    frame.pack()
    text = f"Does {url}, redirected to {redirect}, use a visible anti adblocker? \n Choose invalid, when the site is not visible or the redirect is too different."
    text_label = tk.Label(frame, text = text, font = ('Helvetica 15 bold'))
    text_label.pack()
    image = Image.open(f"data/screenshots/{url}.png")
    # Resize the image
    resize_image = image.resize((1440, 690))
    img = ImageTk.PhotoImage(resize_image)
    image_label = tk.Label(frame, image = img)
    image_label.image = img
    image_label.pack()

    def next_label():
        frame.destroy()
        process_urls(rows, root)

    def save_and_next_label(label):
        save_label(url, label)
        next_label()
    
    yes_button = Button(frame, text = "Yes (space)", command = lambda: save_and_next_label(True), font = ('Helvetica 12'))
    yes_button.pack(side = LEFT)
    
    no_button = Button(frame, text = "No (enter)", command = lambda: save_and_next_label(False), font = ('Helvetica 12'))
    no_button.pack(side = LEFT)
    
    invalid_button = Button(frame, text = "Invalid (backspace)", command = next_label, font = ('Helvetica 12'))
    invalid_button.pack(side = LEFT)
    
    exit_button = Button(frame, text = "Exit (e)", command = root.destroy, font = ('Helvetica 12'))
    exit_button.pack(side = LEFT)

    # Bind key events to the root window
    root.bind('<space>', lambda e: save_and_next_label(True))
    root.bind('<Return>', lambda e: save_and_next_label(False))
    root.bind('<BackSpace>', lambda e: next_label())
    root.bind('<e>', lambda e: root.destroy())

def process_urls(rows, root):
    if rows:
        url, redirect = rows.pop(0)
        get_label(url, redirect, root)

root = tk.Tk()
root.focus_set()
rows = get_urls_to_label()
process_urls(rows, root)
root.eval('tk::PlaceWindow . center')
root.mainloop()
# Count labeled urls
with open("data/labeled_urls.csv", "r") as file:
    nr_labeled_urls = sum(1 for line in file)-1
print(f"You have labeled {nr_labeled_urls} urls.")
