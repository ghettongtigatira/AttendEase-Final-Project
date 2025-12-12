import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from backend.face_recognition import FaceRecognizer
from backend.student_manager import StudentManager
from backend.attendance_handler import AttendanceHandler
from backend.utils import TextToSpeech, validate_enrollment_number, validate_name
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, CARD_BG,
    INPUT_BG, INPUT_FG, TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT,
    LABEL_FONT, WINDOW_SIZE, PADDING, APP_BRAND, SUCCESS_BG, DANGER_BG,
    BORDER_COLOR, HIGHLIGHT, configure_ttk_styles, animate_window_in
)
import os
import cv2
from PIL import Image, ImageTk

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
        try:
            animate_window_in(self.window)
        except Exception:
            pass
        
        self.setup_ui()
        self.load_subjects()
    
    def go_back(self):
        """Go back to main window"""
        self.window.destroy()
        if self.main_window:
            self.main_window.window.deiconify()
            self.main_window.load_students_list()
    
    def setup_ui(self):
        """Setup registration UI - Modern horizontal layout"""
        # Apply theme styles
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        
        # Header
        header = tk.Frame(self.window, bg=ACCENT_BG, height=70)
        header.pack(fill=X)
        header.pack_propagate(False)
        
        header_line = tk.Frame(self.window, bg=PRIMARY_FG, height=2)
        header_line.pack(fill=X)
        
        # Back button
        back_btn = tk.Button(
            header,
            text="← Back",
            command=self.go_back,
            bd=0,
            font=("Segoe UI", 11, "bold"),
            bg=CARD_BG,
            fg=PRIMARY_FG,
            padx=16,
            pady=8,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
        )
        back_btn.pack(side=LEFT, padx=PADDING*2, pady=15)
        self._add_button_hover(back_btn, CARD_BG)
        
        # Title
        tk.Label(header, text="👤  Register Student", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING)
        tk.Label(header, text="│ Enter details and capture face", bg=ACCENT_BG, fg="#8899aa", font=("Segoe UI", 12)).pack(side=LEFT, padx=10)
        
        # Center container
        center_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        center_frame.pack(expand=True, fill=BOTH)
        
        # Main card container - WIDE horizontal layout
        card = tk.Frame(center_frame, bg=CARD_BG, padx=40, pady=30)
        card.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        # Section title
        tk.Label(card, text="Enter Student Details", bg=CARD_BG, fg=PRIMARY_FG, font=("Segoe UI", 24, "bold")).pack(pady=(0, 25))
        
        # ============== MAIN CONTENT - TWO COLUMNS ==============
        content_frame = tk.Frame(card, bg=CARD_BG)
        content_frame.pack(fill=BOTH, expand=True)
        
        # LEFT COLUMN - Form inputs
        left_col = tk.Frame(content_frame, bg=CARD_BG)
        left_col.pack(side=LEFT, fill=BOTH, padx=(0, 30))
        
        # Enrollment No
        tk.Label(left_col, text="Enrollment No", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, anchor=W).pack(anchor=W, pady=(0, 5))
        self.txt1 = tk.Entry(left_col, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Segoe UI", 13), width=28, insertbackground=INPUT_FG)
        self.txt1.pack(anchor=W, ipady=10, pady=(0, 3))
        self.id_hint = tk.Label(left_col, text="Format: 0123-0123", bg=CARD_BG, fg="#6b7a94", font=("Segoe UI", 9, "italic"))
        self.id_hint.pack(anchor=W, pady=(0, 15))
        
        # Name
        tk.Label(left_col, text="Name", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, anchor=W).pack(anchor=W, pady=(0, 5))
        self.txt2 = tk.Entry(left_col, bd=0, bg=INPUT_BG, fg=INPUT_FG, relief=FLAT, font=("Segoe UI", 13), width=28, insertbackground=INPUT_FG)
        self.txt2.pack(anchor=W, ipady=10, pady=(0, 20))
        
        # Enrolled Subjects
        tk.Label(left_col, text="Enrolled Subjects", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, anchor=W).pack(anchor=W, pady=(0, 8))
        
        subject_row = tk.Frame(left_col, bg=CARD_BG)
        subject_row.pack(anchor=W, pady=(0, 8))
        
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(subject_row, textvariable=self.subject_var, state="readonly", width=18, font=("Segoe UI", 11))
        self.subject_combo.pack(side=LEFT, padx=(0, 10), ipady=3)
        
        add_subject_btn = tk.Button(subject_row, text="➕ Add", command=self.add_subject_to_list, bd=0, font=("Segoe UI", 10, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG, padx=14, pady=5, cursor="hand2")
        add_subject_btn.pack(side=LEFT, padx=(0, 8))
        self._add_button_hover(add_subject_btn, PRIMARY_FG)
        
        clear_btn = tk.Button(subject_row, text="🧹 Clear", command=self.clear_subjects, bd=0, font=("Segoe UI", 10), bg=ACCENT_BG, fg=ACCENT_FG, padx=12, pady=5, cursor="hand2")
        clear_btn.pack(side=LEFT)
        self._add_button_hover(clear_btn, ACCENT_BG)
        
        self.subjects_display = tk.Label(left_col, text="No subjects selected", bg=INPUT_BG, fg="#6b7a94", font=("Segoe UI", 10), anchor=W, padx=10, pady=8, width=35)
        self.subjects_display.pack(anchor=W)
        
        # RIGHT COLUMN - ID Photo & Status
        right_col = tk.Frame(content_frame, bg=CARD_BG)
        right_col.pack(side=LEFT, fill=BOTH)
        
        # ID Photo Section - Modern card design
        tk.Label(right_col, text="ID Photo (Optional)", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, anchor=W).pack(anchor=W, pady=(0, 10))
        
        # ID Photo card with border
        id_photo_card = tk.Frame(right_col, bg=INPUT_BG, highlightthickness=1, highlightbackground=BORDER_COLOR, padx=15, pady=15)
        id_photo_card.pack(anchor=W, pady=(0, 20))
        
        # Photo preview - centered, larger
        self.id_photo_preview_frame = tk.Frame(id_photo_card, bg="#0a1628", width=120, height=120, highlightthickness=2, highlightbackground=PRIMARY_FG)
        self.id_photo_preview_frame.pack(pady=(0, 12))
        self.id_photo_preview_frame.pack_propagate(False)
        
        self.id_photo_label = tk.Label(self.id_photo_preview_frame, text="👤", bg="#0a1628", fg="#3d5a80", font=("Segoe UI", 36))
        self.id_photo_label.pack(expand=True, fill=BOTH)
        
        # Buttons row - horizontal below photo
        id_btn_row = tk.Frame(id_photo_card, bg=INPUT_BG)
        id_btn_row.pack()
        
        capture_id_btn = tk.Button(id_btn_row, text="📸", command=self.capture_id_photo, bd=0, font=("Segoe UI", 14), bg=PRIMARY_FG, fg=PRIMARY_BG, padx=12, pady=6, cursor="hand2")
        capture_id_btn.pack(side=LEFT, padx=(0, 8))
        self._add_button_hover(capture_id_btn, PRIMARY_FG)
        
        upload_id_btn = tk.Button(id_btn_row, text="📁", command=self.upload_id_photo, bd=0, font=("Segoe UI", 14), bg=ACCENT_BG, fg=ACCENT_FG, padx=12, pady=6, cursor="hand2")
        upload_id_btn.pack(side=LEFT, padx=(0, 8))
        self._add_button_hover(upload_id_btn, ACCENT_BG)
        
        clear_id_btn = tk.Button(id_btn_row, text="🗑️", command=self.clear_id_photo, bd=0, font=("Segoe UI", 14), bg="#1a2a3f", fg="#6b7a94", padx=12, pady=6, cursor="hand2")
        clear_id_btn.pack(side=LEFT)
        self._add_button_hover(clear_id_btn, "#1a2a3f")
        
        # Store the captured/uploaded photo path temporarily
        self.temp_id_photo_path = None
        self.temp_id_photo_image = None
        
        # Status Section
        tk.Label(right_col, text="Status", bg=CARD_BG, fg=ACCENT_FG, font=LABEL_FONT, anchor=W).pack(anchor=W, pady=(0, 8))
        self.message = tk.Label(right_col, text="Ready to capture", bd=0, bg=INPUT_BG, fg=PRIMARY_FG, relief=FLAT, font=("Segoe UI", 11), height=2, anchor=W, padx=12, width=30)
        self.message.pack(anchor=W)
        
        # ============== ACTION BUTTONS - Bottom Center ==============
        actions = tk.Frame(card, bg=CARD_BG)
        actions.pack(pady=(25, 5))
        
        take_btn = tk.Button(actions, text="📸  Take Image", command=self.take_image, bd=0, font=BUTTON_FONT, bg=PRIMARY_FG, fg=PRIMARY_BG, padx=35, pady=14, cursor="hand2")
        take_btn.pack(side=LEFT, padx=(0, 20))
        self._add_button_hover(take_btn, PRIMARY_FG)
        
        train_btn = tk.Button(actions, text="⚙️  Train Image", command=self.train_image, bd=0, font=BUTTON_FONT, bg=PRIMARY_FG, fg=PRIMARY_BG, padx=35, pady=14, cursor="hand2")
        train_btn.pack(side=LEFT)
        self._add_button_hover(train_btn, PRIMARY_FG)
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
    
    # ============== ID PHOTO METHODS ==============
    
    def capture_id_photo(self):
        """Capture ID photo from camera"""
        enrollment = (self.txt1.get() or "").strip()
        
        if not enrollment:
            self.message.configure(text="Enter Enrollment No first!", bg="red", fg="white")
            return
        
        # Validate enrollment format
        import re
        if not re.match(r"^\d{4}-\d{4}$", enrollment):
            self.message.configure(text="Invalid ID format. Use ####-#### (e.g., 0123-0263)", bg="red", fg="white")
            return
        
        self.message.configure(text="Opening camera... Press SPACE to capture, ESC to cancel", bg=INPUT_BG, fg=PRIMARY_FG)
        self.window.update()
        
        # Use the backend method to capture
        success, msg, captured_image = self.student_manager.capture_id_photo_from_camera(
            enrollment, 
            self.haarcascade_path
        )
        
        if success and captured_image is not None:
            self.temp_id_photo_image = captured_image
            self.temp_id_photo_path = None  # Clear file path since we have image
            self.update_id_photo_preview(captured_image)
            self.message.configure(text="ID photo captured! It will be saved when you register.", bg="green", fg="white")
        else:
            self.message.configure(text=msg, bg="red" if not success else INPUT_BG, fg="white" if not success else PRIMARY_FG)
    
    def upload_id_photo(self):
        """Upload ID photo from file"""
        enrollment = (self.txt1.get() or "").strip()
        
        if not enrollment:
            self.message.configure(text="Enter Enrollment No first!", bg="red", fg="white")
            return
        
        # Validate enrollment format
        import re
        if not re.match(r"^\d{4}-\d{4}$", enrollment):
            self.message.configure(text="Invalid ID format. Use ####-#### (e.g., 0123-0263)", bg="red", fg="white")
            return
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select ID Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load and preview the image
                img = Image.open(file_path)
                self.temp_id_photo_path = file_path
                self.temp_id_photo_image = None  # Clear camera image since we have file
                
                # Convert PIL image to format suitable for preview
                self.update_id_photo_preview_from_pil(img)
                self.message.configure(text="ID photo loaded! It will be saved when you register.", bg="green", fg="white")
            except Exception as e:
                self.message.configure(text=f"Error loading image: {str(e)}", bg="red", fg="white")
    
    def update_id_photo_preview(self, cv2_image):
        """Update the ID photo preview from a cv2 image"""
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(image_rgb)
            self.update_id_photo_preview_from_pil(img)
        except Exception as e:
            self.message.configure(text=f"Error displaying preview: {str(e)}", bg="red", fg="white")
    
    def update_id_photo_preview_from_pil(self, pil_image):
        """Update the ID photo preview from a PIL image"""
        try:
            # Resize to fit preview frame (100x100)
            pil_image.thumbnail((96, 96), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update label
            self.id_photo_label.configure(image=photo, text="")
            self.id_photo_label.image = photo  # Keep reference
        except Exception as e:
            self.message.configure(text=f"Error displaying preview: {str(e)}", bg="red", fg="white")
    
    def clear_id_photo(self):
        """Clear the selected ID photo"""
        self.temp_id_photo_path = None
        self.temp_id_photo_image = None
        self.id_photo_label.configure(image="", text="�", font=("Segoe UI", 36), fg="#3d5a80")
        self.id_photo_label.image = None
        self.message.configure(text="ID photo cleared", bg=INPUT_BG, fg=PRIMARY_FG)
    
    def save_id_photo_for_student(self, enrollment):
        """Save the captured/uploaded ID photo for the student"""
        try:
            if self.temp_id_photo_path:
                # Save from file
                success, msg = self.student_manager.save_id_photo(enrollment, self.temp_id_photo_path, is_file_path=True)
                return success, msg
            elif self.temp_id_photo_image is not None:
                # Save from camera capture
                success, msg = self.student_manager.save_id_photo(enrollment, self.temp_id_photo_image, is_file_path=False)
                return success, msg
            return True, "No ID photo to save"
        except Exception as e:
            return False, f"Error saving ID photo: {str(e)}"

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
            
            # Save ID photo if captured/uploaded
            id_photo_ok, id_photo_msg = self.save_id_photo_for_student(enrollment)
            if not id_photo_ok:
                self.message.configure(text=f"Warning: {id_photo_msg}", bg="#f59e0b", fg="white")

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
                # Clear ID photo preview
                self.clear_id_photo()
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