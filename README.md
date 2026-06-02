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

## replace powerlevel 10k with starship (add starship.toml later):
brew install starship
eval "$(starship init zsh)" # add to dotfiles - make sure reference to it linked
starship preset catppuccin-powerline -o ~/dotfiles/starship/starship.toml # create toml config of starship in my dotfiles - may want to change which one
ln -s ~/dotfiles/starship/starship.toml ~/.config/starship.toml # link dotfile config to comp config

A couple notes - I think i want a config that takes it to a new line


Actually - I think I want to change from ghostty to cmux 
