import tkinter as tk
from tkinter import *
from backend.face_recognition import FaceRecognizer
from backend.student_manager import StudentManager
from backend.utils import TextToSpeech, validate_enrollment_number, validate_name
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, CARD_BG,
    INPUT_BG, INPUT_FG, TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT,
    LABEL_FONT, WINDOW_SIZE, PADDING, APP_BRAND, SUCCESS_BG, DANGER_BG,
    configure_ttk_styles
)

class RegisterWindow:
    def __init__(self, base_dir, haarcascade_path, train_path, student_details_path, model_path):
        self.base_dir = base_dir
        self.haarcascade_path = haarcascade_path
        self.train_path = train_path
        self.student_details_path = student_details_path
        self.model_path = model_path
        
        self.face_recognizer = FaceRecognizer(haarcascade_path, model_path)
        self.student_manager = StudentManager(student_details_path)
        
        self.window = tk.Tk()
        self.window.title(f"{APP_BRAND} - Register Student")
        self.window.geometry("900x540")
        self.window.configure(background=PRIMARY_BG)
        self.window.resizable(0, 0)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup registration UI"""
        # Apply theme styles
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        header = tk.Frame(self.window, bg=ACCENT_BG)
        header.pack(fill=X)
        tk.Label(header, text="👤➕  Register Your Face", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        tk.Label(header, text="Enter student details, capture images, then train", bg=ACCENT_BG, fg="#9fb5d9", font=SUBTITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        
        # Heading
        body = tk.Frame(self.window, bg=PRIMARY_BG)
        body.pack(fill=BOTH, expand=True, padx=PADDING, pady=PADDING)
        a = tk.Label(body, text="Enter the details", bg=PRIMARY_BG, fg=PRIMARY_FG, font=("Verdana", 16, "bold"))
        a.pack(anchor=W, padx=PADDING, pady=(0, PADDING))
        
        # Enrollment label and input
        form = tk.Frame(body, bg=PRIMARY_BG)
        form.pack(fill=X)
        lbl1 = tk.Label(form, text="Enrollment No", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT)
        lbl1.grid(row=0, column=0, padx=PADDING, pady=(0, PADDING), sticky=W)
        self.txt1 = tk.Entry(form, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Verdana", 18, "bold"), width=24)
        self.txt1.grid(row=0, column=1, padx=PADDING, pady=(0, 6))
        # Format hint under ID field
        self.id_hint = tk.Label(form, text="Format: 0123-0123", bg=PRIMARY_BG, fg="#98a8c4", font=("Verdana", 10, "italic"))
        self.id_hint.grid(row=1, column=1, padx=PADDING, sticky=W)
        
        # Name label and input
        lbl2 = tk.Label(form, text="Name", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT)
        lbl2.grid(row=2, column=0, padx=PADDING, pady=(0, PADDING), sticky=W)
        self.txt2 = tk.Entry(form, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Verdana", 18, "bold"), width=24)
        self.txt2.grid(row=2, column=1, padx=PADDING, pady=(0, PADDING))
        
        # Notification label
        lbl3 = tk.Label(body, text="Status", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT)
        lbl3.pack(anchor=W, padx=PADDING)
        self.message = tk.Label(body, text="", bd=0, bg=CARD_BG, fg=PRIMARY_FG, relief=FLAT, font=("Verdana", 14, "bold"), height=3)
        self.message.pack(fill=X, padx=PADDING, pady=(0, PADDING))
        
        # Buttons
        actions = tk.Frame(self.window, bg=PRIMARY_BG)
        actions.pack(fill=X, padx=PADDING, pady=PADDING)
        take_btn = tk.Button(actions, text="📸  Take Image", command=self.take_image, bd=0, font=BUTTON_FONT, bg=SUCCESS_BG, fg=ACCENT_FG, padx=24, pady=12)
        take_btn.pack(side=LEFT, padx=PADDING)
        self._add_button_hover(take_btn, SUCCESS_BG)
        train_btn = tk.Button(actions, text="⚙️  Train Image", command=self.train_image, bd=0, font=BUTTON_FONT, bg=ACCENT_BG, fg=ACCENT_FG, padx=24, pady=12)
        train_btn.pack(side=LEFT, padx=PADDING)
        self._add_button_hover(train_btn, ACCENT_BG)
    
    
    
    def take_image(self):
        """Capture student images"""
        enrollment = (self.txt1.get() or "").strip()
        name = self.txt2.get()
        
        if not enrollment or not name:
            self.message.configure(text="Enrollment & Name required!", bg="red", fg="white")
            TextToSpeech.speak("Enrollment and Name are required")
            return
        
        # Enforce strict ID format ####-####
        import re
        if not re.match(r"^\d{4}-\d{4}$", enrollment):
            self.message.configure(text="Invalid ID format. Use ####-#### (e.g., 0123-0263)", bg="red", fg="white")
            TextToSpeech.speak("Invalid ID format. Use four digits dash four digits")
            return
        
        # Basic name validation
        if not isinstance(name, str) or not name.strip():
            self.message.configure(text="Invalid name", bg="red", fg="white")
            TextToSpeech.speak("Invalid name")
            return
        
        # Prevent duplicate registration by ID
        try:
            df, _ = self.student_manager.get_all_students()
            if df is not None and enrollment in df["Enrollment"].astype(str).values:
                self.message.configure(text=f"Student with ID {enrollment} already exists", bg="red", fg="white")
                TextToSpeech.speak("Student ID already exists")
                return
        except Exception:
            pass
        
        # FIXED: Check if cascade is loaded before capturing
        if self.face_recognizer.cascade is None:
            self.message.configure(text="Cascade not loaded!", bg="red", fg="white")
            TextToSpeech.speak("Face cascade classifier failed to load")
            return
        
        sample_count, msg = self.face_recognizer.capture_faces(enrollment, name, self.train_path)
        
        if sample_count > 0:
            self.message.configure(text=msg, bg="green", fg="white")
            TextToSpeech.speak(msg)
            
            # Add student to database (string ID)
            ok, msg_add = self.student_manager.add_student(enrollment, name)
            if not ok:
                # Show error if backend rejected (duplicate or format)
                self.message.configure(text=msg_add, bg="red", fg="white")
                TextToSpeech.speak(msg_add)
                return

            # Auto-train immediately after successful capture & add
            try:
                faces, ids = self.face_recognizer.get_training_data(self.train_path)
                if len(faces) == 0:
                    self.message.configure(text="No training images found!", bg="red", fg="white")
                    TextToSpeech.speak("No training images found")
                    return
                success = self.face_recognizer.train_model(faces, ids)
                if success:
                    self.message.configure(text="Training completed successfully!", bg="green", fg="white")
                    TextToSpeech.speak("Training completed successfully")
                else:
                    self.message.configure(text="Training failed!", bg="red", fg="white")
                    TextToSpeech.speak("Training failed")
            except Exception as e:
                self.message.configure(text=f"Error during training: {str(e)}", bg="red", fg="white")
                TextToSpeech.speak(f"Error during training: {str(e)}")
        else:
            self.message.configure(text=msg, bg="red", fg="white")
            TextToSpeech.speak(msg)
    
    def train_image(self):
        """Train the model"""
        try:
            faces, ids = self.face_recognizer.get_training_data(self.train_path)
            
            if len(faces) == 0:
                self.message.configure(text="No training images found!", bg="red", fg="white")
                TextToSpeech.speak("No training images found")
                return
            
            success = self.face_recognizer.train_model(faces, ids)
            
            if success:
                self.message.configure(text="Training completed successfully!", bg="green", fg="white")
                TextToSpeech.speak("Training completed successfully")
                self.txt1.delete(0, "end")
                self.txt2.delete(0, "end")
            else:
                self.message.configure(text="Training failed!", bg="red", fg="white")
                TextToSpeech.speak("Training failed")
        
        except Exception as e:
            self.message.configure(text=f"Error: {str(e)}", bg="red", fg="white")
            TextToSpeech.speak(f"Error: {str(e)}")

    def _add_button_hover(self, btn, base_bg):
        try:
            def on_enter(e):
                btn.configure(bg=self._adjust_color(base_bg, 20))
            def on_leave(e):
                btn.configure(bg=base_bg)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        except Exception:
            pass

    def _adjust_color(self, hex_color, delta):
        try:
            original = hex_color
            hc = hex_color[1:] if hex_color.startswith("#") else hex_color
            r = max(0, min(255, int(hc[0:2], 16) + delta))
            g = max(0, min(255, int(hc[2:4], 16) + delta))
            b = max(0, min(255, int(hc[4:6], 16) + delta))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return original