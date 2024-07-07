import pandas as pd
import tkinter as tk
from tkinter import Frame, Button, LEFT
from PIL import Image, ImageTk

def get_urls_to_label(df):
    # Ensure 'manual' column exists and count already labeled URLs
    if 'manual' in df.columns:
        nr_labeled_urls = df['manual'].notna().sum()
    else:
        df['manual'] = None
        nr_labeled_urls = 0

    # Split the URLs into true and false and interleave them
    true_urls = df[df['keywords'] == True].values.tolist()
    false_urls = df[df['keywords'] == False].values.tolist()
    min_len = min(len(true_urls), len(false_urls))
    interleaved_urls = [val for pair in zip(true_urls[:min_len], false_urls[:min_len]) for val in pair]

    # Return the interleaved urls, starting after the last labeled URL
    return interleaved_urls[nr_labeled_urls:]
    
def save_label(df, url, label):
    index = df[df.iloc[:, 0] == url].index[0]
    df.at[index, 'manual'] = label

def get_label(df, rows, url, original_label, root):
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
        if original_label == "True" and response_label == False:
            response_label = None
        save_label(df, url, response_label)
        frame.destroy()
        process_urls(df, rows, root)
    
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

def process_urls(df, rows, root):
    if rows:
        url, original_label, _ = rows.pop(0)
        get_label(df, rows, url, original_label, root)

if __name__ == "__main__":
    df = pd.read_csv("data/stored_urls.csv")
    rows = get_urls_to_label(df)

    root = tk.Tk()
    root.focus_set()

    process_urls(df, rows, root)

    root.eval('tk::PlaceWindow . center')
    root.mainloop()

    df.to_csv("data/stored_urls.csv", index=False)
    nr_labeled_urls = df['manual'].notna().sum()
    print(f"You have labeled {nr_labeled_urls} urls.")
