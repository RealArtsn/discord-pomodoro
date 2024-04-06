# discord-pomodoro

This is a discord bot designed to join a voice channel and allow discord users to work in a voice channel under a single Pomodoro timer.

https://en.wikipedia.org/wiki/Pomodoro_Technique

## Usage

Sync slash commands before usage:
```sh
python main.py sync
```

Run the bot:
```sh
python main.py
```

Use slash command `/connect` then `/start` to start the timer. Name a sound file `ding.mp3` in the directory with `main.py` to play a sound at timer completion. 

The timer will continue to loop until the bot is no longer in a voice channel. The bot can be disconnected with `/disconnect`.