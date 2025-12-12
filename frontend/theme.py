# AttendEase themed UI constants - Sharp Modern Design

# Core colors - High contrast sharp palette
PRIMARY_BG = "#080d14"       # deep black-navy (sharper)
PRIMARY_FG = "#00e5ff"       # electric cyan (brighter)
ACCENT_BG = "#0d1520"        # header background (darker)
ACCENT_FG = "#ffffff"        # pure white text
DANGER_BG = "#ff3b3b"        # vivid red
SUCCESS_BG = "#00d26a"       # vivid green
INFO_BG = "#0095ff"          # vivid blue
WARNING_BG = "#ffaa00"       # amber warning
CARD_BG = "#0f1a2a"          # card panels (sharper)
INPUT_BG = "#141e2d"         # input background
INPUT_FG = "#ffffff"         # white input text
BORDER_COLOR = "#1e3a5f"     # sharp border color
HIGHLIGHT = "#00e5ff"        # highlight/glow color

# Sharp fonts - Segoe UI for Windows crispness
TITLE_FONT = ("Segoe UI", 28, "bold")
SUBTITLE_FONT = ("Segoe UI", 14, "bold")
BUTTON_FONT = ("Segoe UI", 14, "bold")
LABEL_FONT = ("Segoe UI", 11, "bold")
SMALL_FONT = ("Segoe UI", 10)
MONO_FONT = ("Consolas", 11)

WINDOW_SIZE = "1280x720"
PADDING = 16
BUTTON_SIZE = {"height": 2, "width": 20}

# Sharp corner radius simulation
BORDER_WIDTH = 2
RELIEF_STYLE = "flat"

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

        # Treeview styling - sharper
        style.configure(
            'Treeview',
            background=INPUT_BG,
            foreground=INPUT_FG,
            fieldbackground=INPUT_BG,
            rowheight=42,
            bordercolor=BORDER_COLOR,
            borderwidth=1,
            font=('Segoe UI', 10),
        )
        style.map(
            'Treeview',
            background=[('selected', PRIMARY_FG)],
            foreground=[('selected', PRIMARY_BG)],
        )
        style.configure(
            'Treeview.Heading',
            background=ACCENT_BG,
            foreground=PRIMARY_FG,
            font=('Segoe UI', 11, 'bold'),
            borderwidth=0,
            relief='flat',
        )
        style.map(
            'Treeview.Heading',
            background=[('active', CARD_BG)],
        )

        # Combobox styling - sharp and modern
        style.configure(
            'TCombobox',
            background=PRIMARY_FG,
            foreground=PRIMARY_BG,
            fieldbackground=CARD_BG,
            selectbackground=PRIMARY_FG,
            selectforeground=PRIMARY_BG,
            bordercolor=PRIMARY_FG,
            arrowcolor=PRIMARY_FG,
            arrowsize=14,
            padding=10,
            relief='flat',
        )
        style.map(
            'TCombobox',
            fieldbackground=[('readonly', CARD_BG), ('focus', CARD_BG)],
            background=[('readonly', CARD_BG), ('active', INPUT_BG)],
            foreground=[('readonly', ACCENT_FG), ('focus', ACCENT_FG)],
            bordercolor=[('focus', PRIMARY_FG), ('active', PRIMARY_FG)],
            arrowcolor=[('focus', PRIMARY_FG), ('active', HIGHLIGHT)],
        )
        
        # Custom Sharp Combobox style
        style.configure(
            'Sharp.TCombobox',
            background=CARD_BG,
            foreground=ACCENT_FG,
            fieldbackground=CARD_BG,
            selectbackground=PRIMARY_FG,
            selectforeground=PRIMARY_BG,
            borderwidth=2,
            relief='flat',
            padding=10,
            arrowsize=16,
        )
        style.map(
            'Sharp.TCombobox',
            fieldbackground=[('readonly', CARD_BG)],
            background=[('readonly', CARD_BG), ('active', INPUT_BG), ('focus', INPUT_BG)],
            foreground=[('readonly', ACCENT_FG)],
            bordercolor=[('focus', PRIMARY_FG), ('!focus', BORDER_COLOR)],
        )
        
        # Configure the dropdown listbox colors
        root.option_add('*TCombobox*Listbox.background', CARD_BG)
        root.option_add('*TCombobox*Listbox.foreground', ACCENT_FG)
        root.option_add('*TCombobox*Listbox.selectBackground', PRIMARY_FG)
        root.option_add('*TCombobox*Listbox.selectForeground', PRIMARY_BG)
        root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 11))

        # Scrollbar styling
        style.configure(
            'Vertical.TScrollbar',
            background=CARD_BG,
            troughcolor=PRIMARY_BG,
            bordercolor=BORDER_COLOR,
            arrowcolor=PRIMARY_FG,
        )

        # Buttons
        style.configure(
            'TButton',
            background=CARD_BG,
            foreground=ACCENT_FG,
            padding=10,
            borderwidth=1,
            focusthickness=0,
            font=('Segoe UI', 11, 'bold'),
        )
        style.map(
            'TButton',
            background=[('active', INPUT_BG)],
            foreground=[('active', PRIMARY_FG)],
        )
    except Exception:
        # Safe no-op if ttk not available
        pass

