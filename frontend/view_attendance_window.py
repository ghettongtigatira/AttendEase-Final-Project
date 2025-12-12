import tkinter as tk
from tkinter import *
from tkinter import messagebox
import csv
import os  # FIXED: Add missing import
import pandas as pd  # FIXED: Add for DataFrame operations
from backend.attendance_handler import AttendanceHandler
from backend.utils import TextToSpeech
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, CARD_BG,
    INPUT_BG, INPUT_FG, TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT,
    LABEL_FONT, WINDOW_SIZE, PADDING, APP_BRAND, SUCCESS_BG, DANGER_BG,
    BORDER_COLOR, HIGHLIGHT, configure_ttk_styles, animate_window_in
)

class ViewAttendanceWindow:
    def __init__(self, base_dir, attendance_path, main_window=None):
        self.base_dir = base_dir
        self.attendance_path = attendance_path
        self.attendance_handler = AttendanceHandler(attendance_path, "")
        self.main_window = main_window
        
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - View Attendance")
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
        """Setup view attendance UI"""
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
        tk.Label(header, text="📊  View Attendance", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING)
        tk.Label(header, text="│ View and manage records", bg=ACCENT_BG, fg="#8899aa", font=("Segoe UI", 12)).pack(side=LEFT, padx=10)
        
        # Main content area
        content = tk.Frame(self.window, bg=PRIMARY_BG)
        content.pack(fill=BOTH, expand=True, padx=PADDING*2, pady=PADDING)
        
        # Top control bar in a card
        control_card = tk.Frame(content, bg=CARD_BG, padx=20, pady=15, highlightthickness=1, highlightbackground=BORDER_COLOR)
        control_card.pack(fill=X, pady=(0, PADDING))
        
        # Subject selection row
        tk.Label(control_card, text="Subject:", bg=CARD_BG, fg=ACCENT_FG, font=("Segoe UI", 11, "bold")).pack(side=LEFT, padx=(0, 10))
        from tkinter import ttk
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(control_card, textvariable=self.subject_var, state="readonly", width=28, font=("Segoe UI", 11))
        self.subject_combo.pack(side=LEFT, padx=(0, 20))
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_subject_select)
        
        # Action buttons in control bar
        view_btn = tk.Button(
            control_card,
            text="📊 View Report",
            command=self.view_attendance,
            bd=0,
            font=("Segoe UI", 11, "bold"),
            bg=PRIMARY_FG,
            fg=PRIMARY_BG,
            padx=16,
            pady=8,
            cursor="hand2"
        )
        view_btn.pack(side=LEFT, padx=(0, 10))
        self._add_button_hover(view_btn, PRIMARY_FG)
        
        sheets_btn = tk.Button(
            control_card,
            text="📁 Open Folder",
            command=self.check_sheets,
            bd=0,
            font=("Segoe UI", 11, "bold"),
            bg=CARD_BG,
            fg=PRIMARY_FG,
            padx=16,
            pady=8,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR
        )
        sheets_btn.pack(side=LEFT, padx=(0, 10))
        self._add_button_hover(sheets_btn, CARD_BG)
        
        reset_btn = tk.Button(
            control_card,
            text="🗑️ Reset",
            command=self.reset_attendance,
            bd=0,
            font=("Segoe UI", 11, "bold"),
            bg=DANGER_BG,
            fg="white",
            padx=16,
            pady=8,
            cursor="hand2"
        )
        reset_btn.pack(side=LEFT)
        self._add_button_hover(reset_btn, DANGER_BG, darken=True)
        
        # Records section with header
        records_header = tk.Frame(content, bg=PRIMARY_BG)
        records_header.pack(fill=X, pady=(PADDING, 8))
        
        tk.Label(
            records_header,
            text="📋 Attendance Records",
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            font=("Segoe UI", 14, "bold"),
        ).pack(side=LEFT)
        
        # Subject info label
        self.subject_info_label = tk.Label(
            records_header,
            text="",
            bg=PRIMARY_BG,
            fg=ACCENT_FG,
            font=("Segoe UI", 11),
        )
        self.subject_info_label.pack(side=LEFT, padx=(20, 0))
        
        # Total count label
        self.total_label = tk.Label(
            records_header,
            text="",
            bg=PRIMARY_BG,
            fg=SUCCESS_BG,
            font=("Segoe UI", 11, "bold"),
        )
        self.total_label.pack(side=RIGHT)
        
        # Create Treeview for attendance records
        tree_container = tk.Frame(content, bg=BORDER_COLOR, highlightthickness=1, highlightbackground=BORDER_COLOR)
        tree_container.pack(fill=BOTH, expand=True)
        
        from tkinter import ttk
        
        # Style the Treeview
        style = ttk.Style()
        style.configure("Attendance.Treeview", 
            rowheight=40, 
            background=INPUT_BG, 
            fieldbackground=INPUT_BG, 
            foreground=ACCENT_FG, 
            borderwidth=0, 
            font=("Segoe UI", 11)
        )
        style.configure("Attendance.Treeview.Heading", 
            background=ACCENT_BG, 
            foreground=PRIMARY_FG, 
            font=("Segoe UI", 11, "bold"), 
            relief="flat"
        )
        style.map("Attendance.Treeview.Heading", background=[("active", CARD_BG)])
        
        # Scrollbars
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
        
        columns = ("enrollment", "name", "date", "time")
        self.attendance_tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show="headings", 
            style="Attendance.Treeview"
        )
        
        # Configure columns
        self.attendance_tree.heading("enrollment", text="📋 ENROLLMENT ID")
        self.attendance_tree.heading("name", text="👤 NAME")
        self.attendance_tree.heading("date", text="📅 DATE")
        self.attendance_tree.heading("time", text="⏰ TIME")
        
        self.attendance_tree.column("enrollment", width=180, anchor="center")
        self.attendance_tree.column("name", width=300, anchor="w")
        self.attendance_tree.column("date", width=150, anchor="center")
        self.attendance_tree.column("time", width=150, anchor="center")
        
        # Add scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.attendance_tree.yview, style="Sharp.Vertical.TScrollbar")
        self.attendance_tree.configure(yscrollcommand=vsb.set)
        
        self.attendance_tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        
        # Alternating row colors
        self.attendance_tree.tag_configure("odd", background="#0c1825")
        self.attendance_tree.tag_configure("even", background="#101e2f")
        
        # Populate subjects and load initial attendance data
        self.seed_and_load_subjects()
        self.load_attendance_list()

    def load_subjects(self):
        """Load subjects from AttendanceHandler and populate dropdown"""
        subjects, msg = self.attendance_handler.list_subjects()
        # Prefer showing known defaults in front if present
        defaults = [
            "CSST 102","CMSC 310","CSST 101","CMSC 307",
            "CMSC 3O9","CMSC 306","CMSC 305","CMSC 308",
        ]
        ordered = [s for s in defaults if s in subjects] + [s for s in subjects if s not in defaults]
        self.subject_combo["values"] = ordered
        # Select first subject if available
        if ordered:
            self.subject_combo.current(0)
            self.subject_var.set(ordered[0])

    def seed_and_load_subjects(self):
        """Seed default subjects if missing and then load dropdown"""
        defaults = [
            "CSST 102","CMSC 310","CSST 101","CMSC 307",
            "CMSC 3O9","CMSC 306","CMSC 305","CMSC 308",
        ]
        for s in defaults:
            try:
                self.attendance_handler.add_subject(s)
            except Exception:
                pass
        self.load_subjects()
    
    def load_attendance_list(self):
        """Load and display attendance records in Treeview"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # Reset labels
        self.subject_info_label.config(text="")
        self.total_label.config(text="")
        
        # Use combobox text to ensure selected subject is captured
        subject = (self.subject_combo.get() or "").strip()
        
        if not subject:
            self.subject_info_label.config(text="Select a subject to view records")
            return
        
        try:
            attendance_files, msg = self.attendance_handler.get_attendance_records(subject)
            
            if len(attendance_files) == 0:
                self.subject_info_label.config(text=f"No records found for '{subject}'")
                return
            
            # Load the latest attendance file
            latest_file = max(attendance_files, key=lambda x: os.path.getmtime(x))
            
            with open(latest_file, 'r') as file:
                reader = csv.DictReader(file)
                
                self.subject_info_label.config(text=f"Subject: {subject}")
                
                row_count = 0
                rows = list(reader)
                for idx, row in enumerate(rows):
                    enrollment = row.get("Enrollment", "N/A")
                    name = row.get("Name", "N/A")
                    date = row.get("Date", "N/A")
                    time_val = row.get("Time", "N/A")
                    
                    tag = "odd" if idx % 2 else "even"
                    self.attendance_tree.insert(
                        "", 
                        "end", 
                        values=(enrollment, name, date, time_val),
                        tags=(tag,)
                    )
                    row_count += 1
                
                self.total_label.config(text=f"👥 Total: {row_count} student{'s' if row_count != 1 else ''}")
        
        except Exception as e:
            self.subject_info_label.config(text=f"⚠️ Error: {str(e)}")

    def on_subject_select(self, event=None):
        """When dropdown selection changes, refresh list"""
        # Sync variable to visible selection to avoid stale values
        try:
            self.subject_var.set(self.subject_combo.get())
        except Exception:
            pass
        self.load_attendance_list()

    # Manual entry removed; no Enter handler needed
    
    def view_attendance(self):
        """Display attendance with calculations"""
        # Use combobox text to ensure selected subject is captured
        subject = (self.subject_combo.get() or "").strip()
        
        if not subject:
            TextToSpeech.speak("Please enter subject name")
            return
        
        try:
            df, msg = self.attendance_handler.calculate_attendance(subject)
            
            if df is None:
                TextToSpeech.speak(msg)
                messagebox.showwarning("No Data", msg)
                return
            
            # Create display window
            root = tk.Tk()
            root.title(f"Attendance Report - {subject}")
            root.geometry("1000x600")
            root.configure(background="black")
            
            # Title
            title_label = tk.Label(
                root,
                text=f"📊 Attendance Report - {subject}",
                bg="black",
                fg="cyan",
                font=("arial", 14, "bold")
            )
            title_label.pack(pady=10)
            
            # Create frame for table
            table_frame = tk.Frame(root, bg="black", relief=RIDGE, bd=2)
            table_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # Scrollbars
            v_scrollbar = tk.Scrollbar(table_frame, bg="#555555")
            v_scrollbar.pack(side=RIGHT, fill=Y)
            
            h_scrollbar = tk.Scrollbar(table_frame, orient=HORIZONTAL, bg="#555555")
            h_scrollbar.pack(side=BOTTOM, fill=X)
            
            # Canvas for scrolling
            canvas = tk.Canvas(
                table_frame,
                bg="#1c1c1c",
                yscrollcommand=v_scrollbar.set,
                xscrollcommand=h_scrollbar.set,
                highlightthickness=0
            )
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            v_scrollbar.config(command=canvas.yview)
            h_scrollbar.config(command=canvas.xview)
            
            # Inner frame for widgets
            inner_frame = tk.Frame(canvas, bg="black")
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")
            
            # Display DataFrame as table
            for r in range(len(df)):
                for c in range(len(df.columns)):
                    val = df.iloc[r, c]
                    
                    # Style header row differently
                    if r == 0:
                        label = tk.Label(
                            inner_frame,
                            width=12,
                            height=1,
                            fg="cyan",
                            font=("arial", 11, "bold"),
                            bg="#333333",
                            text=str(val),
                            relief=tk.RIDGE,
                            bd=2
                        )
                    else:
                        # Highlight attendance column
                        if c == len(df.columns) - 1 and df.columns[c] == "Attendance":
                            label = tk.Label(
                                inner_frame,
                                width=12,
                                height=1,
                                fg="lime",
                                font=("arial", 11, "bold"),
                                bg="#1c1c1c",
                                text=str(val),
                                relief=tk.RIDGE,
                                bd=1
                            )
                        else:
                            label = tk.Label(
                                inner_frame,
                                width=12,
                                height=1,
                                fg="yellow",
                                font=("arial", 10),
                                bg="#1c1c1c",
                                text=str(val),
                                relief=tk.RIDGE,
                                bd=1
                            )
                    
                    label.grid(row=r, column=c, padx=2, pady=2)
            
            # Update scroll region
            inner_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            root.mainloop()
            TextToSpeech.speak("Attendance displayed successfully")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying attendance: {str(e)}")
            TextToSpeech.speak(f"Error: {str(e)}")

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
    
    def check_sheets(self):
        """Open attendance folder"""
        # Use combobox text to ensure selected subject is captured
        subject = (self.subject_combo.get() or "").strip()
        
        if not subject:
            TextToSpeech.speak("Please enter subject name")
            return
        
        success = self.attendance_handler.open_attendance_folder(subject)
        
        if not success:
            messagebox.showwarning("Not Found", f"No attendance folder found for {subject}")
            TextToSpeech.speak(f"No attendance folder found for {subject}")
        else:
            TextToSpeech.speak(f"Opening attendance folder for {subject}")
    
    def reset_attendance(self):
        """Reset attendance for subject"""
        subject = (self.subject_var.get() or self.tx.get()).strip()
        
        if not subject:
            TextToSpeech.speak("Please enter subject name")
            return
        
        confirm = messagebox.askyesno(
            "⚠️ Reset Confirmation",
            f"Delete ALL attendance records for {subject}?\n\nThis cannot be undone!"
        )
        
        if confirm:
            success, msg = self.attendance_handler.reset_subject_attendance(subject)
            
            if success:
                messagebox.showinfo("Success", msg)
                TextToSpeech.speak(msg)
                self.load_attendance_list()
            else:
                messagebox.showerror("Error", msg)
                TextToSpeech.speak(msg)
    
    # Manual typing removed; dropdown-only selection