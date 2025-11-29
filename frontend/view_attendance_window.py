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
    configure_ttk_styles
)

class ViewAttendanceWindow:
    def __init__(self, base_dir, attendance_path):
        self.base_dir = base_dir
        self.attendance_path = attendance_path
        self.attendance_handler = AttendanceHandler(attendance_path, "")
        
        self.window = tk.Tk()
        self.window.title(f"{APP_BRAND} - View Attendance")
        self.window.geometry("980x640")
        self.window.resizable(0, 0)
        self.window.configure(background=PRIMARY_BG)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup view attendance UI"""
        # Apply theme styles
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        header = tk.Frame(self.window, bg=ACCENT_BG)
        header.pack(fill=X)
        tk.Label(header, text="📑  View Attendance Records", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        tk.Label(header, text="Select subject to see summary", bg=ACCENT_BG, fg="#9fb5d9", font=SUBTITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        
        # Subject label and input (aligned neatly)
        top = tk.Frame(self.window, bg=PRIMARY_BG)
        top.pack(fill=X, padx=PADDING, pady=PADDING)
        tk.Label(top, text="Subject", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT).pack(side=LEFT, padx=(0,8))
        # Dropdown for subjects
        from tkinter import ttk
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(top, textvariable=self.subject_var, state="readonly", width=24)
        self.subject_combo.pack(side=LEFT)
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_subject_select)
        # Dropdown-only selection; removed manual entry for simplicity
        
        # Buttons frame (clean, no heavy borders; use pack for consistent layout)
        button_frame = tk.Frame(self.window, bg=PRIMARY_BG)
        button_frame.pack(fill=X, padx=PADDING, pady=(0, PADDING))
        
        view_btn = tk.Button(
            button_frame,
            text="View Attendance",
            command=self.view_attendance,
            bd=0,
            font=BUTTON_FONT,
            bg=SUCCESS_BG,
            fg=ACCENT_FG,
            padx=18,
            pady=10,
            relief=FLAT,
        )
        view_btn.pack(side=LEFT)
        self._add_button_hover(view_btn, SUCCESS_BG)
        
        sheets_btn = tk.Button(
            button_frame,
            text="Check Sheets",
            command=self.check_sheets,
            bd=0,
            font=BUTTON_FONT,
            bg=CARD_BG,
            fg=ACCENT_FG,
            padx=18,
            pady=10,
            relief=FLAT,
        )
        sheets_btn.pack(side=LEFT, padx=12)
        self._add_button_hover(sheets_btn, CARD_BG)
        
        reset_btn = tk.Button(
            button_frame,
            text="Reset Attendance",
            command=self.reset_attendance,
            bd=0,
            font=BUTTON_FONT,
            bg=DANGER_BG,
            fg="white",
            padx=18,
            pady=10,
            relief=FLAT,
        )
        reset_btn.pack(side=LEFT, padx=12)
        self._add_button_hover(reset_btn, DANGER_BG, darken=True)
        
        # Display area for attendance records
        display_label = tk.Label(
            self.window,
            text="Latest Attendance Records:",
            bg=PRIMARY_BG,
            fg=ACCENT_FG,
            font=LABEL_FONT,
        )
        display_label.pack(anchor=W, padx=PADDING, pady=(PADDING, 0))
        
        # Create frame for scrollable attendance list
        frame = tk.Frame(self.window, bg=CARD_BG)
        frame.pack(fill=BOTH, expand=True, padx=PADDING, pady=PADDING)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame, bg=CARD_BG)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Listbox to display students
        self.attendance_listbox = tk.Listbox(
            frame,
            yscrollcommand=scrollbar.set,
            bg=PRIMARY_BG,
            fg=PRIMARY_FG,
            font=("Verdana", 11),
            relief=FLAT,
            bd=0,
            selectmode=tk.SINGLE
        )
        self.attendance_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.attendance_listbox.yview)
        
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
        """Load and display attendance records"""
        self.attendance_listbox.delete(0, END)
        
        # Use combobox text to ensure selected subject is captured
        subject = (self.subject_combo.get() or "").strip()
        
        if not subject:
            self.attendance_listbox.insert(END, "📝 Enter a subject name to view attendance...")
            return
        
        try:
            attendance_files, msg = self.attendance_handler.get_attendance_records(subject)
            
            if len(attendance_files) == 0:
                self.attendance_listbox.insert(END, f"❌ No records for '{subject}'")
                return
            
            # Load the latest attendance file
            latest_file = max(attendance_files, key=lambda x: os.path.getmtime(x))
            
            with open(latest_file, 'r') as file:
                reader = csv.DictReader(file)
                
                self.attendance_listbox.insert(END, f"✓ Subject: {subject}")
                self.attendance_listbox.insert(END, "-" * 70)
                self.attendance_listbox.insert(END, f"{'Enrollment':<15} {'Name':<30} {'Date':<12} {'Time':<10}")
                self.attendance_listbox.insert(END, "=" * 70)
                
                row_count = 0
                rows = list(reader)
                for row in rows:
                    enrollment = row.get("Enrollment", "N/A")
                    name = row.get("Name", "N/A")
                    date = row.get("Date", "N/A")
                    time_val = row.get("Time", "N/A")
                    
                    display_text = f"{enrollment:<15} {name:<30} {date:<12} {time_val:<10}"
                    self.attendance_listbox.insert(END, display_text)
                    row_count += 1
                
                self.attendance_listbox.insert(END, "=" * 70)
                self.attendance_listbox.insert(END, f"👥 Total Students Marked: {row_count}")
        
        except Exception as e:
            self.attendance_listbox.insert(END, f"⚠️  Error: {str(e)}")

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