import discord
from discord import app_commands
import logging, sys, os
import asyncio
from datetime import datetime

# TODO: Check if timer already running
# TODO: Combine start/connect
# TODO: Make sure timer properly stops
# TODO: Add pause/stop functionality

class Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        # set up slash command tree
        self.tree = app_commands.CommandTree(self)
        
        # Disconnect from all connected voice clients    
        @self.tree.command(name = "disconnect", description = "Disconnects from voice channel.")
        async def slash(interaction:discord.Interaction):
            await interaction.response.send_message('Disconnecting...', ephemeral=True)
            for voice_client in self.voice_clients:
                await voice_client.disconnect()


        # connect to channel and set timer
        @self.tree.command(name = "start", description = "Start pomodoro timer.")
        async def slash(interaction:discord.Interaction):
            # connect to channel
            await self.connect_to_caller(interaction)
            await interaction.response.send_message('Timer started.', ephemeral=True)
            # run timers until bot is out of vc
            while self.is_voice_connected(): # does this actually work?
                await self.set_timer(1200, 'WORK')
                # stop the loop if voice is not connected
                if not self.is_voice_connected():
                    break
                await self.set_timer(300, 'BREAK')
            await self.update_status('Waiting...')

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

        # set status to waiting
        await self.update_status('Waiting...')


    # channel status timer
    async def set_timer(self, time:int, message:str):
        def unix_now():
            return (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        unix_start = unix_now()
        i = time
        while unix_now() < unix_start + time and self.is_voice_connected():
            # set discord activity to remaining time
            await self.update_status(f'{message}: ' + str(int(i/60)) + ' min')
            i = time - (unix_now() - unix_start)
            # wait 60 seconds or i seconds if less than 1 minute
            # sleep_time = 60 if i > 60 else i
            if i > 60:
                sleep_time = 60
            else:
                sleep_time = i
            await asyncio.sleep(sleep_time)

        # skip ding if voice not connected
        if not self.is_voice_connected():
            return

        # play ding sound
        voice_client: discord.VoiceClient = self.voice_clients[0]
        voice_client.play(discord.FFmpegPCMAudio(source='ding.mp3'))
        return
    
    # check if bot is connected to voice channel
    def is_voice_connected(self):
        if len(self.voice_clients) < 1:
            return False
        return self.voice_clients[0].is_connected()

    # update discord status
    async def update_status(self, text:str):
        # use discord game activity to change status
        await self.change_presence(activity=discord.Game(text))

    async def connect_to_caller(self, interaction: discord.Interaction):
        # disconnect all existing voice clients
        for voice_client in self.voice_clients:
            await voice_client.disconnect()
        # connect to calling user's voice channel and respond
        await interaction.user.voice.channel.connect()
        # response = 'Connected successfully.' if self.is_voice_connected() else 'Connecting failed.'
        # await interaction.response.send_message(response ,ephemeral=True)


# create bot instance
Client(intents=discord.Intents.default())