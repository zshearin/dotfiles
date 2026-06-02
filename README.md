# dotfiles

TODO - create dotfiles

Don't have any dotfiles yet, but definitely use aliases in my `.zshrc` that run scripts for me

## Terminal Setup

- [Ghostty](https://ghostty.org/)
- [Oh my zsh](https://ohmyz.sh/#install)
- [P10k](https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k)

### P10k config settings
- Prompt style: rainbow
- Character set: unicode
- Time: 12-hour format
- Prompt Separators: Slanted
- Prompt Heads: Sharp
- Prompt Tails: Flat
- Prompt Height: Two lines
- Prompt Connection: Disconnected
- Prompt Frame: Left
- Frame Color: Light
- Prompt Spacing: Sparse
- Icons: Few icons
- Prompt Flow: Fluent
- Enable Transient: Yes
- Instant Prompt Mode: 1 Verbose


### Color Config on iTerm

- [Use Builtin Solarized Dark](https://iterm2colorschemes.com/)
- [Set as default to all windows](https://superuser.com/questions/228965/set-default-colour-for-all-iterm2-windows)

## Random .zshrc additions:
unsetopt inc_append_history
unsetopt share_history

## Link ghostty config to this repo cloned in home:
ln -s ~/dotfiles/ghostty/.config/ghostty/config ~/.config/ghostty/config
