import tkinter as tk
from tkinter import *
from tkinter import messagebox
import os
from backend.attendance_logic import AttendanceLogic
from backend.utils import TextToSpeech
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG,
    SUCCESS_BG, CARD_BG, INPUT_BG, INPUT_FG, DANGER_BG,
    TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LABEL_FONT,
    WINDOW_SIZE, PADDING, BUTTON_SIZE, APP_BRAND, BORDER_COLOR, HIGHLIGHT,
    configure_ttk_styles, animate_window_in,
)

class AttendanceWindow:
    def __init__(self, base_dir, haarcascade_path, train_path, student_details_path, model_path, main_window=None):
        self.base_dir = base_dir
        self.haarcascade_path = haarcascade_path
        self.train_path = train_path
        self.student_details_path = student_details_path
        self.model_path = model_path
        self.main_window = main_window
        
        # Initialize logic handler
        self.logic = AttendanceLogic(
            base_dir, haarcascade_path, train_path, 
            student_details_path, model_path
        )
        
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - Take Attendance")
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
    
    def go_back(self):
        """Go back to main window"""
        self.window.destroy()
        if self.main_window:
            self.main_window.window.deiconify()
    
    def setup_ui(self):
        """Setup attendance UI"""
        # Apply theme styles consistently
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
        tk.Label(header, text="📸  Take Attendance", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING)
        tk.Label(header, text="│ Select subject and start session", bg=ACCENT_BG, fg="#8899aa", font=("Segoe UI", 12)).pack(side=LEFT, padx=10)
        
        # Center container
        center_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        center_frame.pack(expand=True, fill=BOTH)
        
        # Card container (centered)
        card = tk.Frame(center_frame, bg=CARD_BG, padx=50, pady=35, highlightthickness=1, highlightbackground=BORDER_COLOR)
        card.place(relx=0.5, rely=0.45, anchor=CENTER)
        
        # Card title
        tk.Label(card, text="Attendance Session", bg=CARD_BG, fg=PRIMARY_FG, font=("Segoe UI", 20, "bold")).pack(pady=(0, 25))
        
        # Two column layout
        columns = tk.Frame(card, bg=CARD_BG)
        columns.pack(fill=X)
        
        # Left column - Subject selection
        left = tk.Frame(columns, bg=CARD_BG)
        left.pack(side=LEFT, padx=(0, 40))
        
        tk.Label(left, text="Subject", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=(0, 8))
        
        from tkinter import ttk
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(left, textvariable=self.subject_var, state="readonly", width=28, font=("Segoe UI", 11))
        self.subject_combo.pack(anchor=W, pady=(0, 12))
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_subject_selected)
        
        confirm_btn = tk.Button(
            left,
            text="✅  Confirm Subject",
            command=self.on_confirm_subject,
            bd=0,
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT_BG,
            fg=ACCENT_FG,
            padx=16,
            pady=8,
            cursor="hand2"
        )
        confirm_btn.pack(anchor=W)
        self._add_button_hover(confirm_btn, ACCENT_BG)
        
        # Right column - Status
        right = tk.Frame(columns, bg=CARD_BG)
        right.pack(side=LEFT)
        
        tk.Label(right, text="Status", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 12, "bold")).pack(anchor=W, pady=(0, 8))
        
        self.message = tk.Label(
            right,
            text="Select a subject to begin",
            bd=0,
            bg=INPUT_BG,
            fg=PRIMARY_FG,
            font=("Segoe UI", 11),
            height=3,
            width=30,
            relief=FLAT,
            anchor=W,
            padx=12
        )
        self.message.pack(fill=X)
        
        # Action buttons
        actions = tk.Frame(card, bg=CARD_BG)
        actions.pack(pady=(30, 0))
        
        self.start_btn = tk.Button(
            actions,
            text="▶️  Start Attendance",
            command=self.on_start_attendance,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=24,
            pady=12,
            cursor="hand2"
        )
        self.start_btn.pack(side=LEFT, padx=(0, 15))
        self._add_button_hover(self.start_btn, PRIMARY_FG)
        
        stop_btn = tk.Button(
            actions,
            text="⏹️  Stop Attendance",
            command=self.stop_attendance,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=24,
            pady=12,
            cursor="hand2"
        )
        stop_btn.pack(side=LEFT)
        self._add_button_hover(stop_btn, DANGER_BG, darken=True)

        # Seed default subjects and populate dropdown
        self.seed_and_load_subjects()
    
    def on_start_attendance(self):
        """Handle start attendance button"""
        # Use combobox text to ensure selected subject is captured
        subject = (self.subject_combo.get() or "").strip()
        
        if not subject:
            self.update_message("Please enter subject name!", "red", "white")
            TextToSpeech.speak("Please enter subject name")
            return
        
        # Show chosen subject in status for clarity
        self.update_message(f"Starting for {subject}...", CARD_BG, PRIMARY_FG)
        # Call logic handler
        success, student_count, message = self.logic.start_attendance(subject)
        
        if success:
            self.update_message(f"{message} - {student_count} students", "green", "black")
            TextToSpeech.speak(f"{message}. {student_count} students marked present.")
        else:
            self.update_message(message, "red", "white")
            TextToSpeech.speak(message)

    def seed_and_load_subjects(self):
        """Seed default subjects if missing and load subjects into dropdown"""
        # Prioritize CMSC 310 at the top of seeded subjects
        defaults = [
            "CMSC 310","CSST 102","CSST 101","CMSC 307",
            "CMSC 3O9","CMSC 306","CMSC 305","CMSC 308",
        ]
        # Add subjects to registry
        for s in defaults:
            try:
                self.logic.attendance_handler.add_subject(s)
            except Exception:
                pass
        # Load into dropdown
        subjects, _ = self.logic.attendance_handler.list_subjects()
        # Ensure CMSC 310 appears first if present
        ordered = []
        if subjects:
            ordered = (["CMSC 310"] if "CMSC 310" in subjects else []) + [s for s in subjects if s != "CMSC 310"]
        self.subject_combo["values"] = ordered or subjects
        # Do NOT auto-select; require explicit user choice
        self.subject_var.set("")
        # Disable start until a subject is picked
        try:
            self.start_btn.configure(state=DISABLED)
        except Exception:
            pass

    def on_subject_selected(self, event=None):
        """Enable start button and clear status when subject is chosen"""
        # Read current combobox text to ensure selection is captured
        if (self.subject_combo.get() or "").strip():
            try:
                self.start_btn.configure(state=NORMAL)
            except Exception:
                pass
        self.update_message("", CARD_BG, PRIMARY_FG)

    def on_confirm_subject(self):
        """Confirm the currently selected subject and provide feedback"""
        # Use combobox text (visible selection) rather than variable alone
        subject = (self.subject_combo.get() or "").strip()
        if not subject:
            self.update_message("Please select a subject to confirm.", "red", "white")
            TextToSpeech.speak("Please select a subject to confirm")
            try:
                self.start_btn.configure(state=DISABLED)
            except Exception:
                pass
            return
        # Provide confirmation feedback and ensure Start is enabled
        self.update_message(f"Subject confirmed: {subject}", CARD_BG, PRIMARY_FG)
        TextToSpeech.speak(f"Subject {subject} confirmed")
        try:
            self.start_btn.configure(state=NORMAL)
        except Exception:
            pass
    
    def update_message(self, text, bg_color, fg_color):
        """Update message label"""
        self.message.configure(text=text, bg=bg_color, fg=fg_color)
    
    def stop_attendance(self):
        """Stop attendance and close window"""
        self.update_message("Attendance stopped", "yellow", "black")
        TextToSpeech.speak("Attendance stopped")
        self.window.destroy()

    def _add_button_hover(self, btn, base_bg, darken=False):
        try:
            def on_enter(e):
                btn.configure(bg=self._adjust_color(base_bg, -20 if darken else 20))
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