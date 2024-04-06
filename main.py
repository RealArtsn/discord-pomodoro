import discord
from discord import app_commands
import logging, sys, os
from datetime import datetime

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        # set up slash command tree
        self.tree = app_commands.CommandTree(self)

        # create log directory if not exists
        try:
            os.mkdir('logs')
        except FileExistsError:
            pass

        # logging handler
        self.log_handler = logging.FileHandler(filename=f'logs/{datetime.now().strftime("%y%m%d%H%M%S")}_discord.log', encoding='utf-8', mode='w')

        # Run with token or prompt if one does not exist
        try:
            with open('token', 'r') as token:
                self.run(token.read(), log_handler=self.log_handler, log_level=logging.DEBUG)
        except FileNotFoundError:
            print('Token not found. Input bot token and press enter or place it in a plaintext file named `token`.')
            token_text = input('Paste token: ')
            with open('token','w') as token:
                token.write(token_text)
                self.run(token_text, log_handler=self.log_handler, log_level=logging.DEBUG)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        # sync commands if 'sync' argument provided
        if 'sync' in sys.argv:
            print('Syncing slash commands globally...')
            await self.tree.sync()
            print('Exiting...')
            await self.close()

# create bot instance
Client(intents=discord.Intents.default())