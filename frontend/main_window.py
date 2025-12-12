import tkinter as tk
from tkinter import *
import os
import datetime
import pandas as pd
from PIL import ImageTk, Image
from frontend.register_window import RegisterWindow
from frontend.attendance_window import AttendanceWindow
from frontend.view_attendance_window import ViewAttendanceWindow
from frontend.manage_subjects_window import ManageSubjectsWindow
from frontend.view_students_window import ViewStudentsWindow
from backend.student_manager import StudentManager
from backend.utils import TextToSpeech
import shutil
from tkinter import messagebox
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, DANGER_BG,
    SUCCESS_BG, INFO_BG, CARD_BG, INPUT_BG, INPUT_FG, BORDER_COLOR, HIGHLIGHT,
    TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LABEL_FONT, SMALL_FONT,
    WINDOW_SIZE, PADDING, BUTTON_SIZE, APP_BRAND,
    configure_ttk_styles, animate_window_in, show_loading,
)

class MainWindow:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.window = Tk()
        self.window.title(f"{APP_BRAND} - Face Attendance")
        self.window.configure(background=PRIMARY_BG)
        self.window.overrideredirect(True)  # Borderless
        # Set fullscreen manually (get screen dimensions)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.bind('<Escape>', lambda e: self.window.destroy())  # Exit on Escape
        try:
            animate_window_in(self.window)
        except Exception:
            pass
        
        # Initialize paths
        self.student_details_path = os.path.join(base_dir, "StudentDetails", "studentdetails.csv")
        self.train_path = os.path.join(base_dir, "TrainingImage")
        self.model_path = os.path.join(base_dir, "TrainingImageLabel", "Trainner.yml")
        self.attendance_path = os.path.join(base_dir, "Attendance")
        self.haarcascade_path = os.path.join(base_dir, "haarcascade_frontalface_default.xml")
        
        self.student_manager = StudentManager(self.student_details_path)
        self.setup_ui()
        self.update_time()
    
    def setup_ui(self):
        """Setup main window UI - Sharp Modern Design"""
        # Apply ttk styles for a consistent theme
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        # Sharp header bar with clean line
        header = tk.Frame(self.window, bg=ACCENT_BG, height=80)
        header.pack(fill=X)
        header.pack_propagate(False)
        
        # Bottom border line for header
        header_line = tk.Frame(self.window, bg=PRIMARY_FG, height=2)
        header_line.pack(fill=X)
        
        # Main content container - centered vertically
        content_container = tk.Frame(self.window, bg=PRIMARY_BG)
        content_container.pack(fill=BOTH, expand=True)
        
        # Inner content frame for vertical centering
        content_inner = tk.Frame(content_container, bg=PRIMARY_BG)
        content_inner.place(relx=0.5, rely=0.5, anchor="center")
        
        header_left = tk.Frame(header, bg=ACCENT_BG)
        header_right = tk.Frame(header, bg=ACCENT_BG)
        header_left.pack(side=LEFT, padx=PADDING*2, pady=15)
        header_right.pack(side=RIGHT, padx=PADDING*2, pady=15)

        # Brand text only (no logo in header)
        title = tk.Label(header_left, text=f"{APP_BRAND}", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT)
        title.pack(side=LEFT)
        subtitle = tk.Label(header_left, text="│ Smart Face Attendance", bg=ACCENT_BG, fg="#8899aa", font=("Segoe UI", 12))
        subtitle.pack(side=LEFT, padx=14)
        
        # Time and date display - sharper
        self.time_date_label = tk.Label(
            header_right,
            text="",
            bg=ACCENT_BG,
            fg=PRIMARY_FG,
            font=("Segoe UI", 10, "bold"),
            justify=RIGHT
        )
        self.time_date_label.pack(side=RIGHT)
        
        # Hero banner with logo
        banner = tk.Frame(content_inner, bg=CARD_BG, highlightthickness=1, highlightbackground=BORDER_COLOR)
        banner.pack(fill=X, padx=PADDING*2, pady=(0, 0))
        
        # Logo in banner - centered and larger
        try:
            logo_path = os.path.join(self.base_dir, "UI_Image", "AttendEase-removebg-preview.png")
            logo_img = Image.open(logo_path)
            # Big logo for banner - height 100
            aspect_ratio = logo_img.width / logo_img.height
            new_height = 100
            new_width = int(new_height * aspect_ratio)
            logo_img = logo_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(banner, image=self.logo_photo, bg=CARD_BG)
            logo_label.pack(pady=(PADDING, 0))
        except Exception:
            pass
        
        btext = tk.Label(
            banner,
            text=f"Welcome to {APP_BRAND}",
            bg=CARD_BG,
            fg=PRIMARY_FG,
            font=("Segoe UI", 24, "bold"),
        )
        btext.pack(padx=PADDING*2, pady=(8, 4))
        bsub = tk.Label(
            banner,
            text="Smart, simple face attendance for your classes",
            bg=CARD_BG,
            fg="#7788aa",
            font=("Segoe UI", 11),
        )
        bsub.pack(padx=PADDING*2, pady=(0, PADDING))
        
        # Actions row - sharp cards
        actions = tk.Frame(content_inner, bg=PRIMARY_BG)
        actions.pack(fill=X, padx=PADDING*2, pady=(PADDING, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)
        actions.grid_columnconfigure(3, weight=1)
        actions.grid_columnconfigure(4, weight=1)

        # Sharp card style
        card_style = {"bg": CARD_BG, "highlightthickness": 1, "highlightbackground": BORDER_COLOR, "padx": 15, "pady": 15}

        register_card = tk.Frame(actions, **card_style)
        register_card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tk.Label(register_card, text="👤  REGISTER", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 13, "bold")).pack(pady=(8,8))
        register_btn = tk.Button(
            register_card,
            text="➕ Register Student",
            command=self.open_register_window,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=20, pady=10,
            cursor="hand2",
            activebackground=HIGHLIGHT,
        )
        register_btn.pack(padx=PADDING, pady=(0,8))
        self._add_button_hover(register_btn, PRIMARY_FG)

        take_card = tk.Frame(actions, **card_style)
        take_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        tk.Label(take_card, text="📸  ATTENDANCE", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 13, "bold")).pack(pady=(8,8))
        take_btn = tk.Button(
            take_card,
            text="📷 Take Attendance",
            command=self.open_attendance_window,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=20, pady=10,
            cursor="hand2",
            activebackground=HIGHLIGHT,
        )
        take_btn.pack(padx=PADDING, pady=(0,8))
        self._add_button_hover(take_btn, PRIMARY_FG)

        view_card = tk.Frame(actions, **card_style)
        view_card.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        tk.Label(view_card, text="📊  VIEW", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 13, "bold")).pack(pady=(8,8))
        view_btn = tk.Button(
            view_card,
            text="📊 View Attendance",
            command=self.open_view_attendance_window,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=20, pady=10,
            cursor="hand2",
            activebackground=HIGHLIGHT,
        )
        view_btn.pack(padx=PADDING, pady=(0,8))
        self._add_button_hover(view_btn, PRIMARY_FG)

        manage_card = tk.Frame(actions, **card_style)
        manage_card.grid(row=0, column=3, sticky="nsew", padx=10, pady=10)
        tk.Label(manage_card, text="📚  SUBJECTS", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 13, "bold")).pack(pady=(8,8))
        manage_btn = tk.Button(
            manage_card,
            text="🗂️ Manage Subjects",
            command=self.open_manage_subjects_window,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=20, pady=10,
            cursor="hand2",
            activebackground=HIGHLIGHT,
        )
        manage_btn.pack(padx=PADDING, pady=(0,8))
        self._add_button_hover(manage_btn, PRIMARY_FG)

        # View Students card
        students_card = tk.Frame(actions, **card_style)
        students_card.grid(row=0, column=4, sticky="nsew", padx=10, pady=10)
        tk.Label(students_card, text="👥  STUDENTS", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 13, "bold")).pack(pady=(8,8))
        students_btn = tk.Button(
            students_card,
            text="📋 View Students",
            command=self.open_view_students_window,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=20, pady=10,
            cursor="hand2",
            activebackground=HIGHLIGHT,
        )
        students_btn.pack(padx=PADDING, pady=(0,8))
        self._add_button_hover(students_btn, PRIMARY_FG)

        # Footer
        footer = tk.Frame(content_inner, bg=PRIMARY_BG)
        footer.pack(fill=X, padx=PADDING*2, pady=(PADDING, 0))

        reset_btn = tk.Button(
            footer,
            text="🧹 RESET DATA",
            command=self.reset_student_data,
            bd=0,
            font=("Segoe UI", 12, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=20, pady=10,
            cursor="hand2",
        )
        reset_btn.pack(side=LEFT, padx=0)

        exit_btn = tk.Button(
            footer,
            text="⏻ Exit App",
            bd=0,
            command=self.window.quit,
            font=BUTTON_FONT,
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            activebackground=ACCENT_BG,
            activeforeground=ACCENT_FG,
            padx=20, pady=10,
        )
        exit_btn.pack(side=LEFT, padx=PADDING)
    
    def update_time(self):
        """Update time and date every second"""
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%A, %B %d, %Y")
        
        self.time_date_label.config(text=f"{current_date}\n{current_time}")
        self.window.after(1000, self.update_time)
    
    def open_register_window(self):
        """Open student registration window with loading screen"""
        self.window.withdraw()
        
        def open_window():
            RegisterWindow(self.base_dir, self.haarcascade_path, self.train_path, self.student_details_path, self.model_path, main_window=self)
        
        show_loading(duration_ms=500, callback=open_window)
    
    def open_attendance_window(self):
        """Open take attendance window with loading screen"""
        self.window.withdraw()
        
        def open_window():
            AttendanceWindow(
                self.base_dir,
                self.haarcascade_path,
                self.train_path,
                self.student_details_path,
                self.model_path,
                main_window=self
            )
        
        show_loading(duration_ms=500, callback=open_window)
    
    def open_view_attendance_window(self):
        """Open view attendance window with loading screen"""
        self.window.withdraw()
        
        def open_window():
            ViewAttendanceWindow(self.base_dir, self.attendance_path, main_window=self)
        
        show_loading(duration_ms=500, callback=open_window)

    def open_manage_subjects_window(self):
        """Open manage subjects window with loading screen"""
        self.window.withdraw()
        
        def open_window():
            ManageSubjectsWindow(self.base_dir, self.attendance_path, self.student_details_path, main_window=self)
        
        show_loading(duration_ms=500, callback=open_window)

    def open_view_students_window(self):
        """Open view enrolled students window with loading screen"""
        self.window.withdraw()
        
        def open_window():
            ViewStudentsWindow(self.base_dir, self.student_details_path, self.train_path, main_window=self)
        
        show_loading(duration_ms=500, callback=open_window)
    
    def reset_student_data(self):
        """Reset all student data"""
        confirm = messagebox.askyesno(
            "Reset Confirmation",
            "⚠️ This will DELETE all registered student faces and training model!\n\nAre you sure?"
        )
        
        if not confirm:
            return
        
        try:
            # Delete training images
            if os.path.exists(self.train_path):
                shutil.rmtree(self.train_path)
                os.makedirs(self.train_path, exist_ok=True)
            
            # Delete training model
            if os.path.exists(self.model_path):
                os.remove(self.model_path)
            
            # Reset student details
            self.student_manager.reset_all_students()
            
            messagebox.showinfo("Reset Successful", "✅ All student data has been reset!")
            TextToSpeech.speak("All student data has been reset successfully")
        
        except Exception as e:
            messagebox.showerror("Reset Error", f"Error: {str(e)}")
            TextToSpeech.speak(f"Error resetting data: {str(e)}")
    
    def run(self):
        """Run the main window"""
        self.window.mainloop()

    def load_students_list(self):
        """Placeholder for compatibility - actual list is in ViewStudentsWindow"""
        pass

    def _add_button_hover(self, btn, base_bg, darken=False):
        """Add simple hover effect: brighten or darken color and slight padding change"""
        try:
            def on_enter(e):
                btn.configure(bg=self._adjust_color(base_bg, -20 if darken else 20))
                btn.configure(padx=btn.cget("padx")+1, pady=btn.cget("pady")+1)
            def on_leave(e):
                btn.configure(bg=base_bg)
                btn.configure(padx=btn.cget("padx")-1, pady=btn.cget("pady")-1)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        except Exception:
            pass

    def _adjust_color(self, hex_color, delta):
        """Adjust brightness of a hex color (#RRGGBB) by delta (-255..255)"""
        try:
            original = hex_color
            hc = hex_color[1:] if hex_color.startswith("#") else hex_color
            r = max(0, min(255, int(hc[0:2], 16) + delta))
            g = max(0, min(255, int(hc[2:4], 16) + delta))
            b = max(0, min(255, int(hc[4:6], 16) + delta))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return original