def animate_window_in(win, duration=200, slide=20):
    """Smooth fade and slide-in animation with proper initialization."""
    try:
        # IMPORTANT: Hide window completely first before any geometry
        win.withdraw()
        win.attributes("-alpha", 0.0)
        win.update_idletasks()
        
        # Get geometry after withdraw
        geo = win.geometry()
        parts = geo.split("+")
        size = parts[0]
        x = int(parts[1]) if len(parts) > 1 else 0
        y = int(parts[2]) if len(parts) > 2 else 0
        start_y = y - slide
        
        # Set starting position
        win.geometry(f"{size}+{x}+{start_y}")
        
        # Now show the window (still at alpha 0)
        win.deiconify()
        win.update_idletasks()
        
        steps = 12  # More steps for smoother animation
        step_delay = duration // steps
        
        def step(i=0):
            if i > steps:
                return
            t = i / steps
            # Smooth ease-out cubic for professional feel
            t_ease = 1 - pow(1 - t, 3)
            alpha = min(1.0, t_ease)
            cur_y = int(start_y + (y - start_y) * t_ease)
            try:
                win.attributes("-alpha", alpha)
                win.geometry(f"{size}+{x}+{cur_y}")
                win.update_idletasks()
            except Exception:
                return
            if i < steps:
                win.after(step_delay, step, i + 1)
        
        # Start animation
        win.after(10, step)
    except Exception:
        # Fallback: just show the window
        try:
            win.deiconify()
            win.attributes("-alpha", 1.0)
        except:
            pass

def animate_window_out(win, callback=None, duration=150):
    """Smooth fade-out animation before closing/hiding window."""
    try:
        win.update_idletasks()
        steps = 8
        step_delay = duration // steps
        
        def step(i=0):
            if i > steps:
                if callback:
                    callback()
                return
            t = i / steps
            # Ease-in for fade out
            t_ease = t * t
            alpha = max(0.0, 1.0 - t_ease)
            try:
                win.attributes("-alpha", alpha)
                win.update_idletasks()
            except Exception:
                if callback:
                    callback()
                return
            if i < steps:
                win.after(step_delay, step, i + 1)
            else:
                if callback:
                    callback()
        
        step()
    except Exception:
        if callback:
            callback()

