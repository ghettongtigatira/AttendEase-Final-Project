import tkinter as tk
from tkinter import *
from tkinter import ttk, messagebox
import os
import pandas as pd
from PIL import ImageTk, Image
import shutil
import datetime

from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, DANGER_BG,
    SUCCESS_BG, INFO_BG, CARD_BG, INPUT_BG, INPUT_FG, BORDER_COLOR, HIGHLIGHT,
    TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT, LABEL_FONT, SMALL_FONT,
    PADDING, APP_BRAND, configure_ttk_styles, animate_window_in, show_loading,
)


class ViewStudentsWindow:
    def __init__(self, base_dir, student_details_path, train_path, main_window=None):
        self.base_dir = base_dir
        self.student_details_path = student_details_path
        self.train_path = train_path
        self.main_window = main_window
        
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - Enrolled Students")
        self.window.configure(background=PRIMARY_BG)
        self.window.overrideredirect(True)
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.bind('<Escape>', lambda e: self.go_back())
        
        try:
            animate_window_in(self.window)
        except Exception:
            pass
        
        # Import StudentManager
        from backend.student_manager import StudentManager
        self.student_manager = StudentManager(student_details_path)
        
        self.all_students_df = None
        self.photo_cache = {}
        self.photo_cache_large = {}
        self.placeholder_photo = None
        self.hover_row = None
        
        self.setup_ui()
        self.load_students_list()
    
    def setup_ui(self):
        """Setup the enrolled students window UI"""
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
        tk.Label(header, text="👥  Enrolled Students", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING)
        tk.Label(header, text="│ View and manage students", bg=ACCENT_BG, fg="#8899aa", font=("Segoe UI", 12)).pack(side=LEFT, padx=10)
        
        # Main content
        content = tk.Frame(self.window, bg=PRIMARY_BG)
        content.pack(fill=BOTH, expand=True, padx=PADDING*2, pady=PADDING)
        
        # Search bar
        search_frame = tk.Frame(content, bg=PRIMARY_BG)
        search_frame.pack(fill=X, pady=(0, PADDING))
        
        tk.Label(search_frame, text="🔍", bg=PRIMARY_BG, fg=PRIMARY_FG, font=("Segoe UI", 12)).pack(side=LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=INPUT_BG,
            fg=INPUT_FG,
            insertbackground=PRIMARY_FG,
            relief=FLAT,
            font=("Segoe UI", 11),
            width=30,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_FG
        )
        search_entry.pack(side=LEFT, padx=(0, 10), ipady=8)
        search_entry.bind("<KeyRelease>", self.filter_students)
        
        clear_search = tk.Button(
            search_frame,
            text="✖",
            command=lambda: self._clear_search(search_entry),
            bd=0,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=PRIMARY_FG,
            padx=10,
            pady=6,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        clear_search.pack(side=LEFT, padx=(0, 4))
        self._add_button_hover(clear_search, CARD_BG)
        
        # Subject filter
        tk.Label(search_frame, text="│", bg=PRIMARY_BG, fg=BORDER_COLOR, font=("Segoe UI", 16)).pack(side=LEFT, padx=(16, 16))
        tk.Label(search_frame, text="📁 Filter:", bg=PRIMARY_BG, fg=PRIMARY_FG, font=("Segoe UI", 11, "bold")).pack(side=LEFT, padx=(0, 10))
        
        self.subject_filter_var = tk.StringVar()
        self.subject_filter_combo = ttk.Combobox(
            search_frame,
            textvariable=self.subject_filter_var,
            state="readonly",
            width=20,
            font=("Segoe UI", 11),
            style="Sharp.TCombobox"
        )
        self.subject_filter_combo.pack(side=LEFT, padx=(0, 10), ipady=4)
        self.subject_filter_combo.bind("<<ComboboxSelected>>", self.filter_students)
        
        clear_filter = tk.Button(
            search_frame,
            text="✖ Clear",
            command=self._clear_subject_filter,
            bd=0,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=PRIMARY_FG,
            padx=12,
            pady=6,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        clear_filter.pack(side=LEFT, padx=(0, PADDING))
        self._add_button_hover(clear_filter, CARD_BG)
        
        # Action buttons
        btn_row = tk.Frame(search_frame, bg=PRIMARY_BG)
        btn_row.pack(side=RIGHT)
        
        remove_btn = tk.Button(
            btn_row,
            text="🗑️ REMOVE",
            command=self.remove_selected_student,
            bd=0,
            font=("Segoe UI", 10, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=14,
            pady=6,
            cursor="hand2",
        )
        remove_btn.pack(side=RIGHT, padx=(8, 0))
        self._add_button_hover(remove_btn, DANGER_BG, darken=True)
        
        refresh_btn = tk.Button(
            btn_row,
            text="🔄 REFRESH",
            command=self.load_students_list,
            bd=0,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_BG,
            fg=ACCENT_FG,
            padx=14,
            pady=6,
            cursor="hand2",
        )
        refresh_btn.pack(side=RIGHT, padx=8)
        self._add_button_hover(refresh_btn, CARD_BG)
        
        # Treeview
        tree_container = tk.Frame(content, bg=BORDER_COLOR, highlightthickness=1, highlightbackground=BORDER_COLOR)
        tree_container.pack(fill=BOTH, expand=True, pady=(PADDING, 0))
        
        columns = ("Enrollment", "Name", "Subjects")
        self.students_view = ttk.Treeview(tree_container, columns=columns, show="tree headings", height=15)
        self.students_view.heading("#0", text="Photo", anchor="center")
        self.students_view.column("#0", width=70, anchor="center")
        self.students_view.heading("Enrollment", text="ID")
        self.students_view.heading("Name", text="NAME")
        self.students_view.heading("Subjects", text="ENROLLED SUBJECTS")
        self.students_view.column("Enrollment", width=150, anchor="w")
        self.students_view.column("Name", width=300, anchor="w")
        self.students_view.column("Subjects", width=500, anchor="w")
        
        # Scrollbars
        style = ttk.Style()
        style.configure("Sharp.Vertical.TScrollbar",
            background=CARD_BG,
            troughcolor=PRIMARY_BG,
            bordercolor=BORDER_COLOR,
            arrowcolor=PRIMARY_FG,
            relief="flat",
        )
        style.map("Sharp.Vertical.TScrollbar",
            background=[("active", INPUT_BG), ("pressed", PRIMARY_FG)],
            arrowcolor=[("active", HIGHLIGHT), ("pressed", PRIMARY_BG)],
        )
        style.configure("Sharp.Horizontal.TScrollbar",
            background=CARD_BG,
            troughcolor=PRIMARY_BG,
            bordercolor=BORDER_COLOR,
            arrowcolor=PRIMARY_FG,
            relief="flat",
        )
        style.map("Sharp.Horizontal.TScrollbar",
            background=[("active", INPUT_BG), ("pressed", PRIMARY_FG)],
            arrowcolor=[("active", HIGHLIGHT), ("pressed", PRIMARY_BG)],
        )
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", style="Sharp.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", style="Sharp.Horizontal.TScrollbar")
        self.students_view.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.students_view.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.config(command=self.students_view.yview)
        vsb.pack(side=RIGHT, fill=Y)
        hsb.config(command=self.students_view.xview)
        hsb.pack(side=BOTTOM, fill=X)
        
        # Treeview styling
        style.configure("Treeview", rowheight=40, background=INPUT_BG, fieldbackground=INPUT_BG, foreground=ACCENT_FG, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=ACCENT_BG, foreground=PRIMARY_FG, font=("Segoe UI", 11, "bold"), relief="flat")
        style.map("Treeview.Heading", background=[("active", CARD_BG)])
        self.students_view.tag_configure("odd", background="#0c1825")
        self.students_view.tag_configure("even", background="#101e2f")
        self.students_view.tag_configure("hover", background="#1a3550")
        
        # Bindings
        self.students_view.bind("<Motion>", self._on_tree_hover)
        self.students_view.bind("<Leave>", self._clear_tree_hover)
        self.students_view.bind("<<TreeviewSelect>>", self._on_student_click)
    
    def go_back(self):
        """Return to main window"""
        self.window.destroy()
        if self.main_window:
            self.main_window.window.deiconify()
            self.main_window.window.attributes('-alpha', 1.0)
            self.main_window.load_students_list()
    
    def load_students_list(self):
        """Load all students into the tree view"""
        try:
            self.photo_cache = {}
            self.photo_cache_large = {}
            df, msg = self.student_manager.get_all_students()
            self.all_students_df = df
            self._populate_subject_filter(df)
            self._render_students(df)
        except Exception as e:
            print(f"Error loading students list: {e}")
    
    def _render_students(self, df):
        """Render the treeview rows"""
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
                text="",
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
    
    def _clear_subject_filter(self):
        if hasattr(self, "subject_filter_var"):
            self.subject_filter_var.set("")
        self.filter_students()
    
    def _populate_subject_filter(self, df):
        """Populate subject filter dropdown"""
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
        current = self.subject_filter_var.get()
        if current in values:
            self.subject_filter_var.set(current)
        else:
            self.subject_filter_var.set("All Subjects")
    
    def _get_student_photo(self, enrollment_id):
        return self._get_student_photo_with_size(enrollment_id, 36)
    
    def _get_student_photo_with_size(self, enrollment_id, size):
        cache = self.photo_cache if size <= 40 else self.photo_cache_large
        key = enrollment_id
        if key in cache:
            return cache[key]
        placeholder = self._create_placeholder_photo(size)
        thumbnail = placeholder
        try:
            id_photo_path = os.path.join(self.base_dir, "StudentDetails", "IDPhotos", f"{enrollment_id}.jpg")
            if os.path.exists(id_photo_path):
                img = Image.open(id_photo_path).resize((size, size), Image.Resampling.LANCZOS)
                thumbnail = ImageTk.PhotoImage(img)
            else:
                student_dir = os.path.join(self.train_path, enrollment_id)
                if os.path.isdir(student_dir):
                    images = [f for f in os.listdir(student_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
                    if images:
                        img_path = os.path.join(student_dir, images[0])
                        img = Image.open(img_path).resize((size, size), Image.Resampling.LANCZOS)
                        thumbnail = ImageTk.PhotoImage(img)
        except Exception:
            pass
        cache[key] = thumbnail
        return thumbnail
    
    def _create_placeholder_photo(self, size=36):
        if size <= 40 and self.placeholder_photo:
            return self.placeholder_photo
        img = Image.new("RGB", (size, size), "#12223a")
        photo = ImageTk.PhotoImage(img)
        if size <= 40:
            self.placeholder_photo = photo
        return photo
    
    def _on_student_click(self, event=None):
        """Show student card popup"""
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
        
        popup = tk.Toplevel(self.window)
        popup.title("Student Info")
        popup.configure(bg=CARD_BG)
        popup.geometry("360x360")
        popup.resizable(False, False)
        popup.transient(self.window)
        
        photo = self._get_student_photo_with_size(enrollment_id, 120)
        photo_label = tk.Label(popup, image=photo, bg=CARD_BG)
        photo_label.image = photo
        photo_label.pack(pady=(20, 10))
        
        tk.Label(popup, text=student_name, bg=CARD_BG, fg=PRIMARY_FG, font=("Verdana", 16, "bold")).pack(pady=(0, 6))
        tk.Label(popup, text=f"ID: {enrollment_id}", bg=CARD_BG, fg=ACCENT_FG, font=("Verdana", 11, "bold")).pack()
        tk.Label(popup, text=f"Subjects: {subjects or 'N/A'}", bg=CARD_BG, fg=ACCENT_FG, font=("Verdana", 11)).pack(pady=(4, 0))
        reg_date = self._get_registration_date(enrollment_id)
        tk.Label(popup, text=f"Registered: {reg_date}", bg=CARD_BG, fg="#9fb5d9", font=("Verdana", 10)).pack(pady=(6, 10))
        
        close_btn = tk.Button(popup, text="Close", command=popup.destroy, bd=0, font=("Verdana", 10, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG, padx=14, pady=6, cursor="hand2")
        close_btn.pack(pady=(8, 16))
        self._add_button_hover(close_btn, PRIMARY_FG)
    
    def _get_registration_date(self, enrollment_id):
        try:
            student_dir = os.path.join(self.train_path, enrollment_id)
            if not os.path.isdir(student_dir):
                return "Not available"
            images = [os.path.join(student_dir, f) for f in os.listdir(student_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            if not images:
                return "Not available"
            earliest = min(images, key=lambda p: os.path.getmtime(p))
            dt = datetime.datetime.fromtimestamp(os.path.getmtime(earliest))
            return dt.strftime("%b %d, %Y")
        except Exception:
            return "Not available"
    
    def _on_tree_hover(self, event):
        row = self.students_view.identify_row(event.y)
        if row == self.hover_row:
            return
        if self.hover_row:
            tags = list(self.students_view.item(self.hover_row, "tags"))
            if "hover" in tags:
                tags.remove("hover")
                self.students_view.item(self.hover_row, tags=tuple(tags))
        if row:
            tags = list(self.students_view.item(row, "tags"))
            if "hover" not in tags:
                tags.append("hover")
            self.students_view.item(row, tags=tuple(tags))
        self.hover_row = row
    
    def _clear_tree_hover(self, event=None):
        if self.hover_row:
            tags = list(self.students_view.item(self.hover_row, "tags"))
            if "hover" in tags:
                tags.remove("hover")
                self.students_view.item(self.hover_row, tags=tuple(tags))
        self.hover_row = None
    
    def remove_selected_student(self):
        """Remove the selected student"""
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
            
            ok, msg = self.student_manager.remove_student(enrollment_id)
            if not ok:
                messagebox.showerror("Remove Failed", msg or "Unable to remove student.")
                return
            
            student_train_dir = os.path.join(self.train_path, enrollment_id)
            if os.path.isdir(student_train_dir):
                try:
                    shutil.rmtree(student_train_dir)
                except Exception as e:
                    messagebox.showwarning("Images Not Fully Removed", f"Removed record but failed to delete images: {e}")
            
            self.load_students_list()
            messagebox.showinfo("Removed", f"Student {enrollment_id} removed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {e}")
    
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
            hc = hex_color[1:] if hex_color.startswith("#") else hex_color
            r = max(0, min(255, int(hc[0:2], 16) + delta))
            g = max(0, min(255, int(hc[2:4], 16) + delta))
            b = max(0, min(255, int(hc[4:6], 16) + delta))
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color
