# =====================================================
# ~/.bashrc — clean rebuild (stable & low-end friendly)
# =====================================================

# ---- Run only in interactive shells ----
case $- in
    *i*) ;;
      *) return ;;
esac

# ---- History configuration ----
HISTCONTROL=ignoreboth
HISTSIZE=4000
HISTFILESIZE=8000
shopt -s histappend
PROMPT_COMMAND="history -a"

# ---- Shell behavior ----
shopt -s checkwinsize
set -o notify

# ---- Environment ----
export EDITOR=nano
export VISUAL=nano
export PAGER=less
export TERMINAL=x-terminal-emulator

# ---- PATH (safe prepend) ----
export PATH="$HOME/bin:$HOME/.local/bin:$PATH"

# ---- Colors support ----
if command -v dircolors >/dev/null 2>&1; then
    eval "$(dircolors -b)"
fi

# ---- Aliases (safe + useful) ----
alias ls='ls --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

alias grep='grep --color=auto'
alias cls='clear'
alias h='history'

alias ..='cd ..'
alias ...='cd ../..'

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# ---- Bash completion ----
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# ---- Starship prompt (your ricing) ----
if command -v starship >/dev/null 2>&1; then
    export STARSHIP_CONFIG="$HOME/.config/starship.toml"
    eval "$(starship init bash)"
else
    # Fallback prompt (if starship not available)
    PS1='\u@\h:\w\$ '
fi

# ---- Optional trace (comment out if not needed) ----
# echo "[TRACE] bashrc loaded"
