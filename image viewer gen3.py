"""
Professional Image Viewer - Modern Dark Theme
Features:
- Sleek dark UI with accent colors
- Smooth animations and transitions
- Professional icon set
- Advanced file browser integration
- Multiple zoom modes
- Keyboard shortcuts
- Responsive design
- Status bar with detailed info
"""

import os
import sys
import threading
import time
from tkinter import Tk, Frame, Label, Button, filedialog, LEFT, RIGHT, BOTTOM, TOP, BOTH, X, Y, YES, NW, FLAT
from tkinter import messagebox, Canvas
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import tkinter.font as tkFont

SUPPORTED_EXTS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.ico')

class ModernButton(Frame):
    """Custom modern button with hover effects"""
    def __init__(self, parent, text, command, icon=None, **kwargs):
        super().__init__(parent, bg=kwargs.get('bg', '#2a2a2a'))
        self.command = command
        self.default_bg = kwargs.get('bg', '#2a2a2a')
        self.hover_bg = kwargs.get('hover_bg', '#3a3a3a')
        self.active_bg = kwargs.get('active_bg', '#4a4a4a')
        self.fg = kwargs.get('fg', '#e0e0e0')
        self.hover_fg = kwargs.get('hover_fg', '#ffffff')
        
        self.configure(bg=self.default_bg, relief=FLAT, bd=0)
        
        # Button content
        self.label = Label(self, text=text, bg=self.default_bg, fg=self.fg,
                          font=('Segoe UI', 9), cursor='hand2', padx=12, pady=6)
        self.label.pack(fill=BOTH, expand=YES)
        
        # Bind events
        self.label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        
    def _on_enter(self, e):
        self.configure(bg=self.hover_bg)
        self.label.configure(bg=self.hover_bg, fg=self.hover_fg)
        
    def _on_leave(self, e):
        self.configure(bg=self.default_bg)
        self.label.configure(bg=self.default_bg, fg=self.fg)
        
    def _on_click(self, e):
        self.configure(bg=self.active_bg)
        self.label.configure(bg=self.active_bg)
        self.after(100, lambda: self.configure(bg=self.hover_bg))
        self.after(100, lambda: self.label.configure(bg=self.hover_bg))
        if self.command:
            self.command()


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title('Image Viewer Pro made by nishu ')
        self.root.geometry('1200x800')
        self.root.minsize(800, 600)

        self.images = []
        self.index = 0
        self.img = None
        self.tkimg = None
        self.zoom = 1.0
        self.angle = 0
        self.slideshow = False
        self.slideshow_delay = 3.0
        self.is_fullscreen = False
        self.fit_mode = True  # Auto-fit by default

        # Professional Dark Theme Colors
        self.bg_dark = '#1e1e1e'           # Main background
        self.bg_darker = '#171717'         # Darker sections
        self.bg_lighter = '#2a2a2a'        # Lighter sections
        self.toolbar_bg = '#252525'        # Toolbar background
        self.accent = '#007acc'            # Primary accent (VS Code blue)
        self.accent_hover = '#1e8dd6'      # Accent hover
        self.accent_dim = '#005a9e'        # Dimmed accent
        self.text_primary = '#e0e0e0'      # Primary text
        self.text_secondary = '#9d9d9d'    # Secondary text
        self.border = '#3e3e3e'            # Border color
        self.success = '#4ec9b0'           # Success/active color
        self.warning = '#dcdcaa'           # Warning color
        
        self.root.configure(bg=self.bg_dark)
        
        # Custom fonts
        try:
            self.font_main = tkFont.Font(family='Segoe UI', size=9)
            self.font_bold = tkFont.Font(family='Segoe UI', size=9, weight='bold')
            self.font_status = tkFont.Font(family='Consolas', size=9)
        except:
            self.font_main = tkFont.Font(family='Arial', size=9)
            self.font_bold = tkFont.Font(family='Arial', size=9, weight='bold')
            self.font_status = tkFont.Font(family='Courier', size=9)
        
        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        # Top toolbar
        toolbar = Frame(self.root, bg=self.toolbar_bg, height=50, relief=FLAT)
        toolbar.pack(side=TOP, fill=X)
        toolbar.pack_propagate(False)

        # Toolbar content container
        toolbar_content = Frame(toolbar, bg=self.toolbar_bg)
        toolbar_content.pack(fill=BOTH, expand=YES, padx=10, pady=8)

        # File operations
        file_frame = Frame(toolbar_content, bg=self.toolbar_bg)
        file_frame.pack(side=LEFT, padx=5)

        ModernButton(file_frame, '  📂 Open File  ', self.open_file,
                    bg=self.bg_lighter, hover_bg=self.accent, fg=self.text_primary,
                    hover_fg='#ffffff').pack(side=LEFT, padx=2)
        
        ModernButton(file_frame, '  📁 Open Folder  ', self.open_folder,
                    bg=self.bg_lighter, hover_bg=self.accent, fg=self.text_primary,
                    hover_fg='#ffffff').pack(side=LEFT, padx=2)

        # Separator
        Frame(toolbar_content, bg=self.border, width=1).pack(side=LEFT, fill=Y, padx=10)

        # Navigation
        nav_frame = Frame(toolbar_content, bg=self.toolbar_bg)
        nav_frame.pack(side=LEFT, padx=5)

        ModernButton(nav_frame, '  ←  ', self.prev_image,
                    bg=self.bg_lighter, hover_bg=self.accent_hover, 
                    fg=self.text_primary).pack(side=LEFT, padx=1)
        
        ModernButton(nav_frame, '  →  ', self.next_image,
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)

        # Separator
        Frame(toolbar_content, bg=self.border, width=1).pack(side=LEFT, fill=Y, padx=10)

        # Zoom controls
        zoom_frame = Frame(toolbar_content, bg=self.toolbar_bg)
        zoom_frame.pack(side=LEFT, padx=5)

        ModernButton(zoom_frame, '  🔍+  ', lambda: self.zoom_by(1.25),
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)
        
        ModernButton(zoom_frame, '  🔍−  ', lambda: self.zoom_by(0.8),
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)
        
        ModernButton(zoom_frame, '  ⊡ Fit  ', self.fit_to_window,
                    bg=self.bg_lighter, hover_bg=self.success,
                    fg=self.text_primary).pack(side=LEFT, padx=1)

        # Separator
        Frame(toolbar_content, bg=self.border, width=1).pack(side=LEFT, fill=Y, padx=10)

        # Rotation
        rotate_frame = Frame(toolbar_content, bg=self.toolbar_bg)
        rotate_frame.pack(side=LEFT, padx=5)

        ModernButton(rotate_frame, '  ↺  ', lambda: self.rotate(-90),
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)
        
        ModernButton(rotate_frame, '  ↻  ', lambda: self.rotate(90),
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)

        # Separator
        Frame(toolbar_content, bg=self.border, width=1).pack(side=LEFT, fill=Y, padx=10)

        # Playback controls
        play_frame = Frame(toolbar_content, bg=self.toolbar_bg)
        play_frame.pack(side=LEFT, padx=5)

        self.slideshow_btn_widget = ModernButton(play_frame, '  ▶ Slideshow  ', 
                                                 self.toggle_slideshow,
                                                 bg=self.bg_lighter, hover_bg=self.success,
                                                 fg=self.text_primary)
        self.slideshow_btn_widget.pack(side=LEFT, padx=1)
        
        ModernButton(play_frame, '  ⛶ Fullscreen  ', self.toggle_fullscreen,
                    bg=self.bg_lighter, hover_bg=self.accent_hover,
                    fg=self.text_primary).pack(side=LEFT, padx=1)

        # Main viewing area with border
        self.view_frame = Frame(self.root, bg=self.bg_dark)
        self.view_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)

        # Image container with subtle border
        image_container = Frame(self.view_frame, bg=self.bg_darker, 
                               highlightbackground=self.border, highlightthickness=1)
        image_container.pack(fill=BOTH, expand=YES)

        self.image_label = Label(image_container, bg=self.bg_darker, anchor='center')
        self.image_label.pack(fill=BOTH, expand=YES)

        # Status bar
        status_frame = Frame(self.root, bg=self.toolbar_bg, height=30)
        status_frame.pack(side=BOTTOM, fill=X)
        status_frame.pack_propagate(False)

        # Status content
        status_content = Frame(status_frame, bg=self.toolbar_bg)
        status_content.pack(fill=BOTH, expand=YES, padx=12, pady=5)

        self.status = Label(status_content, 
                           text='No image loaded  •  Press Ctrl+O to open folder or O to open file',
                           anchor='w', bg=self.toolbar_bg, fg=self.text_secondary,
                           font=self.font_status)
        self.status.pack(side=LEFT, fill=BOTH, expand=YES)

        # Status indicator
        self.indicator = Label(status_content, text='●', fg=self.accent, 
                              bg=self.toolbar_bg, font=('Segoe UI', 10))
        self.indicator.pack(side=RIGHT, padx=5)

    def _bind_shortcuts(self):
        self.root.bind('<Left>', lambda e: self.prev_image())
        self.root.bind('<Right>', lambda e: self.next_image())
        self.root.bind('<plus>', lambda e: self.zoom_by(1.25))
        self.root.bind('<equal>', lambda e: self.zoom_by(1.25))
        self.root.bind('<minus>', lambda e: self.zoom_by(0.8))
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen_if())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('f', lambda e: self.fit_to_window())
        self.root.bind('o', lambda e: self.open_file())
        self.root.bind('<Control-o>', lambda e: self.open_folder())
        self.root.bind('r', lambda e: self.rotate(90))
        self.root.bind('<space>', lambda e: self.toggle_slideshow())
        self.root.bind('<MouseWheel>', self._on_mousewheel)
        self.root.bind('<Button-4>', lambda e: self.zoom_by(1.15))
        self.root.bind('<Button-5>', lambda e: self.zoom_by(0.85))

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_by(1.15)
        else:
            self.zoom_by(0.85)

    def open_file(self):
        # Modern file dialog styling (platform dependent)
        path = filedialog.askopenfilename(
            title="Select an Image File",
            filetypes=[
                ('All Images', ' '.join('*'+ext for ext in SUPPORTED_EXTS)),
                ('PNG Images', '*.png'),
                ('JPEG Images', '*.jpg *.jpeg'),
                ('GIF Images', '*.gif'),
                ('WebP Images', '*.webp'),
                ('All Files', '*.*')
            ]
        )
        if not path:
            return
        
        folder = os.path.dirname(path)
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
        self.indicator.config(fg=self.success)

    def open_folder(self):
        folder = filedialog.askdirectory(title="Select Image Folder")
        if not folder:
            return
        
        files = sorted([os.path.join(folder, f) for f in os.listdir(folder) 
                       if f.lower().endswith(SUPPORTED_EXTS)])
        
        if not files:
            messagebox.showinfo('No Images Found', 
                              'No supported image files found in the selected folder.\n\n' +
                              'Supported formats: ' + ', '.join(SUPPORTED_EXTS),
                              icon='info')
            return
        
        self.images = files
        self.index = 0
        self.load_image(self.images[self.index])
        self.indicator.config(fg=self.success)

    def load_image(self, path):
        try:
            img = Image.open(path)
        except Exception as e:
            messagebox.showerror('Error Loading Image', 
                               f'Unable to open the selected image:\n\n{str(e)}',
                               icon='error')
            return
        
        self.img = img.convert('RGBA') if img.mode in ('RGBA', 'LA', 'P') else img.convert('RGB')
        self.zoom = 1.0
        self.angle = 0
        self.fit_mode = True
        self._render()
        self._update_status()

    def _render(self):
        if self.img is None:
            return
        
        # Apply rotation
        display = self.img.rotate(self.angle, expand=True, resample=Image.BICUBIC)

        # Get frame dimensions
        frame_w = max(100, self.view_frame.winfo_width() - 20)
        frame_h = max(100, self.view_frame.winfo_height() - 20)
        
        # Calculate target size
        if self.fit_mode:
            # Fit to window
            ratio = min(frame_w / display.width, frame_h / display.height)
            target_w = max(1, int(display.width * ratio))
            target_h = max(1, int(display.height * ratio))
        else:
            # Use zoom factor
            target_w = max(1, int(display.width * self.zoom))
            target_h = max(1, int(display.height * self.zoom))

        # Resize with high quality
        try:
            resized = display.resize((target_w, target_h), Image.LANCZOS)
        except Exception:
            resized = display

        self.tkimg = ImageTk.PhotoImage(resized)
        self.image_label.config(image=self.tkimg)

    def _update_status(self):
        if not self.images:
            self.status.config(text='No image loaded  •  Press Ctrl+O to open folder or O to open file',
                             fg=self.text_secondary)
            self.indicator.config(fg=self.accent)
            return
        
        path = self.images[self.index]
        fname = os.path.basename(path)
        
        # Get file size
        try:
            size_bytes = os.path.getsize(path)
            if size_bytes < 1024:
                size_str = f'{size_bytes} B'
            elif size_bytes < 1024 * 1024:
                size_str = f'{size_bytes / 1024:.1f} KB'
            else:
                size_str = f'{size_bytes / (1024 * 1024):.1f} MB'
        except:
            size_str = 'Unknown'
        
        mode_str = 'Fit' if self.fit_mode else f'{self.zoom:.0%}'
        
        info = (f'{self.index + 1}/{len(self.images)}  •  '
                f'{fname}  •  '
                f'{self.img.width}×{self.img.height}px  •  '
                f'{size_str}  •  '
                f'Zoom: {mode_str}  •  '
                f'Rotation: {self.angle}°')
        
        self.status.config(text=info, fg=self.text_primary)

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
        self.fit_mode = False
        self.zoom *= factor
        self.zoom = max(0.05, min(self.zoom, 20))
        self._render()
        self._update_status()

    def fit_to_window(self):
        if self.img is None:
            return
        self.fit_mode = True
        self.zoom = 1.0
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
        
        if self.slideshow:
            self.slideshow_btn_widget.label.config(text='  ⏸ Pause  ')
            self.indicator.config(fg=self.warning)
            threading.Thread(target=self._slideshow_loop, daemon=True).start()
        else:
            self.slideshow_btn_widget.label.config(text='  ▶ Slideshow  ')
            self.indicator.config(fg=self.success)

    def _slideshow_loop(self):
        while self.slideshow:
            time.sleep(self.slideshow_delay)
            if not self.slideshow:
                break
            self.index = (self.index + 1) % len(self.images)
            self.root.after(0, lambda: self.load_image(self.images[self.index]))


if __name__ == '__main__':
    root = Tk()
    app = ImageViewer(root)
    
    # Handle window resize
    last_size = [0, 0]
    def on_resize(event):
        if app.img is not None:
            current_size = [app.view_frame.winfo_width(), app.view_frame.winfo_height()]
            if current_size != last_size:
                last_size[0], last_size[1] = current_size
                app._render()
    
    root.bind('<Configure>', on_resize)
    root.mainloop()
