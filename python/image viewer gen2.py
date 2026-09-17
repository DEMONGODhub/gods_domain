"""
Enhanced Image Viewer - Linux Mint UI Theme
Features:
- Linux Mint inspired color scheme (green accents, clean flat design)
- Open image file or folder
- Next / Previous navigation
- Zoom in / out, Fit to window
- Rotate left / right
- Fullscreen toggle
- Slideshow play/pause
- Keyboard shortcuts and mouse wheel zoom
- Status bar showing filename / index / size
->a advise that you didnt want dont try to downloaad if you alreadt has them hehehehhehe
Dependencies: Pillow (PIL)
Install: pip install pillow
Run: python image_viewer.py

Author: (ROHIT) Enhanced with Linux Mint Theme
"""

import os
import sys
import threading
import time
from tkinter import Tk, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTTOM, TOP, BOTH, X, Y, YES, NW, SUNKEN, FLAT, GROOVE, RIDGE
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

SUPPORTED_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('Image Viewer - Linux Mint Style')
        self.root.geometry('1000x700')
        self.root.minsize(600, 400)

        self.images = []          # list of file paths
        self.index = 0            # current index
        self.img = None           # PIL Image
        self.tkimg = None         # PhotoImage for Tk
        self.zoom = 1.0
        self.angle = 0            # rotation
        self.slideshow = False
        self.slideshow_delay = 2.0  # seconds
        self.is_fullscreen = False

        # Linux Mint Color Scheme
        self.mint_green = '#8fa876'       # Classic Mint green
        self.mint_green_dark = '#6b8e4e'  # Darker mint green
        self.mint_green_light = '#a8c796' # Lighter mint green
        self.bg_color = '#f5f5f5'         # Light gray background (Mint-X/Y style)
        self.toolbar_bg = '#e8e8e8'       # Toolbar light gray
        self.button_bg = '#d6d6d6'        # Button background
        self.button_fg = '#2d2d2d'        # Dark text
        self.button_active = self.mint_green  # Mint green on hover
        self.button_active_fg = '#ffffff' # White text on hover
        self.status_bg = '#e8e8e8'        # Status bar background
        self.status_fg = '#3c3c3c'        # Status text
        self.border_color = '#c0c0c0'     # Subtle borders

        self.root.configure(bg=self.bg_color)
        
        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        # Top toolbar with Linux Mint styling
        toolbar = Frame(self.root, bg=self.toolbar_bg, height=60, relief=FLAT, bd=1)
        toolbar.pack(side=TOP, fill=X, padx=0, pady=0)

        # Add a subtle border at the bottom of toolbar
        toolbar_border = Frame(toolbar, bg=self.border_color, height=1)
        toolbar_border.pack(side=BOTTOM, fill=X)

        button_style = {
            'bg': self.button_bg,
            'fg': self.button_fg,
            'activebackground': self.button_active,
            'activeforeground': self.button_active_fg,
            'relief': FLAT,
            'bd': 1,
            'padx': 14,
            'pady': 8,
            'font': ('Ubuntu', 9, 'normal'),  # Ubuntu font (used in Mint)
            'cursor': 'hand2'
        }

        # Container for buttons with padding
        button_container = Frame(toolbar, bg=self.toolbar_bg)
        button_container.pack(fill=BOTH, expand=YES, padx=8, pady=8)

        # File operations
        open_btn = Button(button_container, text='📁 Open File', command=self.open_file, **button_style)
        open_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(open_btn, "Open image file (O)")
        self._add_hover_effect(open_btn)

        open_folder_btn = Button(button_container, text='🗂️ Open Folder', command=self.open_folder, **button_style)
        open_folder_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(open_folder_btn, "Open folder (Ctrl+O)")
        self._add_hover_effect(open_folder_btn)

        # Separator
        sep1 = Frame(button_container, bg=self.border_color, width=1)
        sep1.pack(side=LEFT, fill=Y, padx=10, pady=4)

        # Navigation
        prev_btn = Button(button_container, text='◀ Previous', command=self.prev_image, **button_style)
        prev_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(prev_btn, "Previous image (←)")
        self._add_hover_effect(prev_btn)

        next_btn = Button(button_container, text='Next ▶', command=self.next_image, **button_style)
        next_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(next_btn, "Next image (→)")
        self._add_hover_effect(next_btn)

        # Separator
        sep2 = Frame(button_container, bg=self.border_color, width=1)
        sep2.pack(side=LEFT, fill=Y, padx=10, pady=4)

        # Zoom controls
        zoom_in_btn = Button(button_container, text='🔍+ Zoom In', command=lambda: self.zoom_by(1.25), **button_style)
        zoom_in_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(zoom_in_btn, "Zoom in (+/scroll)")
        self._add_hover_effect(zoom_in_btn)

        zoom_out_btn = Button(button_container, text='🔍− Zoom Out', command=lambda: self.zoom_by(0.8), **button_style)
        zoom_out_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(zoom_out_btn, "Zoom out (-/scroll)")
        self._add_hover_effect(zoom_out_btn)

        fit_btn = Button(button_container, text='⊡ Fit', command=self.fit_to_window, **button_style)
        fit_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(fit_btn, "Fit to window (F)")
        self._add_hover_effect(fit_btn)

        # Separator
        sep3 = Frame(button_container, bg=self.border_color, width=1)
        sep3.pack(side=LEFT, fill=Y, padx=10, pady=4)

        # Rotation
        rotate_left_btn = Button(button_container, text='↺ Rotate L', command=lambda: self.rotate(-90), **button_style)
        rotate_left_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(rotate_left_btn, "Rotate left 90°")
        self._add_hover_effect(rotate_left_btn)

        rotate_right_btn = Button(button_container, text='↻ Rotate R', command=lambda: self.rotate(90), **button_style)
        rotate_right_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(rotate_right_btn, "Rotate right 90° (R)")
        self._add_hover_effect(rotate_right_btn)

        # Separator
        sep4 = Frame(button_container, bg=self.border_color, width=1)
        sep4.pack(side=LEFT, fill=Y, padx=10, pady=4)

        # View modes
        self.slideshow_btn = Button(button_container, text='▶ Slideshow', command=self.toggle_slideshow, **button_style)
        self.slideshow_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(self.slideshow_btn, "Toggle slideshow (Space)")
        self._add_hover_effect(self.slideshow_btn)

        fs_btn = Button(button_container, text='⛶ Fullscreen', command=self.toggle_fullscreen, **button_style)
        fs_btn.pack(side=LEFT, padx=2)
        self._create_tooltip(fs_btn, "Toggle fullscreen (F11/Esc)")
        self._add_hover_effect(fs_btn)

        # Canvas area with subtle border
        self.view_frame = Frame(self.root, bg=self.bg_color, bd=0)
        self.view_frame.pack(fill=BOTH, expand=YES, padx=4, pady=4)

        # Inner frame with border for image
        image_container = Frame(self.view_frame, bg='#ffffff', relief=FLAT, bd=1, 
                               highlightbackground=self.border_color, highlightthickness=1)
        image_container.pack(fill=BOTH, expand=YES)

        self.image_label = Label(image_container, bg='#ffffff', anchor=NW)
        self.image_label.pack(fill=BOTH, expand=YES)

        # Status bar with Mint styling
        status_frame = Frame(self.root, bg=self.status_bg, relief=FLAT, bd=1)
        status_frame.pack(side=BOTTOM, fill=X)
        
        # Top border for status bar
        status_border = Frame(status_frame, bg=self.border_color, height=1)
        status_border.pack(side=TOP, fill=X)

        self.status = Label(
            status_frame, 
            text='No image loaded  •  Use "Open File" or "Open Folder" to begin',
            relief=FLAT,
            anchor='w',
            bg=self.status_bg,
            fg=self.status_fg,
            font=('Ubuntu', 9),
            padx=12,
            pady=6
        )
        self.status.pack(side=LEFT, fill=BOTH, expand=YES)

        # Add a small Mint-themed indicator in status bar
        indicator = Label(status_frame, text='●', fg=self.mint_green, bg=self.status_bg, 
                         font=('Ubuntu', 12))
        indicator.pack(side=RIGHT, padx=10)

    def _add_hover_effect(self, button):
        """Add Linux Mint style hover effect to buttons"""
        original_bg = button.cget('bg')
        original_fg = button.cget('fg')
        
        def on_enter(e):
            button.config(bg=self.button_active, fg=self.button_active_fg)
        
        def on_leave(e):
            button.config(bg=original_bg, fg=original_fg)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def _create_tooltip(self, widget, text):
        """Create a Linux Mint styled tooltip"""
        def on_enter(event):
            tooltip = Tk()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Mint-styled tooltip
            frame = Frame(tooltip, bg=self.mint_green_dark, bd=1, relief=FLAT)
            frame.pack()
            
            label = Label(frame, text=text, bg=self.mint_green_dark, fg='#ffffff', 
                         relief=FLAT, font=('Ubuntu', 8), padx=8, pady=4)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _bind_shortcuts(self):
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<plus>', lambda e: self.zoom_by(1.25))
        self.root.bind('<equal>', lambda e: self.zoom_by(1.25))  # For easier + without shift
        self.root.bind('<minus>', lambda e: self.zoom_by(0.8))
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen_if())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('f', lambda e: self.fit_to_window())
        self.root.bind('o', lambda e: self.open_file())
        self.root.bind('<Control-o>', lambda e: self.open_folder())
        self.root.bind('r', lambda e: self.rotate(90))
        self.root.bind('<space>', lambda e: self.toggle_slideshow())
        # Mouse wheel zoom
        self.root.bind('<MouseWheel>', self._on_mousewheel)
        # For Linux / X11 mouse wheel events
        self.root.bind('<Button-4>', lambda e: self.zoom_by(1.1))
        self.root.bind('<Button-5>', lambda e: self.zoom_by(0.9))

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_by(1.1)
        else:
            self.zoom_by(0.9)

    def open_file(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[('Image Files', ' '.join('*'+ext for ext in SUPPORTED_EXTS)),
                      ('All Files', '*.*')]
        )
        if not path:
            return
        folder = os.path.dirname(path)
        # load all images from that folder for navigation
        files = sorted([os.path.join(folder, f) for f in os.listdir(folder) 
                       if f.lower().endswith(SUPPORTED_EXTS)])
        if files:
            try:
                self.index = files.index(path)
                self.images = files
            except ValueError:
                self.images = [path]
                self.index = 0
        else:
            self.images = [path]
            self.index = 0
        self.load_image(self.images[self.index])

    def open_folder(self):
        folder = filedialog.askdirectory(title="Select a folder containing images")
        if not folder:
            return
        files = sorted([os.path.join(folder, f) for f in os.listdir(folder) 
                       if f.lower().endswith(SUPPORTED_EXTS)])
        if not files:
            messagebox.showinfo('No images', 'No supported image files found in the selected folder.')
            return
        self.images = files
        self.index = 0
        self.load_image(self.images[self.index])

    def load_image(self, path):
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror('Open error', f'Unable to open image:\n{e}')
            return
        self.img = img.convert('RGBA') if img.mode in ('RGBA','LA') else img.convert('RGB')
        self.zoom = 1.0
        self.angle = 0
        self._render()
        self._update_status()

    def _render(self):
        if self.img is None:
            return
        # apply rotation
        display = self.img.rotate(self.angle, expand=True)

        # compute target size based on zoom and view_frame size
        frame_w = max(100, self.view_frame.winfo_width())
        frame_h = max(100, self.view_frame.winfo_height())
        target_w = int(display.width * self.zoom)
        target_h = int(display.height * self.zoom)

        # if image larger than frame and zoom == 1, fit to window
        if self.zoom == 1.0 and (target_w > frame_w or target_h > frame_h):
            ratio = min(frame_w / display.width, frame_h / display.height)
            target_w = max(1, int(display.width * ratio))
            target_h = max(1, int(display.height * ratio))

        try:
            resized = display.resize((target_w, target_h), Image.LANCZOS)
        except Exception:
            resized = display

        self.tkimg = ImageTk.PhotoImage(resized)
        self.image_label.config(image=self.tkimg)

    def _update_status(self):
        if not self.images:
            self.status.config(text='No image loaded  •  Use "Open File" or "Open Folder" to begin')
            return
        path = self.images[self.index]
        fname = os.path.basename(path)
        info = (f'Image {self.index+1} of {len(self.images)}  •  '
                f'{fname}  •  '
                f'{self.img.width} × {self.img.height} px  •  '
                f'Zoom: {self.zoom:.0%}  •  '
                f'Rotation: {self.angle}°')
        self.status.config(text=info)

    def prev_image(self):
        if not self.images:
            return
        self.index = (self.index - 1) % len(self.images)
        self.load_image(self.images[self.index])

    def next_image(self):
        if not self.images:
            return
        self.index = (self.index + 1) % len(self.images)
        self.load_image(self.images[self.index])

    def zoom_by(self, factor):
        if self.img is None:
            return
        self.zoom *= factor
        # clamp zoom
        self.zoom = max(0.05, min(self.zoom, 20))
        self._render()
        self._update_status()

    def fit_to_window(self):
        if self.img is None:
            return
        # compute ratio to fit
        frame_w = max(100, self.view_frame.winfo_width())
        frame_h = max(100, self.view_frame.winfo_height())
        
        # Account for rotation
        display = self.img.rotate(self.angle, expand=True)
        ratio = min(frame_w / display.width, frame_h / display.height)
        self.zoom = ratio
        self._render()
        self._update_status()

    def rotate(self, degrees):
        if self.img is None:
            return
        self.angle = (self.angle + degrees) % 360
        self._render()
        self._update_status()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def _exit_fullscreen_if(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)

    def toggle_slideshow(self):
        if not self.images:
            return
        self.slideshow = not self.slideshow
        
        # Update button text
        if self.slideshow:
            self.slideshow_btn.config(text='⏸ Pause')
            threading.Thread(target=self._slideshow_loop, daemon=True).start()
        else:
            self.slideshow_btn.config(text='▶ Slideshow')

    def _slideshow_loop(self):
        while self.slideshow:
            time.sleep(self.slideshow_delay)
            if not self.slideshow:
                break
            # advance
            self.index = (self.index + 1) % len(self.images)
            # load on main thread via after
            self.root.after(0, lambda: self.load_image(self.images[self.index]))


if __name__ == '__main__':
    root = Tk()
    app = ImageViewer(root)
    
    # Ensure UI updates trigger re-render when resizing (only if image loaded)
    last_size = [0, 0]
    def on_resize(event):
        # Only re-render if size actually changed and we have an image
        if app.img is not None:
            current_size = [app.view_frame.winfo_width(), app.view_frame.winfo_height()]
            if current_size != last_size:
                last_size[0], last_size[1] = current_size
                app._render()
    
    root.bind('<Configure>', on_resize)
    root.mainloop()
