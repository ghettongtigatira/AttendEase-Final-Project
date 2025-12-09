import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import os
from backend.attendance_handler import AttendanceHandler
from backend.utils import TextToSpeech
from frontend.theme import (
    PRIMARY_BG, PRIMARY_FG, ACCENT_BG, ACCENT_FG, CARD_BG,
    INPUT_BG, INPUT_FG, TITLE_FONT, SUBTITLE_FONT, BUTTON_FONT,
    LABEL_FONT, WINDOW_SIZE, PADDING, APP_BRAND, DANGER_BG,
    configure_ttk_styles
)

class ManageSubjectsWindow:
    def __init__(self, base_dir, attendance_path, student_details_path, main_window=None):
        self.base_dir = base_dir
        self.attendance_path = attendance_path
        self.student_details_path = student_details_path
        self.handler = AttendanceHandler(attendance_path, student_details_path)
        self.main_window = main_window

        # Use Toplevel instead of a new Tk root to avoid variable scope issues
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - Manage Subjects")
        self.window.configure(background=PRIMARY_BG)
        self.window.overrideredirect(True)  # Borderless
        # Set fullscreen manually (get screen dimensions)
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry(f"{screen_width}x{screen_height}+0+0")
        self.window.bind('<Escape>', lambda e: self.go_back())  # Back on Escape
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        self.subject_var = tk.StringVar()
        self.new_subject_var = tk.StringVar()

        self.setup_ui()
        self.load_subjects()
    
    def go_back(self):
        """Go back to main window"""
        self.window.destroy()
        if self.main_window:
            self.main_window.window.deiconify()

    def setup_ui(self):
        # Apply theme styles
        try:
            configure_ttk_styles(self.window)
        except Exception:
            pass
        header = tk.Frame(self.window, bg=ACCENT_BG)
        header.pack(fill=X)
        tk.Label(header, text="📚  Manage Subjects", bg=ACCENT_BG, fg=PRIMARY_FG, font=TITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        tk.Label(header, text="Add or remove subjects", bg=ACCENT_BG, fg="#9fb5d9", font=SUBTITLE_FONT).pack(side=LEFT, padx=PADDING, pady=PADDING)
        
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
        
        # Main card (centered)
        card = tk.Frame(center_frame, bg=CARD_BG, padx=50, pady=35)
        card.place(relx=0.5, rely=0.45, anchor=CENTER)
        
        # Card title
        tk.Label(card, text="Subject Management", bg=CARD_BG, fg=PRIMARY_FG, font=("Verdana", 20, "bold")).pack(pady=(0, 25))
        
        # Two column layout
        columns = tk.Frame(card, bg=CARD_BG)
        columns.pack(fill=X)
        
        # Left column - Existing subjects
        left = tk.Frame(columns, bg=CARD_BG)
        left.pack(side=LEFT, padx=(0, 50))
        
        tk.Label(left, text="Existing Subjects", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(anchor=W, pady=(0, 10))
        self.subject_combo = ttk.Combobox(left, textvariable=self.subject_var, state="readonly", width=25, font=("Verdana", 11))
        self.subject_combo.pack(anchor=W, pady=(0, 15))
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_select_subject)
        
        btns = tk.Frame(left, bg=CARD_BG)
        btns.pack(anchor=W)
        
        self.remove_btn = tk.Button(
            btns, text="🗑️ Remove", command=self.on_remove_subject,
            bd=0, font=("Verdana", 11, "bold"), bg=DANGER_BG, fg="white",
            padx=16, pady=8, cursor="hand2"
        )
        self.remove_btn.pack(side=LEFT, padx=(0, 10))
        self._add_button_hover(self.remove_btn, DANGER_BG, darken=True)
        
        open_btn = tk.Button(
            btns, text="📂 Open Folder", command=self.on_open_folder,
            bd=0, font=("Verdana", 11, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG,
            padx=16, pady=8, cursor="hand2"
        )
        open_btn.pack(side=LEFT)
        self._add_button_hover(open_btn, PRIMARY_FG)
        
        # Right column - Add new subject
        right = tk.Frame(columns, bg=CARD_BG)
        right.pack(side=LEFT)
        
        tk.Label(right, text="Add New Subject", bg=CARD_BG, fg=ACCENT_FG, font=SUBTITLE_FONT).pack(anchor=W, pady=(0, 10))
        self.new_subject_entry = tk.Entry(right, bd=0, bg=INPUT_BG, fg=INPUT_FG, font=("Verdana", 12), relief=FLAT, width=22, textvariable=self.new_subject_var, insertbackground=INPUT_FG)
        self.new_subject_entry.pack(anchor=W, pady=(0, 15), ipady=8)
        
        add_btn = tk.Button(
            right, text="➕ Add Subject", command=self.on_add_subject,
            bd=0, font=("Verdana", 11, "bold"), bg=PRIMARY_FG, fg=PRIMARY_BG,
            padx=16, pady=8, cursor="hand2"
        )
        add_btn.pack(anchor=W)
        self._add_button_hover(add_btn, PRIMARY_FG)
        
        # Status bar at bottom of card
        self.status = tk.Label(
            card, text="Select a subject to manage", bg=INPUT_BG, fg=PRIMARY_FG,
            font=("Verdana", 11), relief=FLAT, height=2, anchor=W, padx=12
        )
        self.status.pack(fill=X, pady=(25, 0))

    def load_subjects(self):
        subjects, _ = self.handler.list_subjects()
        self.subject_combo["values"] = subjects
        self.subject_var.set("")
        self.remove_btn.configure(state=DISABLED)
        self.update_status("Select a subject to manage.")

    def on_select_subject(self, event=None):
        subject = (self.subject_combo.get() or "").strip()
        if not subject:
            self.remove_btn.configure(state=DISABLED)
            return
        # Check if subject has records; disable remove if it does
        files, _ = self.handler.get_attendance_records(subject)
        if files:
            self.remove_btn.configure(state=DISABLED)
            self.update_status(f"'{subject}' has records. Reset before removing.")
        else:
            self.remove_btn.configure(state=NORMAL)
            self.update_status(f"'{subject}' can be removed.")

    def on_remove_subject(self):
        subject = (self.subject_combo.get() or "").strip()
        if not subject:
            self.update_status("Please select a subject to remove.")
            return
        ok, msg = self.handler.remove_subject(subject)
        if ok:
            messagebox.showinfo("Removed", msg)
            TextToSpeech.speak(msg)
            self.load_subjects()
        else:
            messagebox.showwarning("Cannot Remove", msg)
            TextToSpeech.speak(msg)

    def on_open_folder(self):
        subject = (self.subject_combo.get() or "").strip()
        if not subject:
            self.update_status("Select a subject first.")
            return
        if not self.handler.open_attendance_folder(subject):
            messagebox.showwarning("Not Found", f"No folder for {subject}")
        else:
            self.update_status(f"Opened folder for {subject}")

    def on_add_subject(self):
        subject = (self.new_subject_var.get() or "").strip()
        if not subject:
            self.update_status("Enter a subject name.")
            return
        ok, msg = self.handler.add_subject(subject)
        if ok:
            messagebox.showinfo("Added", msg)
            TextToSpeech.speak(msg)
            self.new_subject_var.set("")
            self.load_subjects()
        else:
            messagebox.showerror("Error", msg)
            TextToSpeech.speak(msg)

    def update_status(self, text):
        self.status.configure(text=text)

    def run(self):
        self.window.mainloop()

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
