#!/usr/bin/env python3
"""
Modern QR Code Generator for Linux
Built with GTK4 + Libadwaita for 2026 design standards
an dthere are the ideas of this god too ypu full you dident mantion that f***you
althow it is much batter then my code
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GdkPixbuf, Gio, GLib
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer
from PIL import Image
import io
import os


class QRCodeWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Window setup
        self.set_title("QR Forge")
        self.set_default_size(900, 750)
        
        # Data storage
        self.url_text = ""
        self.fill_color = "#000000"
        self.back_color = "#ffffff"
        self.logo_path = None
        self.qr_image = None
        self.current_style = "square"
        
        self.build_ui()
    
    def build_ui(self):
        # Main box with toolbar view
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)
        
        # Header Bar
        header = Adw.HeaderBar()
        header.set_show_title(True)
        
        # Menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        menu_button.set_tooltip_text("Main Menu")
        header.pack_end(menu_button)
        
        # Create menu
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu.append("Keyboard Shortcuts", "app.shortcuts")
        menu_button.set_menu_model(menu)
        
        toolbar_view.add_top_bar(header)
        
        # Main content - Clamp for centered, responsive layout
        clamp = Adw.Clamp()
        clamp.set_maximum_size(800)
        clamp.set_tightening_threshold(600)
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Welcome banner
        banner_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        banner_box.set_halign(Gtk.Align.CENTER)
        
        title_label = Gtk.Label()
        title_label.set_markup('<span size="xx-large" weight="bold">QR Forge(by ronit)</span>')
        title_label.add_css_class("title-1")
        banner_box.append(title_label)
        
        subtitle_label = Gtk.Label(label="Create beautiful, customizable QR codes")
        subtitle_label.add_css_class("dim-label")
        subtitle_label.add_css_class("title-4")
        banner_box.append(subtitle_label)
        
        main_box.append(banner_box)
        
        # URL Input Group
        url_group = Adw.PreferencesGroup()
        url_group.set_title("Content")
        url_group.set_description("Enter the URL or text to encode")
        
        url_row = Adw.EntryRow()
        url_row.set_title("URL or Text")
        url_row.connect("changed", self.on_url_changed)
        self.url_entry = url_row
        url_group.add(url_row)
        
        main_box.append(url_group)
        
        # Style Customization Group
        style_group = Adw.PreferencesGroup()
        style_group.set_title("Style")
        style_group.set_description("Choose your QR code appearance rohit")
        
        # Style selector
        style_row = Adw.ComboRow()
        style_row.set_title("Pattern Style")
        style_row.set_subtitle("Select the module shape")
        
        style_model = Gtk.StringList()
        styles = ["Square (Classic)", "Rounded Corners", "Circular Dots", "Gapped Squares"]
        for style in styles:
            style_model.append(style)
        
        style_row.set_model(style_model)
        style_row.set_selected(0)
        style_row.connect("notify::selected", self.on_style_changed)
        self.style_row = style_row
        
        style_group.add(style_row)
        
        main_box.append(style_group)
        
        # Color Customization Group
        color_group = Adw.PreferencesGroup()
        color_group.set_title("Colors")
        color_group.set_description("Customize your QR code colors")
        
        # QR Color
        fill_row = Adw.ActionRow()
        fill_row.set_title("QR Code Color")
        fill_row.set_subtitle("Color of the QR pattern")
        
        fill_button = Gtk.ColorButton()
        fill_rgba = Gdk.RGBA()
        fill_rgba.parse(self.fill_color)
        fill_button.set_property("rgba", fill_rgba)
        fill_button.connect("color-set", self.on_fill_color_changed)
        fill_button.set_valign(Gtk.Align.CENTER)
        fill_row.add_suffix(fill_button)
        self.fill_button = fill_button
        
        color_group.add(fill_row)
        
        # Background Color
        back_row = Adw.ActionRow()
        back_row.set_title("Background Color")
        back_row.set_subtitle("Color of the background")
        
        back_button = Gtk.ColorButton()
        back_rgba = Gdk.RGBA()
        back_rgba.parse(self.back_color)
        back_button.set_rgba(back_rgba)
        back_button.connect("color-set", self.on_back_color_changed)
        back_button.set_valign(Gtk.Align.CENTER)
        back_row.add_suffix(back_button)
        self.back_button = back_button
        
        color_group.add(back_row)
        
        main_box.append(color_group)
        
        # Logo Group
        logo_group = Adw.PreferencesGroup()
        logo_group.set_title("Branding")
        logo_group.set_description("Add a logo to the center (optional)")
        
        logo_row = Adw.ActionRow()
        logo_row.set_title("Center Logo")
        logo_row.set_subtitle("No logo selected")
        
        logo_button = Gtk.Button(label="Choose Logo")
        logo_button.set_valign(Gtk.Align.CENTER)
        logo_button.connect("clicked", self.on_choose_logo)
        logo_row.add_suffix(logo_button)
        self.logo_row = logo_row
        
        logo_group.add(logo_row)
        
        main_box.append(logo_group)
        
        # Action Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(12)
        
        generate_btn = Gtk.Button(label="Generate QR Code")
        generate_btn.add_css_class("suggested-action")
        generate_btn.add_css_class("pill")
        generate_btn.set_size_request(180, 48)
        generate_btn.connect("clicked", self.on_generate)
        button_box.append(generate_btn)
        
        save_btn = Gtk.Button(label="Save")
        save_btn.add_css_class("pill")
        save_btn.set_size_request(120, 48)
        save_btn.connect("clicked", self.on_save)
        save_btn.set_sensitive(False)
        self.save_btn = save_btn
        button_box.append(save_btn)
        
        main_box.append(button_box)
        
        # Preview Card
        preview_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        preview_card.add_css_class("card")
        preview_card.set_size_request(-1, 350)
        
        preview_label = Gtk.Label(label="Preview")
        preview_label.add_css_class("title-4")
        preview_label.set_margin_top(16)
        preview_label.set_margin_bottom(12)
        preview_card.append(preview_label)
        
        # Preview image area
        preview_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        preview_box.set_vexpand(True)
        preview_box.set_valign(Gtk.Align.CENTER)
        preview_box.set_halign(Gtk.Align.CENTER)
        
        self.preview_image = Gtk.Picture()
        self.preview_image.set_size_request(300, 300)
        self.preview_image.set_can_shrink(True)
        
        placeholder = Gtk.Label(label="Your QR code will appear here")
        placeholder.add_css_class("dim-label")
        placeholder.set_margin_top(120)
        self.placeholder = placeholder
        
        preview_box.append(placeholder)
        preview_box.append(self.preview_image)
        
        preview_card.append(preview_box)
        
        main_box.append(preview_card)
        
        clamp.set_child(main_box)
        
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(clamp)
        
        toolbar_view.set_content(scrolled)
    
    def on_url_changed(self, entry):
        self.url_text = entry.get_text()
    
    def on_style_changed(self, combo, _pspec):
        selected = combo.get_selected()
        style_map = {0: "square", 1: "rounded", 2: "circle", 3: "gapped"}
        self.current_style = style_map.get(selected, "square")
    
    def on_fill_color_changed(self, button):
        rgba = button.get_rgba()
        self.fill_color = self.rgba_to_hex(rgba)
    
    def on_back_color_changed(self, button):
        rgba = button.get_rgba()
        self.back_color = self.rgba_to_hex(rgba)
    
    def rgba_to_hex(self, rgba):
        r = int(rgba.red * 255)
        g = int(rgba.green * 255)
        b = int(rgba.blue * 255)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def on_choose_logo(self, button):
        dialog = Gtk.FileDialog()
        
        # Create file filter for images
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/png")
        filter_images.add_mime_type("image/jpeg")
        filter_images.add_mime_type("image/gif")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_images)
        dialog.set_filters(filters)
        
        dialog.open(self, None, self.on_logo_selected)
    
    def on_logo_selected(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                self.logo_path = file.get_path()
                filename = file.get_basename()
                self.logo_row.set_subtitle(f"Selected: {filename}")
        except GLib.Error:
            pass
    
    def on_generate(self, button):
        if not self.url_text.strip():
            self.show_toast("Please enter a URL or text")
            return
        
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(self.url_text)
            qr.make(fit=True)
            
            # Apply style
            style_map = {
                "square": None,
                "rounded": RoundedModuleDrawer(),
                "circle": CircleModuleDrawer(),
                "gapped": GappedSquareModuleDrawer()
            }
            
            module_drawer = style_map[self.current_style]
            
            if module_drawer:
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    fill_color=self.fill_color,
                    back_color=self.back_color
                )
            else:
                img = qr.make_image(
                    fill_color=self.fill_color,
                    back_color=self.back_color
                )
            
            # Add logo if provided
            if self.logo_path:
                logo = Image.open(self.logo_path)
                qr_width, qr_height = img.size
                logo_size = qr_width // 5
                logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                
                logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
                img.paste(logo, logo_pos)
            
            self.qr_image = img
            
            # Display preview
            img_copy = img.copy()
            img_copy.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Convert PIL to GdkPixbuf
            buffer = io.BytesIO()
            img_copy.save(buffer, format='PNG')
            buffer.seek(0)
            
            loader = GdkPixbuf.PixbufLoader.new()
            loader.write(buffer.read())
            loader.close()
            pixbuf = loader.get_pixbuf()
            
            texture = Gdk.Texture.new_for_pixbuf(pixbuf)
            self.preview_image.set_paintable(texture)
            self.placeholder.set_visible(False)
            
            self.save_btn.set_sensitive(True)
            self.show_toast("QR code generated successfully!")
            
        except Exception as e:
            self.show_toast(f"Error: {str(e)}")
    
    def on_save(self, button):
        if not self.qr_image:
            self.show_toast("Generate a QR code first")
            return
        
        dialog = Gtk.FileDialog()
        dialog.set_initial_name("qrcode.png")
        
        # Create file filter
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG files")
        filter_png.add_pattern("*.png")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_png)
        dialog.set_filters(filters)
        
        dialog.save(self, None, self.on_save_response)
    
    def on_save_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                path = file.get_path()
                self.qr_image.save(path)
                self.show_toast(f"Saved to {os.path.basename(path)}")
        except GLib.Error:
            pass
    
    def show_toast(self, message):
        toast = Adw.Toast(title=message)
        toast.set_timeout(2)
        
        # Get the toast overlay (need to add one if not present)
        if not hasattr(self, 'toast_overlay'):
            return
        self.toast_overlay.add_toast(toast)


class QRForgeApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.github.qrforge',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        self.create_action('quit', lambda *_: self.quit(), ['<Ctrl>Q'])
        self.create_action('about', self.on_about)
        self.create_action('shortcuts', self.on_shortcuts)
    
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = QRCodeWindow(application=self)
            
            # Add toast overlay
            overlay = Adw.ToastOverlay()
            content = win.get_content()
            win.set_content(overlay)
            overlay.set_child(content)
            win.toast_overlay = overlay
        
        win.present()
    
    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)
    
    def on_about(self, action, param):
        about = Adw.AboutDialog(
            application_name="QR Forge",
            application_icon="com.github.qrforge",
            developer_name="Your Name",
            version="1.0.0",
            website="https://github.com/yourname/qrforge",
            issue_url="https://github.com/yourname/qrforge/issues",
            copyright="© 2025 Your Name",
            license_type=Gtk.License.MIT_X11,
            developers=["Your Name"],
            designers=["Your Name"],
        )
        about.present(self.props.active_window)
    
    def on_shortcuts(self, action, param):
        builder = Gtk.Builder()
        builder.add_from_string("""
        <interface>
          <object class="GtkShortcutsWindow" id="shortcuts">
            <property name="modal">1</property>
            <child>
              <object class="GtkShortcutsSection">
                <property name="section-name">shortcuts</property>
                <child>
                  <object class="GtkShortcutsGroup">
                    <property name="title" translatable="yes">General</property>
                    <child>
                      <object class="GtkShortcutsShortcut">
                        <property name="title" translatable="yes">Quit</property>
                        <property name="accelerator">&lt;Ctrl&gt;Q</property>
                      </object>
                    </child>
                  </object>
                </child>
              </object>
            </child>
          </object>
        </interface>
        """)
        shortcuts = builder.get_object("shortcuts")
        shortcuts.set_transient_for(self.props.active_window)
        shortcuts.present()


def main():
    app = QRForgeApp()
    return app.run(None)


if __name__ == "__main__":
    main()
