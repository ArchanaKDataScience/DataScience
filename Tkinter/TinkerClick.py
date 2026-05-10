import tkinter as tk
from tkinter import messagebox

# Function to be called when the button is clicked
def on_button_click():
    user_input = entry.get()
    messagebox.showinfo("Information", f"You entered: {user_input}")

# Create the main application window
root = tk.Tk()
root.title("Simple Tkinter App")

# Create a label widget
label = tk.Label(root, text="Enter something:")
label.pack(pady=10)

# Create a text entry widget
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Create a button widget
button = tk.Button(root, text="Submit", command=on_button_click)
button.pack(pady=10)

# Run the application
root.mainloop()

