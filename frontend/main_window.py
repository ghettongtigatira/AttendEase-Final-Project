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
from backend.student_manager import StudentManager
from backend.utils import TextToSpeech
import shutil
from tkinter import messagebox
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, DANGER_BG,
    SUCCESS_BG, INFO_BG, CARD_BG, INPUT_BG, INPUT_FG,
    TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LABEL_FONT, SMALL_FONT,
    WINDOW_SIZE, PADDING, BUTTON_SIZE, APP_BRAND,
    configure_ttk_styles, animate_window_in,
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
        self.all_students_df = None
        self.photo_cache = {}
        self.photo_cache_large = {}
        self.placeholder_photo = None
        self.hover_row = None
        self.setup_ui()
        self.update_time()
    
    def setup_ui(self):
        """Setup main window UI"""
        # Apply ttk styles for a consistent theme
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        # Header bar with subtle gradient and spacious layout
        header = tk.Canvas(self.window, height=86, bg=ACCENT_BG, highlightthickness=0)
        header.pack(fill=X)
        try:
            for i in range(86):
                color = f"#0a1c33"
                header.create_line(0, i, self.window.winfo_screenwidth(), i, fill=color)
        except Exception:
            pass
        header_left = tk.Frame(self.window, bg=ACCENT_BG)
        header_right = tk.Frame(self.window, bg=ACCENT_BG)
        header_left.place(x=PADDING, y=12, height=62)
        header_right.place(relx=1.0, x=-PADDING, y=12, height=62, anchor="ne")

        # Exit button
        exit_btn = tk.Button(
            header_right,
            text="⏻ Exit",
            command=self.window.destroy,
            bd=0,
            font=("Verdana", 12, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=14,
            pady=6,
            cursor="hand2"
        )
        exit_btn.pack(side=RIGHT, padx=(12, 0))
        self._add_button_hover(exit_btn, DANGER_BG, darken=True)

        # Brand text with accent pill
        badge = tk.Label(header_left, text="⚡", bg=PRIMARY_FG, fg=PRIMARY_BG, font=("Verdana", 14, "bold"), padx=10, pady=6)
        badge.pack(side=LEFT, padx=(0, 12))
        title = tk.Label(header_left, text=f"{APP_BRAND}", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT)
        title.pack(side=LEFT)
        subtitle = tk.Label(header_left, text="Smart Face Attendance System", bg=ACCENT_BG, fg="#c2d4ea", font=SUBTITLE_FONT)
        subtitle.pack(side=LEFT, padx=14)
        
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
        btext.pack(padx=PADDING*1.5, pady=(PADDING*1.5, 6))
        bsub = tk.Label(
            banner,
            text="Smart, simple face attendance for your classes",
            bg=CARD_BG,
            fg="#98a8c4",
            font=("Verdana", 11),
        )
        bsub.pack(padx=PADDING*1.5, pady=(0, PADDING*1.5))
        
        # Action area with responsive spacing
        # Actions row as cards
        actions = tk.Frame(self.window, bg=PRIMARY_BG)
        actions.pack(fill=X, padx=PADDING*1.5, pady=(PADDING*2, PADDING*1.25))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)
        actions.grid_columnconfigure(2, weight=1)
        actions.grid_columnconfigure(3, weight=1)

        register_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE, padx=10, pady=10)
        register_card.grid(row=0, column=0, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(register_card, text="👤➕  Register Student", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(12,6))
        register_btn = tk.Button(
            register_card,
            text="➕ Register Student",
            command=self.open_register_window,
            bd=0,
            font=BUTTON_FONT,
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=26, pady=12,
        )
        register_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(register_btn, PRIMARY_FG)

        take_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE, padx=10, pady=10)
        take_card.grid(row=0, column=1, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(take_card, text="📸✔️  Take Attendance", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(12,6))
        take_btn = tk.Button(
            take_card,
            text="📷 Take Attendance",
            command=self.open_attendance_window,
            bd=0,
            font=BUTTON_FONT,
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=24, pady=12,
        )
        take_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(take_btn, PRIMARY_FG)

        view_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE, padx=10, pady=10)
        view_card.grid(row=0, column=2, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(view_card, text="📑  View Attendance", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(12,6))
        view_btn = tk.Button(
            view_card,
            text="📊 View Attendance",
            command=self.open_view_attendance_window,
            bd=0,
            font=BUTTON_FONT,
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=24, pady=12,
        )
        view_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(view_btn, PRIMARY_FG)

        manage_card = tk.Frame(actions, bg=CARD_BG, bd=2, relief=RIDGE, padx=10, pady=10)
        manage_card.grid(row=0, column=3, sticky="nsew", padx=PADDING, pady=PADDING)
        tk.Label(manage_card, text="📚  Manage Subjects", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(pady=(12,6))
        manage_btn = tk.Button(
            manage_card,
            text="🗂️ Manage Subjects",
            command=self.open_manage_subjects_window,
            bd=0,
            font=BUTTON_FONT,
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=24, pady=12,
        )
        manage_btn.pack(padx=PADDING, pady=(0,12))
        self._add_button_hover(manage_btn, PRIMARY_FG)

        # Students list section
        from tkinter import ttk
        list_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        list_frame.pack(fill=BOTH, expand=True, padx=PADDING*1.5, pady=(PADDING, PADDING*2))

        # Section title with divider
        title_frame = tk.Frame(list_frame, bg=PRIMARY_BG)
        title_frame.pack(fill=X, pady=(0, 4))
        tk.Label(title_frame, text="👥  Enrolled Students", bg=PRIMARY_BG, fg=PRIMARY_FG, font=("Verdana", 18, "bold")).pack(side=LEFT, padx=PADDING, pady=(0,8))
        tk.Frame(title_frame, bg="#183251", height=3).pack(side=LEFT, fill=X, expand=True, padx=(14, PADDING), pady=(18,0))

        search_frame = tk.Frame(list_frame, bg=PRIMARY_BG)
        search_frame.pack(fill=X, pady=(0, PADDING))
        tk.Label(search_frame, text="🔍  Search", bg=PRIMARY_BG, fg=ACCENT_FG, font=("Verdana", 11, "bold")).pack(side=LEFT, padx=(PADDING, 8))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=INPUT_BG, fg=INPUT_FG, insertbackground=INPUT_FG, relief=FLAT, font=("Verdana", 11), width=32)
        search_entry.pack(side=LEFT, padx=(0,8), ipady=6)
        search_entry.bind("<KeyRelease>", self.filter_students)
        clear_search = tk.Button(search_frame, text="✖ Clear", command=lambda: self._clear_search(search_entry), bd=0, font=("Verdana", 10, "bold"), bg=CARD_BG, fg=ACCENT_FG, padx=10, pady=6)
        clear_search.pack(side=LEFT)
        self._add_button_hover(clear_search, CARD_BG)
        # Subject filter
        tk.Label(search_frame, text=" |  Filter by Subject", bg=PRIMARY_BG, fg=ACCENT_FG, font=("Verdana", 11, "bold")).pack(side=LEFT, padx=(16, 8))
        self.subject_filter_var = tk.StringVar()
        self.subject_filter_combo = ttk.Combobox(search_frame, textvariable=self.subject_filter_var, state="readonly", width=20, font=("Verdana", 10))
        self.subject_filter_combo.pack(side=LEFT, padx=(0, 10))
        self.subject_filter_combo.bind("<<ComboboxSelected>>", self.filter_students)
        clear_filter = tk.Button(search_frame, text="Clear Filter", command=self._clear_subject_filter, bd=0, font=("Verdana", 10), bg=CARD_BG, fg=ACCENT_FG, padx=10, pady=6)
        clear_filter.pack(side=LEFT, padx=(0, PADDING))
        self._add_button_hover(clear_filter, CARD_BG)

        # Refresh and remove controls above the table for visibility
        refresh_bar = tk.Frame(list_frame, bg=PRIMARY_BG)
        refresh_bar.pack(fill=X, padx=0, pady=(0, PADDING//2))
        btn_row = tk.Frame(refresh_bar, bg=PRIMARY_BG)
        btn_row.pack(side=RIGHT)
        remove_btn = tk.Button(
            btn_row,
            text="🗑️  Remove Selected",
            command=self.remove_selected_student,
            bd=0,
            font=("Verdana", 10, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=10, pady=6,
        )
        remove_btn.pack(side=RIGHT, padx=(8,0))
        self._add_button_hover(remove_btn, DANGER_BG, darken=True)
        refresh_btn = tk.Button(
            btn_row,
            text="🔄  Refresh List",
            command=self.load_students_list,
            bd=0,
            font=("Verdana", 10, "bold"),
            bg=CARD_BG,
            fg=ACCENT_FG,
            padx=12, pady=6,
        )
        refresh_btn.pack(side=RIGHT, padx=8)
        self._add_button_hover(refresh_btn, CARD_BG)

        # Use tree column for photo so images render with show="tree"
        columns = ("Enrollment", "Name", "Subjects")
        self.students_view = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=11)
        self.students_view.heading("#0", text="Photo", anchor="center")
        self.students_view.column("#0", width=80, anchor="center")
        self.students_view.heading("Enrollment", text="ID")
        self.students_view.heading("Name", text="Name")
        self.students_view.heading("Subjects", text="Enrolled Subjects")
        self.students_view.column("Enrollment", width=140, anchor="w")
        self.students_view.column("Name", width=300, anchor="w")
        self.students_view.column("Subjects", width=420, anchor="w")
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
            style.configure("Treeview", rowheight=44, background="#0d1a2e", fieldbackground="#0d1a2e", foreground=PRIMARY_FG, bordercolor=CARD_BG, borderwidth=0)
            style.configure("Treeview.Heading", background="#122844", foreground=PRIMARY_FG, font=("Verdana", 12, "bold"))
            self.students_view.tag_configure("odd", background="#0f213b")
            self.students_view.tag_configure("even", background="#0b1a30")
            self.students_view.tag_configure("hover", background="#16345c")
        except Exception:
            pass
        # Hover highlight for table rows
        self.students_view.bind("<Motion>", self._on_tree_hover)
        self.students_view.bind("<Leave>", self._clear_tree_hover)
        self.students_view.bind("<<TreeviewSelect>>", self._on_student_click)

        # Initial load
        self.load_students_list()

        footer = tk.Frame(self.window, bg=PRIMARY_BG)
        footer.pack(fill=X, padx=PADDING*1.5, pady=(PADDING*1.5, PADDING*2))

        reset_btn = tk.Button(
            footer,
            text="🧹 Reset Student Data",
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
        """Open student registration window"""
        self.window.withdraw()  # Hide main window
        RegisterWindow(self.base_dir, self.haarcascade_path, self.train_path, self.student_details_path, self.model_path, main_window=self)
    
    def open_attendance_window(self):
        """Open take attendance window"""
        self.window.withdraw()  # Hide main window
        AttendanceWindow(
            self.base_dir,
            self.haarcascade_path,
            self.train_path,
            self.student_details_path,
            self.model_path,
            main_window=self
        )
    
    def open_view_attendance_window(self):
        """Open view attendance window"""
        self.window.withdraw()  # Hide main window
        ViewAttendanceWindow(self.base_dir, self.attendance_path, main_window=self)

    def open_manage_subjects_window(self):
        """Open manage subjects window"""
        self.window.withdraw()  # Hide main window
        ManageSubjectsWindow(self.base_dir, self.attendance_path, self.student_details_path, main_window=self)
    
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
            self.photo_cache = {}
            df, msg = self.student_manager.get_all_students()
            self.all_students_df = df
            self._populate_subject_filter(df)
            self._render_students(df)
        except Exception as e:
            print(f"Error loading students list: {e}")

    def _render_students(self, df):
        """Render the treeview rows with optional filtered dataframe"""
        for row in self.students_view.get_children():
            self.students_view.delete(row)
        if df is None or len(df) == 0:
            return
        df = df.reset_index(drop=True)
        for idx, row in df.iterrows():
            tag = "odd" if idx % 2 else "even"
            subjects = row.get("Subjects", "")
            if pd.isna(subjects):
                subjects = ""
            subjects_display = subjects.replace(";", ", ") if subjects else "No subjects"
            enrollment_id = str(row.get("Enrollment", ""))
            photo = self._get_student_photo(enrollment_id)
            self.students_view.insert(
                "",
                "end",
                text="",  # tree column (photo)
                values=(enrollment_id, row.get("Name", ""), subjects_display),
                image=photo,
                tags=(tag,),
            )

    def filter_students(self, event=None):
        """Filter students by search query"""
        if self.all_students_df is None:
            return
        query = (self.search_var.get() or "").strip().lower()
        subject_filter = (self.subject_filter_var.get() or "").strip()
        if not query and not subject_filter:
            self._render_students(self.all_students_df)
            return
        def matcher(row):
            matches_text = (
                query in str(row.get("Enrollment", "")).lower()
                or query in str(row.get("Name", "")).lower()
                or query in str(row.get("Subjects", "")).lower()
            ) if query else True
            if not matches_text:
                return False
            if not subject_filter or subject_filter == "All Subjects":
                return True
            subjects_val = str(row.get("Subjects", "") or "")
            subjects_list = [s.strip().lower() for s in subjects_val.split(";") if s.strip()]
            return subject_filter.lower() in subjects_list
        filtered = self.all_students_df[self.all_students_df.apply(matcher, axis=1)]
        self._render_students(filtered)

    def _clear_search(self, entry):
        self.search_var.set("")
        self.filter_students()
        try:
            entry.focus_set()
        except Exception:
            pass
        # do not reset subject filter here

    def _clear_subject_filter(self):
        """Clear subject filter and re-render"""
        if hasattr(self, "subject_filter_var"):
            self.subject_filter_var.set("")
        self.filter_students()

    def _on_student_click(self, event=None):
        """Show a quick student card popup with details and larger photo"""
        selection = self.students_view.selection()
        if not selection:
            return
        item_id = selection[0]
        values = self.students_view.item(item_id, "values")
        if not values or len(values) < 2:
            return
        enrollment_id = values[0]
        student_name = values[1]
        subjects = values[2] if len(values) > 2 else ""

        # Build popup
        popup = tk.Toplevel(self.window)
        popup.title("Student Info")
        popup.configure(bg=CARD_BG)
        popup.geometry("360x360")
        popup.resizable(False, False)
        popup.transient(self.window)

        # Photo
        photo = self._get_student_photo_with_size(enrollment_id, 120)
        photo_label = tk.Label(popup, image=photo, bg=CARD_BG)
        photo_label.image = photo
        photo_label.pack(pady=(20, 10))

        # Text info
        tk.Label(popup, text=student_name, bg=CARD_BG, fg=PRIMARY_FG, font=("Verdana", 16, "bold")).pack(pady=(0, 6))
        tk.Label(popup, text=f"ID: {enrollment_id}", bg=CARD_BG, fg=ACCENT_FG, font=("Verdana", 11, "bold")).pack()
        tk.Label(popup, text=f"Section: {subjects or 'N/A'}", bg=CARD_BG, fg=ACCENT_FG, font=("Verdana", 11)).pack(pady=(4,0))
        reg_date = self._get_registration_date(enrollment_id)
        tk.Label(popup, text=f"Registered: {reg_date}", bg=CARD_BG, fg="#9fb5d9", font=("Verdana", 10)).pack(pady=(6, 10))

        # Close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy, bd=0, font=("Verdana", 10, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG, padx=14, pady=6, cursor="hand2")
        close_btn.pack(pady=(8, 16))
        self._add_button_hover(close_btn, PRIMARY_FG)

    def _get_student_photo(self, enrollment_id):
        """Return cached thumbnail for a student or placeholder"""
        return self._get_student_photo_with_size(enrollment_id, 36)

    def _get_student_photo_with_size(self, enrollment_id, size):
        """Return cached thumbnail for a student or placeholder at given size"""
        cache = self.photo_cache if size <= 40 else self.photo_cache_large
        key = enrollment_id
        if key in cache:
            return cache[key]
        placeholder = self._create_placeholder_photo(size)
        thumbnail = placeholder
        try:
            student_dir = os.path.join(self.train_path, enrollment_id)
            if os.path.isdir(student_dir):
                images = [f for f in os.listdir(student_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                if images:
                    img_path = os.path.join(student_dir, images[0])
                    img = Image.open(img_path).resize((size, size))
                    thumbnail = ImageTk.PhotoImage(img)
        except Exception:
            pass
        cache[key] = thumbnail
        return thumbnail

    def _create_placeholder_photo(self, size=36):
        """Create or return a soft placeholder avatar"""
        if size <= 40 and self.placeholder_photo:
            return self.placeholder_photo
        img = Image.new("RGB", (size, size), "#12223a")
        photo = ImageTk.PhotoImage(img)
        if size <= 40:
            self.placeholder_photo = photo
        return photo

    def _populate_subject_filter(self, df):
        """Populate subject filter dropdown from dataframe"""
        if df is None or len(df) == 0:
            self.subject_filter_combo["values"] = ["All Subjects"]
            self.subject_filter_var.set("All Subjects")
            return
        subjects = []
        for val in df.get("Subjects", []):
            if pd.isna(val):
                continue
            parts = [s.strip() for s in str(val).split(";") if s.strip()]
            subjects.extend(parts)
        unique_subjects = sorted(set(subjects))
        values = ["All Subjects"] + unique_subjects
        self.subject_filter_combo["values"] = values
        # keep current selection if still valid
        current = self.subject_filter_var.get()
        if current in values:
            self.subject_filter_var.set(current)
        else:
            self.subject_filter_var.set("All Subjects")

    def _get_registration_date(self, enrollment_id):
        """Infer registration date from earliest training image timestamp"""
        try:
            student_dir = os.path.join(self.train_path, enrollment_id)
            if not os.path.isdir(student_dir):
                return "Not available"
            images = [os.path.join(student_dir, f) for f in os.listdir(student_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if not images:
                return "Not available"
            earliest = min(images, key=lambda p: os.path.getmtime(p))
            import datetime
            dt = datetime.datetime.fromtimestamp(os.path.getmtime(earliest))
            return dt.strftime("%b %d, %Y")
        except Exception:
            return "Not available"

    def _on_tree_hover(self, event):
        """Apply hover highlighting to tree rows"""
        row = self.students_view.identify_row(event.y)
        if row == self.hover_row:
            return
        # remove previous hover
        if self.hover_row:
            tags = list(self.students_view.item(self.hover_row, "tags"))
            if "hover" in tags:
                tags.remove("hover")
                self.students_view.item(self.hover_row, tags=tuple(tags))
        # add hover to current row
        if row:
            tags = list(self.students_view.item(row, "tags"))
            if "hover" not in tags:
                tags.append("hover")
            self.students_view.item(row, tags=tuple(tags))
        self.hover_row = row

    def _clear_tree_hover(self, event=None):
        """Clear hover tag when leaving the tree"""
        if self.hover_row:
            tags = list(self.students_view.item(self.hover_row, "tags"))
            if "hover" in tags:
                tags.remove("hover")
                self.students_view.item(self.hover_row, tags=tuple(tags))
        self.hover_row = None

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
                f"⚠️ Remove '{student_name}' ({enrollment_id})?\nThis will also delete their training images.",
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