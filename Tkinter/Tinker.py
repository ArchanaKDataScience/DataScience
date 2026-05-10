import tkinter as tk
# Function to be called when the button is clicked
def on_button_click():
    label.config(text="Button clicked!")

# Create the main application window
root = tk.Tk()
root.title("Simple Tkinter App")

# Create a label widget
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=20)

# Create a button widget
button = tk.Button(root, text="Click Me", command=on_button_click)
button.pack(pady=20)

# Run the application
root.mainloop()