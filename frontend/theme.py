# AttendEase themed UI constants

PRIMARY_BG = "#0c1524"       # softened deep navy
PRIMARY_FG = "#64d8ff"       # bright cyan accent
ACCENT_BG = "#0a1c33"        # header/nav background
ACCENT_FG = "#e5ecf5"        # light text
DANGER_BG = "#ef4444"        # red-500
SUCCESS_BG = "#22c55e"       # green-500
INFO_BG = "#3b82f6"          # blue-500
CARD_BG = "#0f1d34"          # card panels
INPUT_BG = "#16243a"         # input background
INPUT_FG = "#eef2ff"         # input text

TITLE_FONT = ("Verdana", 30, "bold")
SUBTITLE_FONT = ("Verdana", 16, "bold")
BUTTON_FONT = ("Verdana", 16)
LABEL_FONT = ("Verdana", 12, "bold")
SMALL_FONT = ("Verdana", 10)

WINDOW_SIZE = "1280x720"
PADDING = 16
BUTTON_SIZE = {"height": 2, "width": 20}

APP_BRAND = "AttendEase"

# Optional ttk style configuration helper
def configure_ttk_styles(root):
	try:
		import tkinter as tk
		from tkinter import ttk
		style = ttk.Style(root)
		# Use 'clam' theme for better control
		try:
			style.theme_use('clam')
		except Exception:
			pass

		# Treeview styling
		style.configure(
			'Treeview',
			background=INPUT_BG,
			foreground=INPUT_FG,
			fieldbackground=INPUT_BG,
			rowheight=26,
			bordercolor=CARD_BG,
			borderwidth=0,
		)
		style.map(
			'Treeview',
			background=[('selected', SUCCESS_BG)],
			foreground=[('selected', ACCENT_FG)],
		)
		style.configure(
			'Treeview.Heading',
			background=CARD_BG,
			foreground=ACCENT_FG,
			font=('Verdana', 11, 'bold'),
		)

		# Buttons
		style.configure(
			'TButton',
			background=CARD_BG,
			foreground=ACCENT_FG,
			padding=8,
			borderwidth=0,
			focusthickness=0,
		)
		style.map(
			'TButton',
			background=[('active', INPUT_BG)],
			foreground=[('active', PRIMARY_FG)],
		)
	except Exception:
		# Safe no-op if ttk not available
		pass

def animate_window_in(win, duration=180, slide=20):
	"""Fade and slight slide-in for a window over ~150-200ms."""
	try:
		win.update_idletasks()
		geo = win.geometry()
		parts = geo.split("+")
		size = parts[0]
		x = int(parts[1]) if len(parts) > 1 else 0
		y = int(parts[2]) if len(parts) > 2 else 0
		start_y = y - slide
		win.geometry(f"{size}+{x}+{start_y}")
		win.attributes("-alpha", 0.0)
		steps = max(6, int(duration / 20))
		def step(i=0):
			t = i / steps
			alpha = min(1.0, t)
			cur_y = int(start_y + (y - start_y) * t)
			try:
				win.attributes("-alpha", alpha)
				win.geometry(f"{size}+{x}+{cur_y}")
			except Exception:
				return
			if i < steps:
				win.after(int(duration / steps), step, i + 1)
		step()
	except Exception:
		pass
