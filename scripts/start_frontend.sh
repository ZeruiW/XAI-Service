#!/usr/bin/zsh

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

nvm install v19 &&
nvm use v19 &&
(cd /root/xai-service/frontend && npm i && npm run build && npm run start)
