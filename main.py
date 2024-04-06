import discord
from discord import app_commands
import logging, sys, os
import asyncio
from datetime import datetime

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        # set up slash command tree
        self.tree = app_commands.CommandTree(self)

        @self.tree.command(name = "connect", description = "Connects to voice channel.")
        async def slash(interaction:discord.Interaction):
            # disconnect all existing voice clients
            for voice_client in self.voice_clients:
                await voice_client.disconnect()
            # connect to calling user's voice channel and respond
            await interaction.user.voice.channel.connect()
            response = 'Connected successfully.' if self.voice_clients[0].is_connected() else 'Connecting failed.'
            await interaction.response.send_message(response ,ephemeral=True)
        
        # Disconnect from all connected voice clients    
        @self.tree.command(name = "disconnect", description = "Disconnects from voice channel.")
        async def slash(interaction:discord.Interaction):
            await interaction.response.send_message('Disconnecting...', ephemeral=True)
            for voice_client in self.voice_clients:
                await voice_client.disconnect()

        # connect to channel and set timer
        @self.tree.command(name = "start", description = "Start pomodoro timer.")
        async def slash(interaction:discord.Interaction):
            await self.reset_timer()

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

    # channel status timer
    POMODORO_SECONDS = 1200
    async def reset_timer(self):
        def unix_now():
            return (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        unix_start = unix_now()
        i = self.POMODORO_SECONDS
        while unix_now() < unix_start + self.POMODORO_SECONDS:
            # set discord activity to remaining seconds
            await self.change_presence(activity=discord.Game(str(i)))
            await asyncio.sleep(1)
            i -= 1
        voice_client: discord.VoiceClient = self.voice_clients[0]
        await self.change_presence(activity=discord.Game('Waiting...'))
        await voice_client.play(discord.FFmpegPCMAudio(source='ding.mp3'))


# create bot instance
Client(intents=discord.Intents.default())