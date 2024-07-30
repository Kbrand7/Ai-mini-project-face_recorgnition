import os
import cv2
import face_recognition
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

# Directory to save registered faces
face_dir = 'registered_faces'
if not os.path.exists(face_dir):
    os.makedirs(face_dir)

# Text file to save attendance records
attendance_file = 'attendance.txt'

# Initialize webcam
cap = cv2.VideoCapture(0)

# Function to update the webcam feed
def update_webcam(label):
    if not label.winfo_exists():
        return
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
    label.after(10, update_webcam, label)

# Function to capture image from webcam
def capture_image():
    ret, frame = cap.read()
    if not ret:
        messagebox.showerror("Error", "Failed to capture image from webcam")
        return None
    return frame

# Function to register a new user
def register():
    def save_registration():
        registration_number = reg_number_entry.get()
        if not registration_number:
            messagebox.showwarning("Warning", "Please enter a registration number")
            return

        frame = capture_image()
        if frame is not None:
            img_path = os.path.join(face_dir, f"{registration_number}.jpg")
            cv2.imwrite(img_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # Save in BGR format
            messagebox.showinfo("Info", "Image captured and saved successfully")
            registration_window.destroy()
            root.deiconify()

    root.withdraw()
    registration_window = tk.Toplevel(root)
    registration_window.title("Register")

    tk.Label(registration_window, text="Enter Registration Number:").pack()
    reg_number_entry = tk.Entry(registration_window)
    reg_number_entry.pack()

    # Webcam feed for registration window
    webcam_label = tk.Label(registration_window)
    webcam_label.pack()
    update_webcam(webcam_label)

    tk.Button(registration_window, text="Accept", command=save_registration).pack()
    tk.Button(registration_window, text="Try Again",
              command=lambda: (registration_window.destroy(), root.deiconify())).pack()

    registration_window.mainloop()

# Function to login
def login():
    def process_login():
        frame = capture_image()
        if frame is None:
            return

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            print(f"Frame shape: {frame_rgb.shape}, dtype: {frame_rgb.dtype}")
            pil_image = Image.fromarray(frame_rgb)
            face_locations = face_recognition.face_locations(frame_rgb)
            if not face_locations:
                raise ValueError("No face detected")
            face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
            print(f"Number of faces detected: {len(face_locations)}")
            print(f"Number of face encodings generated: {len(face_encodings)}")
        except Exception as e:
            messagebox.showerror("Error", f"Face recognition failed: {e}")
            return

        if face_encodings:
            known_faces = []
            known_reg_numbers = []
            for file in os.listdir(face_dir):
                img_path = os.path.join(face_dir, file)
                img = cv2.imread(img_path)  # Load image with OpenCV for consistency
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
                if len(face_recognition.face_encodings(img_rgb)) > 0:
                    encoding = face_recognition.face_encodings(img_rgb)[0]
                    known_faces.append(encoding)
                    known_reg_numbers.append(os.path.splitext(file)[0])
                else:
                    print(f"Warning: No face detected in the image {img_path}")

            matches = face_recognition.compare_faces(known_faces, face_encodings[0])
            print(f"Matches found: {matches}")
            if True in matches:
                matched_index = matches.index(True)
                reg_number = known_reg_numbers[matched_index]
                with open(attendance_file, 'a') as f:
                    f.write(f"{reg_number}, {datetime.now()}\n")
                messagebox.showinfo("Success", "Login successful")
            else:
                messagebox.showwarning("Failed", "Unknown user! Please register or try again.")
                retry_window = tk.Toplevel(root)
                retry_window.title("Retry or Register")

                tk.Label(retry_window, text="Unknown user! Please register new user or try again.").pack()
                tk.Button(retry_window, text="Accept",
                          command=lambda: (retry_window.destroy(), root.deiconify())).pack()
                retry_window.mainloop()
        else:
            messagebox.showwarning("Failed", "No face detected")

    root.withdraw()
    login_window = tk.Toplevel(root)
    login_window.title("Login")

    # Webcam feed for login window
    webcam_label = tk.Label(login_window)
    webcam_label.pack()
    update_webcam(webcam_label)

    tk.Button(login_window, text="Capture and Login", command=process_login).pack()
    tk.Button(login_window, text="Cancel", command=lambda: (login_window.destroy(), root.deiconify())).pack()

    login_window.mainloop()

# Main application
root = tk.Tk()
root.title("Smart Attendance System")

# Webcam feed for main window
webcam_label = tk.Label(root)
webcam_label.pack()
update_webcam(webcam_label)

tk.Button(root, text="Login", command=login).pack()
tk.Button(root, text="Register New User", command=register).pack()

root.mainloop()

# Release the webcam
cap.release()
cv2.destroyAllWindows()
