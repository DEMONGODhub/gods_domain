# Geany color schemes

This folder contains the repository's Dracula theme and additional themes from the official [Geany Themes collection](https://github.com/geany/geany-themes): Gruvbox Dark, One Dark, Solarized Dark, and Solarized Light.

To add them to Geany's **View → Change Color Scheme** menu on Linux:

```sh
mkdir -p ~/.config/geany/colorschemes
cp geany/colorschemes/*.conf ~/.config/geany/colorschemes/
```

Restart Geany if it is already open. The themes change editor colors only; they do not change fonts, window size, or editor features.
