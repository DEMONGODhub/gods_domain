"""
Enhanced Image Viewer - single-file Python app using Tkinter + Pillow
Features:
- Open image file or folder
- Next / Previous navigation
- Zoom in / out, Fit to window
- Rotate left / right
- Fullscreen toggle
- Slideshow play/pause
- Keyboard shortcuts and mouse wheel zoom
- Status bar showing filename / index / size

Dependencies: Pillow (PIL)
Install: pip install pillow
Run: python image_viewer.py

Author: (ROHIT) your ____ heheheheheh
"""

import os
import sys
import threading
import time
from tkinter import Tk, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTTOM, TOP, BOTH, X, Y, YES, NW, SUNKEN, FLAT, GROOVE
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

SUPPORTED_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff')

class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('Image Viewer')
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

        # Color scheme
        self.bg_color = '#2b2b2b'
        self.toolbar_bg = '#1e1e1e'
        self.button_bg = '#3c3c3c'
        self.button_fg = '#e0e0e0'
        self.button_active = '#505050'
        self.status_bg = '#1e1e1e'
        self.status_fg = '#b0b0b0'

        self.root.configure(bg=self.bg_color)
        
        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        # Top toolbar with improved styling
        toolbar = Frame(self.root, bg=self.toolbar_bg, height=50)
        toolbar.pack(side=TOP, fill=X, padx=0, pady=0)

        button_style = {
            'bg': self.button_bg,
            'fg': self.button_fg,
            'activebackground': self.button_active,
            'activeforeground': '#ffffff',
            'relief': FLAT,
            'bd': 0,
            'padx': 12,
            'pady': 6,
            'font': ('Arial', 9)
        }

        # File operations
        open_btn = Button(toolbar, text='📁 Open File', command=self.open_file, **button_style)
        open_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(open_btn, "Open image file (O)")

        open_folder_btn = Button(toolbar, text='🗂️ Open Folder', command=self.open_folder, **button_style)
        open_folder_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(open_folder_btn, "Open folder (Ctrl+O)")

        # Separator
        sep1 = Frame(toolbar, bg='#555555', width=2)
        sep1.pack(side=LEFT, fill=Y, padx=8, pady=10)

        # Navigation
        prev_btn = Button(toolbar, text='⬅️ Previous', command=self.prev_image, **button_style)
        prev_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(prev_btn, "Previous image (←)")

        next_btn = Button(toolbar, text='➡️ Next', command=self.next_image, **button_style)
        next_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(next_btn, "Next image (→)")

        # Separator
        sep2 = Frame(toolbar, bg='#555555', width=2)
        sep2.pack(side=LEFT, fill=Y, padx=8, pady=10)

        # Zoom controls
        zoom_in_btn = Button(toolbar, text='🔍+ Zoom In', command=lambda: self.zoom_by(1.25), **button_style)
        zoom_in_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(zoom_in_btn, "Zoom in (+/scroll)")

        zoom_out_btn = Button(toolbar, text='🔍- Zoom Out', command=lambda: self.zoom_by(0.8), **button_style)
        zoom_out_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(zoom_out_btn, "Zoom out (-/scroll)")

        fit_btn = Button(toolbar, text='⊡ Fit', command=self.fit_to_window, **button_style)
        fit_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(fit_btn, "Fit to window (F)")

        # Separator
        sep3 = Frame(toolbar, bg='#555555', width=2)
        sep3.pack(side=LEFT, fill=Y, padx=8, pady=10)

        # Rotation
        rotate_left_btn = Button(toolbar, text='⟲ Rotate L', command=lambda: self.rotate(-90), **button_style)
        rotate_left_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(rotate_left_btn, "Rotate left 90°")

        rotate_right_btn = Button(toolbar, text='⟳ Rotate R', command=lambda: self.rotate(90), **button_style)
        rotate_right_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(rotate_right_btn, "Rotate right 90° (R)")

        # Separator
        sep4 = Frame(toolbar, bg='#555555', width=2)
        sep4.pack(side=LEFT, fill=Y, padx=8, pady=10)

        # View modes
        self.slideshow_btn = Button(toolbar, text='▶️ Slideshow', command=self.toggle_slideshow, **button_style)
        self.slideshow_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(self.slideshow_btn, "Toggle slideshow (Space)")

        fs_btn = Button(toolbar, text='⛶ Fullscreen', command=self.toggle_fullscreen, **button_style)
        fs_btn.pack(side=LEFT, padx=2, pady=8)
        self._create_tooltip(fs_btn, "Toggle fullscreen (F11/Esc)")

        # Canvas area (a Label that holds the image)
        self.view_frame = Frame(self.root, bg=self.bg_color, bd=0)
        self.view_frame.pack(fill=BOTH, expand=YES)

        self.image_label = Label(self.view_frame, bg=self.bg_color, anchor=NW)
        self.image_label.pack(fill=BOTH, expand=YES)

        # Status bar with improved styling
        self.status = Label(
            self.root, 
            text='No image loaded  |  Use "Open File" or "Open Folder" to begin',
            relief=FLAT,
            anchor='w',
            bg=self.status_bg,
            fg=self.status_fg,
            font=('Arial', 9),
            padx=10,
            pady=5
        )
        self.status.pack(side=BOTTOM, fill=X)

    def _create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget"""
        def on_enter(event):
            tooltip = Tk()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = Label(tooltip, text=text, bg='#333333', fg='#ffffff', 
                         relief=FLAT, bd=1, font=('Arial', 8), padx=5, pady=3)
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
            self.status.config(text='No image loaded  |  Use "Open File" or "Open Folder" to begin')
            return
        path = self.images[self.index]
        fname = os.path.basename(path)
        info = (f'Image {self.index+1} of {len(self.images)}  |  '
                f'{fname}  |  '
                f'{self.img.width} × {self.img.height} px  |  '
                f'Zoom: {self.zoom:.0%}  |  '
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
            self.slideshow_btn.config(text='⏸️ Pause')
            threading.Thread(target=self._slideshow_loop, daemon=True).start()
        else:
            self.slideshow_btn.config(text='▶️ Slideshow')

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
