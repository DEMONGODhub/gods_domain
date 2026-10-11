# Ranger color scheme using the repository's Dracula palette.
# Ranger terminals expose named ANSI colors, so the colors follow the
# terminal's matching Dracula palette when available.
from ranger.colorschemes.default import Default
from ranger.gui.color import cyan, green, magenta, red, yellow


class Scheme(Default):
    progress_bar_color = magenta

    def use(self, context):
        fg, bg, attr = super().use(context)

        # Keep Ranger's default layout, selection, and status behavior,
        # while changing the foreground colors to Dracula accents.
        if context.directory:
            fg = magenta
        elif context.link:
            fg = cyan if context.good else red
        elif context.executable:
            fg = green
        elif context.media:
            fg = yellow if context.image else magenta
        elif context.container:
            fg = yellow

        if context.bad:
            fg = red

        return fg, bg, attr
