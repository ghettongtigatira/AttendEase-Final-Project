import tkinter as tk
from tkinter import *
import os
import datetime
from PIL import ImageTk, Image
from frontend.register_window import RegisterWindow
from frontend.attendance_window import AttendanceWindow
from frontend.view_attendance_window import ViewAttendanceWindow
from frontend.manage_subjects_window import ManageSubjectsWindow
from backend.student_manager import StudentManager
from backend.utils import TextToSpeech
import shutil
from tkinter import messagebox
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, DANGER_BG,
    SUCCESS_BG, INFO_BG, CARD_BG, INPUT_BG, INPUT_FG,
    TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LABEL_FONT, SMALL_FONT,
    WINDOW_SIZE, PADDING, BUTTON_SIZE, APP_BRAND,
    configure_ttk_styles,
)

class MainWindow:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.window = Tk()
        self.window.title(f"{APP_BRAND} - Face Attendance")
        self.window.geometry(WINDOW_SIZE)
        self.window.configure(background=PRIMARY_BG)
        
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
        """Setup main window UI"""
        # Apply ttk styles for a consistent theme
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        # Header bar with subtle gradient and tighter layout
        header = tk.Canvas(self.window, height=72, bg=ACCENT_BG, highlightthickness=0)
        header.pack(fill=X)
        # Draw a simple vertical gradient by lines (subtle depth)
        try:
            for i in range(72):
                shade = 0x0E + int(i * 0.003)  # subtle change
                color = f"#0E1A2B"
                header.create_line(0, i, self.window.winfo_screenwidth(), i, fill=color)
        except Exception:
            pass
        # Header content containers
        header_left = tk.Frame(self.window, bg=ACCENT_BG)
        header_right = tk.Frame(self.window, bg=ACCENT_BG)
        header_left.place(x=PADDING, y=8, height=56)
        header_right.place(relx=1.0, x=-PADDING, y=8, height=56, anchor="ne")

        # Brand text (icon later)
        title = tk.Label(header_left, text=APP_BRAND, bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT)
        title.pack(side=LEFT)
        subtitle = tk.Label(header_left, text="Smart Face Attendance System", bg=ACCENT_BG, fg="#9fb5d9", font=SUBTITLE_FONT)
        subtitle.pack(side=LEFT, padx=12)
        
        # Time and date display
        self.time_date_label = tk.Label(
            header_right,
            text="",
            bg=ACCENT_BG,
            fg="#c9d7ef",
            font=("Verdana", 10),
            justify=RIGHT
        )
        self.time_date_label.pack()
        
        # Welcome message
        # Hero banner
        banner = tk.Frame(self.window, bg=CARD_BG)
        banner.pack(fill=X, padx=PADDING, pady=(PADDING, 0))
        btext = tk.Label(
            banner,
            text=f"Welcome to {APP_BRAND}",
            bg=CARD_BG,
            fg=PRIMARY_FG,
            font=("Verdana", 26, "bold"),
        )
        btext.pack(padx=PADDING, pady=(PADDING, 4))
        bsub = tk.Label(
            banner,
            text="Smart, simple face attendance for your classes",
            bg=CARD_BG,
            fg="#98a8c4",
            font=("Verdana", 11),
        )
        bsub.pack(padx=PADDING, pady=(0, PADDING))
        
        # Action area with responsive spacing
        # Actions row as cards
        actions = tk.Frame(self.window, bg=PRIMARY_BG)
        actions.pack(fill=X, padx=PADDING, pady=(PADDING*2, PADDING))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)
        actions.grid_columnconfigure(3, weight=1)

        register_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE)
        register_card.grid(row=0, column=0, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(register_card, text="👤➕  Register Student", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(10,4))
        register_btn = tk.Button(
            register_card,
            text="Register Student",
            command=self.open_register_window,
            bd=0,
            font=BUTTON_FONT,
            bg=INFO_BG,
            fg=ACCENT_FG,
            padx=24, pady=12,
        )
        register_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(register_btn, INFO_BG)

        take_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE)
        take_card.grid(row=0, column=1, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(take_card, text="📸✔️  Take Attendance", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(10,4))
        take_btn = tk.Button(
            take_card,
            text="Take Attendance",
            command=self.open_attendance_window,
            bd=0,
            font=BUTTON_FONT,
            bg=SUCCESS_BG,
            fg=ACCENT_FG,
            padx=24, pady=12,
        )
        take_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(take_btn, SUCCESS_BG)

        view_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE)
        view_card.grid(row=0, column=2, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(view_card, text="📑  View Attendance", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(10,4))
        view_btn = tk.Button(
            view_card,
            text="View Attendance",
            command=self.open_view_attendance_window,
            bd=0,
            font=BUTTON_FONT,
            bg=SUCCESS_BG,
            fg=ACCENT_FG,
            padx=24, pady=12,
        )
        view_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(view_btn, SUCCESS_BG)

        manage_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE)
        manage_card.grid(row=0, column=3, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(manage_card, text="📚  Manage Subjects", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(10,4))
        manage_btn = tk.Button(
            manage_card,
            text="Manage Subjects",
            command=self.open_manage_subjects_window,
            bd=0,
            font=BUTTON_FONT,
            bg="#6C5CE7",  # purple for subject management
            fg=ACCENT_FG,
            padx=24, pady=12,
        )
        manage_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(manage_btn, "#6C5CE7")

        # Students list section
        from tkinter import ttk
        list_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        list_frame.pack(fill=BOTH, expand=True, padx=PADDING, pady=(PADDING, PADDING*2))

        # Section title with divider
        title_frame = tk.Frame(list_frame, bg=PRIMARY_BG)
        title_frame.pack(fill=X)
        tk.Label(title_frame, text="👥  Enrolled Students", bg=PRIMARY_BG, fg=PRIMARY_FG, font=("Verdana", 16, "bold")).pack(side=LEFT, padx=PADDING, pady=(0,6))
        tk.Frame(title_frame, bg="#10233E", height=2).pack(side=LEFT, fill=X, expand=True, padx=(12, PADDING), pady=(14,0))

        columns = ("Enrollment", "Name")
        self.students_view = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.students_view.heading("Enrollment", text="ID")
        self.students_view.heading("Name", text="Name")
        self.students_view.column("Enrollment", width=200, anchor="w")
        self.students_view.column("Name", width=540, anchor="w")
        # Add scrollbars (use pack consistently to avoid mix with grid)
        sv_container = tk.Frame(list_frame, bg=PRIMARY_BG)
        sv_container.pack(fill=BOTH, expand=True)
        vsb = tk.Scrollbar(sv_container, orient="vertical")
        hsb = tk.Scrollbar(sv_container, orient="horizontal")
        self.students_view.configure(yscroll=vsb.set, xscroll=hsb.set)
        # Layout using pack
        self.students_view.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.config(command=self.students_view.yview)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.config(command=self.students_view.xview)
        hsb.pack(side=BOTTOM, fill=X)

        # Style header and rows: striped, larger row height
        try:
            style = ttk.Style()
            style.configure("Treeview", rowheight=28, background="#0A1220", fieldbackground="#0A1220", foreground=PRIMARY_FG)
            style.configure("Treeview.Heading", background="#10233E", foreground=PRIMARY_FG, font=("Verdana", 11, "bold"))
            # Tag alternating rows
            self.students_view.tag_configure("odd", background="#0C1730")
            self.students_view.tag_configure("even", background="#0A1220")
        except Exception:
            pass

        # Add a refresh button
        refresh_bar = tk.Frame(self.window, bg=PRIMARY_BG)
        refresh_bar.pack(fill=X, padx=PADDING, pady=(0, PADDING))
        # Right-aligned compact rounded-like buttons with emoji icons
        btn_row = tk.Frame(refresh_bar, bg=PRIMARY_BG)
        btn_row.pack(side=RIGHT)
        remove_btn = tk.Button(
            btn_row,
            text="🗑️  Remove Selected",
            command=self.remove_selected_student,
            bd=0,
            font=("Verdana", 11, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=16, pady=8,
        )
        remove_btn.pack(side=RIGHT, padx=(8,0))
        self._add_button_hover(remove_btn, DANGER_BG, darken=True)
        refresh_btn = tk.Button(
            btn_row,
            text="🔄  Refresh List",
            command=self.load_students_list,
            bd=0,
            font=("Verdana", 11, "bold"),
            bg=CARD_BG,
            fg=ACCENT_FG,
            padx=16, pady=8,
        )
        refresh_btn.pack(side=RIGHT, padx=8)
        self._add_button_hover(refresh_btn, CARD_BG)

        # Initial load
        self.load_students_list()

        footer = tk.Frame(self.window, bg=PRIMARY_BG)
        footer.pack(fill=X, padx=PADDING, pady=(PADDING, PADDING*2))

        reset_btn = tk.Button(
            footer,
            text="Reset Student Data",
            command=self.reset_student_data,
            bd=0,
            font=BUTTON_FONT,
            bg=DANGER_BG,
            fg="white",
            padx=20, pady=10,
        )
        reset_btn.pack(side=LEFT, padx=PADDING)

        exit_btn = tk.Button(
            footer,
            text="EXIT",
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
        """Open student registration window"""
        RegisterWindow(self.base_dir, self.haarcascade_path, self.train_path, self.student_details_path, self.model_path)
    
    def open_attendance_window(self):
        """Open take attendance window"""
        # Fix argument order: (base_dir, haarcascade_path, train_path, student_details_path, model_path)
        AttendanceWindow(
            self.base_dir,
            self.haarcascade_path,
            self.train_path,
            self.student_details_path,
            self.model_path,
        )
    
    def open_view_attendance_window(self):
        """Open view attendance window"""
        ViewAttendanceWindow(self.base_dir, self.attendance_path)

    def open_manage_subjects_window(self):
        """Open manage subjects window"""
        ManageSubjectsWindow(self.base_dir, self.attendance_path, self.student_details_path)
    
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
        """Load all students into the tree view"""
        try:
            # Clear existing rows
            for row in self.students_view.get_children():
                self.students_view.delete(row)
            # Load from CSV via StudentManager
            df, msg = self.student_manager.get_all_students()
            if df is None or len(df) == 0:
                return
            for idx, row in df.iterrows():
                tag = "odd" if idx % 2 else "even"
                self.students_view.insert("", "end", values=(row.get("Enrollment", ""), row.get("Name", "")), tags=(tag,))
        except Exception as e:
            print(f"Error loading students list: {e}")

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

    def remove_selected_student(self):
        """Remove the selected student from CSV and training images"""
        try:
            selection = self.students_view.selection()
            if not selection:
                messagebox.showinfo("No Selection", "Please select a student to remove.")
                return
            item_id = selection[0]
            values = self.students_view.item(item_id, "values")
            if not values or len(values) < 1:
                messagebox.showinfo("No Selection", "Please select a valid student entry.")
                return
            enrollment_id = values[0]
            student_name = values[1] if len(values) > 1 else ""

            confirm = messagebox.askyesno(
                "Remove Student",
                f"This will remove student '{student_name}' with ID {enrollment_id} and delete their training images.\n\nProceed?"
            )
            if not confirm:
                return

            # Remove from CSV via StudentManager
            ok, msg = self.student_manager.remove_student(enrollment_id)
            if not ok:
                messagebox.showerror("Remove Failed", msg or "Unable to remove student.")
                return

            # Delete training images folder for this student if exists
            student_train_dir = os.path.join(self.train_path, enrollment_id)
            if os.path.isdir(student_train_dir):
                try:
                    shutil.rmtree(student_train_dir)
                except Exception as e:
                    messagebox.showwarning("Images Not Fully Removed", f"Removed record but failed to delete images: {e}")

            # Optionally remove model; keeping it, as retraining will refresh
            # Refresh list
            self.load_students_list()
            messagebox.showinfo("Removed", f"Student {enrollment_id} removed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")