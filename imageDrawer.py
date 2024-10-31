import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import turtle
import math
import os

class ContourLevelAdjuster:
    def __init__(self, root):
        self.root = root
        self.root.title("Contour Level Adjuster")
        
        # Initialize image path
        self.image_path = ""
        self.low_threshold = 50
        self.high_threshold = 150
        self.contours = []
        # Create a label to display the image
        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Create sliders for low and high thresholds with labels
        low_label = tk.Label(self.root, text="Low Threshold:")
        low_label.grid(row=1, column=0, sticky='e', padx=5)

        self.low_slider = ttk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_Low_thresholds)
        self.low_slider.set(50)  # Default value
        self.low_slider.grid(row=1, column=1, sticky='we', padx=5)

        high_label = tk.Label(self.root, text="High Threshold:")
        high_label.grid(row=2, column=0, sticky='e', padx=5)

        self.high_slider = ttk.Scale(self.root, from_=0, to=255, orient='horizontal', command=self.update_High_thresholds)
        self.high_slider.set(150)  # Default value
        self.high_slider.grid(row=2, column=1, sticky='we', padx=5)

        # Add entry for jump threshold
        jump_label = tk.Label(self.root, text="Jump Threshold:")
        jump_label.grid(row=3, column=0, sticky='e', padx=5)

        self.jump_entry = tk.Entry(self.root)
        self.jump_entry.insert(0, "30")  # Default value
        self.jump_entry.grid(row=3, column=1, sticky='we', padx=5)

        # Add buttons for selecting image, saving contours, drawing, and closing the app
        select_button = ttk.Button(self.root, text="Select Image", command=self.select_image)
        select_button.grid(row=4, column=0, sticky='we', padx=5, pady=5)

        save_button = ttk.Button(self.root, text="Save Contours", command=self.save_contours)
        save_button.grid(row=4, column=1, sticky='we', padx=5, pady=5)

        draw_button = ttk.Button(self.root, text="Draw", command=self.draw_contours)
        draw_button.grid(row=4, column=2, sticky='we', padx=5, pady=5)

        close_button = ttk.Button(self.root, text="Close", command=self.close_app)
        close_button.grid(row=4, column=3, sticky='we', padx=5, pady=5)

        # Configure grid to make sliders and buttons expand
        self.root.grid_columnconfigure(1, weight=1)

    def process_image(self, low_threshold, high_threshold):
        if not self.image_path:
            return

        # Load and process the image
        image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)

        # Resize the image if it's larger than the max dimensions
        max_width, max_height = 700, 500
        height, width = image.shape
        if width > max_width or height > max_height:
            scaling_factor = min(max_width / width, max_height / height)
            new_size = (int(width * scaling_factor), int(height * scaling_factor))
            image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(image, (5, 5), 0)

        # Perform edge detection using Canny with adjustable thresholds
        edges = cv2.Canny(blurred, low_threshold, high_threshold)

        # Convert edges to a format suitable for Tkinter display
        edges_display = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        edges_image = Image.fromarray(edges_display)
        edges_photo = ImageTk.PhotoImage(edges_image)

        # Update the label with the new image
        self.image_label.config(image=edges_photo)
        self.image_label.image = edges_photo

        # Find contours with RETR_TREE to capture hierarchical structure
        self.contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # Save detailed points (without contour approximation)
        
    def update_High_thresholds(self, *args):
        self.high_threshold = self.high_slider.get()
        self.process_image(self.low_threshold, self.high_threshold)

    def update_Low_thresholds(self, *args):
        self.low_threshold = self.low_slider.get()
        self.process_image(self.low_threshold, self.high_threshold)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if self.image_path:
            self.process_image(self.low_slider.get(), self.high_slider.get())

    def save_contours(self):
        if not self.image_path or not hasattr(self, 'contours'):
            print("No contours to save.")
            return

        detailed_points = []
        for contour in self.contours:
            for point in contour:
                x, y = point[0]
                detailed_points.append((x, y))  

        # Ensure the "contours" directory exists
        contours_dir = os.path.join(os.path.dirname(__file__), "contours")
        os.makedirs(contours_dir, exist_ok=True)

        # Construct the file path
        base_name = os.path.basename(self.image_path).split(".")[0]
        file_path = os.path.join(contours_dir, f"{base_name}_detailed_contour.txt")

        # Save points to a file for use with Turtle
        with open(file_path, "w") as file:
            for point in detailed_points:
                file.write(f"{point[0]},{point[1]}\n")
        print("Contours saved successfully.")

    def draw_contours(self):
        # Load contour points
        detailed_points = []
        try:
            with open("..\\contours\\" + self.image_path.split(".")[0] + "_detailed_contour.txt", "r") as file:
                for line in file:
                    x, y = map(int, line.strip().split(','))
                    detailed_points.append((x, y))
        except FileNotFoundError:
            print("Contour file not found. Please save contours first.")
            return

        # Calculate the center offset
        min_x = min(point[0] for point in detailed_points)
        max_x = max(point[0] for point in detailed_points)
        min_y = min(point[1] for point in detailed_points)
        max_y = max(point[1] for point in detailed_points)

        offset_x = (max_x + min_x) / 2
        offset_y = (max_y + min_y) / 2

        # Get the jump threshold from the entry box
        try:
            distance_threshold = int(self.jump_entry.get())
        except ValueError:
            print("Invalid jump threshold value. Using default of 30.")
            distance_threshold = 10

        # Reinitialize Turtle graphics
        screen = turtle.Screen()
        screen.setup(width=800, height=600)
        screen.title("Contour Drawing")
        screen.bgcolor("white")

        pen = turtle.Turtle()
        pen.speed(0)  
        pen.penup()  

        # Move to the first point adjusted for centering
        first_point = detailed_points[0]
        pen.goto(first_point[0] - offset_x, -(first_point[1] - offset_y))
        pen.pendown()

        for i in range(1, len(detailed_points)):
            x_prev, y_prev = detailed_points[i - 1]
            x, y = detailed_points[i]
            
            distance = math.sqrt((x - x_prev) ** 2 + (y - y_prev) ** 2)
            
            if distance > distance_threshold:
                pen.penup()
            else:
                pen.pendown()
            
            pen.goto(x - offset_x, -(y - offset_y))

        pen.hideturtle()
        turtle.done()


    def close_app(self):
        self.root.destroy()

# Create the main window and run the application
root = tk.Tk()
app = ContourLevelAdjuster(root)
root.mainloop()

