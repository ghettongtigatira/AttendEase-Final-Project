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
    def __init__(self, base_dir, attendance_path, student_details_path):
        self.base_dir = base_dir
        self.attendance_path = attendance_path
        self.student_details_path = student_details_path
        self.handler = AttendanceHandler(attendance_path, student_details_path)

        # Use Toplevel instead of a new Tk root to avoid variable scope issues
        self.window = tk.Toplevel()
        self.window.title(f"{APP_BRAND} - Manage Subjects")
        self.window.geometry("720x480")
        self.window.configure(background=PRIMARY_BG)
        self.window.resizable(0, 0)

        self.subject_var = tk.StringVar()
        self.new_subject_var = tk.StringVar()

        self.setup_ui()
        self.load_subjects()

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

        body = tk.Frame(self.window, bg=PRIMARY_BG)
        body.pack(fill=BOTH, expand=True, padx=PADDING, pady=PADDING)

        left = tk.Frame(body, bg=PRIMARY_BG)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        tk.Label(left, text="Existing Subjects", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT).pack(anchor=W, padx=PADDING, pady=(PADDING, 6))
        self.subject_combo = ttk.Combobox(left, textvariable=self.subject_var, state="readonly", width=28)
        self.subject_combo.pack(anchor=W, padx=PADDING, pady=(0, PADDING))
        self.subject_combo.bind("<<ComboboxSelected>>", self.on_select_subject)

        btns = tk.Frame(left, bg=PRIMARY_BG)
        btns.pack(anchor=W, padx=PADDING, pady=(0, PADDING))

        self.remove_btn = tk.Button(
            btns, text="Remove Subject", command=self.on_remove_subject,
            bd=0, font=BUTTON_FONT, bg=DANGER_BG, fg="white",
            activebackground=ACCENT_BG, activeforeground=ACCENT_FG,
        )
        self.remove_btn.pack(side=LEFT, padx=(0, PADDING))
        self._add_button_hover(self.remove_btn, DANGER_BG, darken=True)

        open_btn = tk.Button(
            btns, text="Open Folder", command=self.on_open_folder,
            bd=0, font=BUTTON_FONT, bg=CARD_BG, fg=ACCENT_FG,
            activebackground=ACCENT_BG, activeforeground=ACCENT_FG,
        )
        open_btn.pack(side=LEFT)
        self._add_button_hover(open_btn, CARD_BG)

        # Add new subject
        right = tk.Frame(body, bg=PRIMARY_BG)
        right.pack(side=RIGHT, fill=BOTH, expand=True)

        tk.Label(right, text="Add New Subject", bg=PRIMARY_BG, fg=ACCENT_FG, font=LABEL_FONT).pack(anchor=W, padx=PADDING, pady=(PADDING, 6))
        self.new_subject_entry = tk.Entry(right, bd=0, bg=INPUT_BG, fg=INPUT_FG, font=("Verdana", 14, "bold"), relief=FLAT, width=24, textvariable=self.new_subject_var)
        self.new_subject_entry.pack(anchor=W, padx=PADDING, pady=(0, 6))

        add_btn = tk.Button(
            right, text="Add Subject", command=self.on_add_subject,
            bd=0, font=BUTTON_FONT, bg=ACCENT_BG, fg=ACCENT_FG,
            activebackground=CARD_BG, activeforeground=PRIMARY_FG,
        )
        add_btn.pack(anchor=W, padx=PADDING, pady=(0, PADDING))
        self._add_button_hover(add_btn, ACCENT_BG)

        # Status
        self.status = tk.Label(
            self.window, text="", bg=CARD_BG, fg=PRIMARY_FG,
            font=("Verdana", 12, "bold"), relief=FLAT, height=3
        )
        self.status.pack(fill=X, padx=PADDING, pady=(0, PADDING))

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
