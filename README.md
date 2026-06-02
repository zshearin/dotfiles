# dotfiles

TODO - create dotfiles

Don't have any dotfiles yet, but definitely use aliases in my `.zshrc` that run scripts for me

## Terminal Setup

- Cmux 
- [Oh my zsh](https://ohmyz.sh/#install)
- Starship theme


## Starship config (how I configured, can skip step 3 and just use existing `starship.toml`:
1. `brew install starship`
2. `eval "$(starship init zsh)"` # add to dotfiles - make sure reference to it linked
3. `starship preset catppuccin-powerline -o ~/dotfiles/starship/starship.toml` # create toml config of starship in my dotfiles - may want to change which one
4. `ln -s ~/dotfiles/starship/starship.toml ~/.config/starship.toml` # link dotfile config to comp config
5. Change starship.toml to have `[line_break]` section `disabled = false`

## add to .zshrc (using zsh folder as my home). If at work, also add work specific ones after (to overwrite):
DOTFILES="$HOME/dotfiles/zsh"