def create_sharp_button(parent, text, command, bg_color=None, fg_color=None, width=None):
    """Create a sharp, modern button with hover effects."""
    import tkinter as tk
    bg = bg_color or PRIMARY_FG
    fg = fg_color or PRIMARY_BG
    
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bd=0,
        font=BUTTON_FONT,
        bg=bg,
        fg=fg,
        activebackground=HIGHLIGHT,
        activeforeground=PRIMARY_BG,
        cursor="hand2",
        padx=20,
        pady=10,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
    )
    if width:
        btn.config(width=width)
    
    # Hover effects
    def on_enter(e):
        btn.config(bg=HIGHLIGHT, fg=PRIMARY_BG)
    def on_leave(e):
        btn.config(bg=bg, fg=fg)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def create_sharp_entry(parent, textvariable=None, width=25):
    """Create a sharp, modern entry field."""
    import tkinter as tk
    entry = tk.Entry(
        parent,
        bd=0,
        bg=INPUT_BG,
        fg=INPUT_FG,
        font=("Segoe UI", 12),
        insertbackground=PRIMARY_FG,
        relief="flat",
        width=width,
        highlightthickness=2,
        highlightbackground=BORDER_COLOR,
        highlightcolor=PRIMARY_FG,
    )
    if textvariable:
        entry.config(textvariable=textvariable)
    return entry

def create_sharp_label(parent, text, font_style=None, fg_color=None, bg_color=None):
    """Create a sharp label."""
    import tkinter as tk
    return tk.Label(
        parent,
        text=text,
        bg=bg_color or CARD_BG,
        fg=fg_color or ACCENT_FG,
        font=font_style or LABEL_FONT,
    )

def create_card_frame(parent, padding=20):
    """Create a sharp card container with border."""
    import tkinter as tk
    card = tk.Frame(
        parent,
        bg=CARD_BG,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        padx=padding,
        pady=padding,
    )
    return card

# ============== LOADING SCREEN ==============

class LoadingScreen:
    """A simple loading overlay that appears during window transitions."""
    
    def __init__(self, parent=None):
        import tkinter as tk
        
        # Create a new toplevel for the loading screen
        self.root = tk.Toplevel() if parent else tk.Tk()
        self.root.title("")
        self.root.configure(background=PRIMARY_BG)
        self.root.overrideredirect(True)  # Borderless
        
        # Fullscreen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Make it appear on top
        self.root.attributes("-topmost", True)
        
        # Center container
        container = tk.Frame(self.root, bg=PRIMARY_BG)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # App icon/brand
        brand_label = tk.Label(
            container,
            text="📋",
            font=("Segoe UI", 48),
            bg=PRIMARY_BG,
            fg=PRIMARY_FG
        )
        brand_label.pack(pady=(0, 10))
        
        # App name
        name_label = tk.Label(
            container,
            text=APP_BRAND,
            font=("Segoe UI", 24, "bold"),
            bg=PRIMARY_BG,
            fg=PRIMARY_FG
        )
        name_label.pack(pady=(0, 20))
        
        # Loading text with animation dots
        self.loading_label = tk.Label(
            container,
            text="Loading",
            font=("Segoe UI", 14),
            bg=PRIMARY_BG,
            fg=ACCENT_FG
        )
        self.loading_label.pack()
        
        # Loading bar container
        bar_container = tk.Frame(container, bg=BORDER_COLOR, height=4, width=200)
        bar_container.pack(pady=(15, 0))
        bar_container.pack_propagate(False)
        
        # Loading bar (animated)
        self.loading_bar = tk.Frame(bar_container, bg=PRIMARY_FG, height=4, width=0)
        self.loading_bar.place(x=0, y=0, height=4)
        
        self.dots = 0
        self.bar_width = 0
        self.animate()
        
        self.root.update()
    
    def animate(self):
        """Animate the loading dots and bar."""
        try:
            # Animate dots
            self.dots = (self.dots + 1) % 4
            dots_text = "." * self.dots
            self.loading_label.config(text=f"Loading{dots_text}")
            
            # Animate bar
            self.bar_width = (self.bar_width + 15) % 200
            self.loading_bar.place(x=0, y=0, width=self.bar_width, height=4)
            
            self.root.after(150, self.animate)
        except:
            pass
    
    def destroy(self):
        """Close the loading screen."""
        try:
            self.root.destroy()
        except:
            pass


def show_loading(duration_ms=400, callback=None):
    """Show a loading screen for a brief duration, then execute callback."""
    import tkinter as tk
    
    loading = LoadingScreen()
    
    def on_complete():
        loading.destroy()
        if callback:
            callback()
    
    loading.root.after(duration_ms, on_complete)
    return loading