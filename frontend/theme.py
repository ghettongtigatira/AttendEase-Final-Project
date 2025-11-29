# AttendEase themed UI constants

PRIMARY_BG = "#0f172a"       # slate-900
PRIMARY_FG = "#38bdf8"       # sky-400 accent
ACCENT_BG = "#0b1220"        # darker header
ACCENT_FG = "#e2e8f0"        # slate-200 text
DANGER_BG = "#dc2626"        # red-600
SUCCESS_BG = "#16a34a"       # green-600
INFO_BG = "#2563eb"          # blue-600
CARD_BG = "#111827"          # gray-900 card panels
INPUT_BG = "#1f2937"         # gray-800 entry background
INPUT_FG = "#e5e7eb"         # gray-200

TITLE_FONT = ("Verdana", 28, "bold")
SUBTITLE_FONT = ("Verdana", 16, "bold")
BUTTON_FONT = ("Verdana", 16)
LABEL_FONT = ("Verdana", 12, "bold")
SMALL_FONT = ("Verdana", 10)

WINDOW_SIZE = "1280x720"
PADDING = 12
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
