import tkinter as tk
from tkinter import *
from tkinter import ttk
from backend.face_recognition import FaceRecognizer
from backend.student_manager import StudentManager
from backend.attendance_handler import AttendanceHandler
from backend.utils import TextToSpeech, validate_enrollment_number, validate_name
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, CARD_BG,
    INPUT_BG, INPUT_FG, TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT,
    LABEL_FONT, WINDOW_SIZE, PADDING, APP_BRAND, SUCCESS_BG, DANGER_BG,
    configure_ttk_styles
)
import os

class RegisterWindow:
    def __init__(self, base_dir, haarcascade_path, train_path, student_details_path, model_path, main_window=None):
        self.base_dir = base_dir
        self.haarcascade_path = haarcascade_path
        self.train_path = train_path
        self.student_details_path = student_details_path
        self.model_path = model_path
        self.attendance_path = os.path.join(base_dir, "Attendance")
        self.main_window = main_window
        
        self.face_recognizer = FaceRecognizer(haarcascade_path, model_path)
        self.student_manager = StudentManager(student_details_path)
        self.attendance_handler = AttendanceHandler(self.attendance_path, student_details_path)
        
        # Selected subjects list
        self.selected_subjects = []
        
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - Register Student")
        self.window.configure(background=PRIMARY_BG)
        self.window.overrideredirect(True)  # Borderless
        # Set fullscreen manually (get screen dimensions)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.bind('<Escape>', lambda e: self.go_back())  # Back on Escape
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)
        
        self.setup_ui()
        self.load_subjects()
    
    def go_back(self):
        """Go back to main window"""
        self.window.destroy()
        if self.main_window:
            self.main_window.window.deiconify()
            self.main_window.load_students_list()
    
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
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back",
            command=self.go_back,
            bd=0,
            font=("Verdana", 12, "bold"),
            bg=ACCENT_BG,
            fg=PRIMARY_FG,
            padx=16,
            pady=6,
            cursor="hand2"
        )
        back_btn.pack(side=RIGHT, padx=PADDING, pady=PADDING)
        self._add_button_hover(back_btn, ACCENT_BG)
        
        # Center container
        center_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        center_frame.pack(expand=True, fill=BOTH)
        
        # Card container (centered)
        card = tk.Frame(center_frame, bg=CARD_BG, padx=40, pady=30)
        card.place(relx=0.5, rely=0.45, anchor=CENTER)
        
        # Section title
        tk.Label(card, text="Enter Student Details", bg=CARD_BG, fg=PRIMARY_FG, font=("Verdana", 20, "bold")).pack(pady=(0, 20))
        
        # Form container
        form = tk.Frame(card, bg=CARD_BG)
        form.pack(pady=(0, 15))
        
        # Enrollment label and input
        lbl1 = tk.Label(form, text="Enrollment No", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, width=14, anchor=W)
        lbl1.grid(row=0, column=0, pady=8, padx=(0, 15), sticky=W)
        self.txt1 = tk.Entry(form, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Verdana", 14), width=25, insertbackground=INPUT_FG)
        self.txt1.grid(row=0, column=1, pady=8, ipady=8, sticky=W)
        # Format hint
        self.id_hint = tk.Label(form, text="Format: 0123-0123", bg=CARD_BG, fg="#6b7a94", font=("Verdana", 9, "italic"))
        self.id_hint.grid(row=1, column=1, sticky=W)
        
        # Name label and input
        lbl2 = tk.Label(form, text="Name", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, width=14, anchor=W)
        lbl2.grid(row=2, column=0, pady=(15, 8), padx=(0, 15), sticky=W)
        self.txt2 = tk.Entry(form, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Verdana", 14), width=25, insertbackground=INPUT_FG)
        self.txt2.grid(row=2, column=1, pady=(15, 8), ipady=8, sticky=W)
        
        # Subject selection section
        subject_section = tk.Frame(card, bg=CARD_BG)
        subject_section.pack(fill=X, pady=(10, 0))
        
        tk.Label(subject_section, text="Enrolled Subjects", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT).pack(anchor=W, pady=(0, 8))
        
        # Subject selection row
        subject_row = tk.Frame(subject_section, bg=CARD_BG)
        subject_row.pack(fill=X)
        
        # Subject dropdown
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(subject_row, textvariable=self.subject_var, state="readonly", width=20, font=("Verdana", 11))
        self.subject_combo.pack(side=LEFT, padx=(0, 10))
        
        # Add subject button
        add_subject_btn = tk.Button(subject_row, text="+ Add", command=self.add_subject_to_list, bd=0, font=("Verdana", 10, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG, padx=12, pady=4, cursor="hand2")
        add_subject_btn.pack(side=LEFT, padx=(0, 10))
        self._add_button_hover(add_subject_btn, PRIMARY_FG)
        
        # Clear all button
        clear_btn = tk.Button(subject_row, text="Clear All", command=self.clear_subjects, bd=0, font=("Verdana", 10), bg=ACCENT_BG, fg=ACCENT_FG, padx=10, pady=4, cursor="hand2")
        clear_btn.pack(side=LEFT)
        self._add_button_hover(clear_btn, ACCENT_BG)
        
        # Selected subjects display
        self.subjects_display = tk.Label(subject_section, text="No subjects selected", bg=INPUT_BG, fg="#6b7a94", font=("Verdana", 10), anchor=W, padx=10, pady=8)
        self.subjects_display.pack(fill=X, pady=(8, 0))
        
        # Status section
        status_frame = tk.Frame(card, bg=CARD_BG)
        status_frame.pack(fill=X, pady=(15, 0))
        tk.Label(status_frame, text="Status", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT).pack(anchor=W, pady=(0, 6))
        self.message = tk.Label(status_frame, text="Ready to capture", bd=0, bg=INPUT_BG, fg=PRIMARY_FG, relief=FLAT, font=("Verdana", 11), height=2, anchor=W, padx=10)
        self.message.pack(fill=X)
        
        # Buttons
        actions = tk.Frame(card, bg=CARD_BG)
        actions.pack(pady=(20, 0))
        take_btn = tk.Button(actions, text="📸  Take Image", command=self.take_image, bd=0, font=BUTTON_FONT, bg=PRIMARY_FG, fg=PRIMARY_BG, padx=24, pady=12, cursor="hand2")
        take_btn.pack(side=LEFT, padx=(0, 15))
        self._add_button_hover(take_btn, PRIMARY_FG)
        train_btn = tk.Button(actions, text="⚙️  Train Image", command=self.train_image, bd=0, font=BUTTON_FONT, bg=PRIMARY_FG, fg=PRIMARY_BG, padx=24, pady=12, cursor="hand2")
        train_btn.pack(side=LEFT)
        self._add_button_hover(train_btn, PRIMARY_FG)
    
    def load_subjects(self):
        """Load available subjects into dropdown"""
        subjects, _ = self.attendance_handler.list_subjects()
        self.subject_combo["values"] = subjects if subjects else []
        if subjects:
            self.subject_combo.current(0)
    
    def add_subject_to_list(self):
        """Add selected subject to the student's enrolled subjects"""
        subject = self.subject_var.get().strip()
        if not subject:
            return
        if subject in self.selected_subjects:
            self.message.configure(text=f"'{subject}' already added", bg=INPUT_BG, fg="#f59e0b")
            return
        self.selected_subjects.append(subject)
        self.update_subjects_display()
        self.message.configure(text=f"Added '{subject}'", bg=INPUT_BG, fg=PRIMARY_FG)
    
    def clear_subjects(self):
        """Clear all selected subjects"""
        self.selected_subjects = []
        self.update_subjects_display()
        self.message.configure(text="Subjects cleared", bg=INPUT_BG, fg=PRIMARY_FG)
    
    def update_subjects_display(self):
        """Update the display of selected subjects"""
        if self.selected_subjects:
            display_text = ", ".join(self.selected_subjects)
            self.subjects_display.configure(text=display_text, fg=PRIMARY_FG)
        else:
            self.subjects_display.configure(text="No subjects selected", fg="#6b7a94")
    
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
            
            # Add student to database (string ID) with enrolled subjects
            ok, msg_add = self.student_manager.add_student(enrollment, name, self.selected_subjects)
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
                # Clear selected subjects
                self.selected_subjects = []
                self.update_subjects_display()
            else:
                self.message.configure(text="Training failed!", bg="red", fg="white")
                TextToSpeech.speak("Training failed")
        
        except Exception as e:
            self.message.configure(text=f"Error: {str(e)}", bg="red", fg="white")
            TextToSpeech.speak(f"Error: {str(e)}")

    def _add_button_hover(self, btn, base_bg, darken=False):
        try:
            delta = -20 if darken else 20
            def on_enter(e):
                btn.configure(bg=self._adjust_color(base_bg, delta))
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