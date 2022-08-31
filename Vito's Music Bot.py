import asyncio
import datetime
import json
import logging
import os
import random
import sys

import click
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

import cache
import functions
import pack
import spotify
import youtubeAPI

#from youtube_dl import YoutubeDL

bf = '{l_bar}{bar:50}{r_bar}{bar:-10b}'

x = datetime.datetime.now()
logging.basicConfig(
    format= u'\x1b[30;1m%(asctime)s \x1B[1m\x1B[34m%(levelname)-8s \x1B[0m\x1B[35m%(module)s.%(funcName)s \x1B[0m%(message)s' 
    if discord.utils.stream_supports_colour(sys.stdout) else u'[%(asctime)s] [%(levelname)-8s] %(module)s.%(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('./logs/{}.log'.format(x.strftime("%d-%m-%Y %H-%M-%S"))),
        logging.StreamHandler(stream=sys.stdout)
    ]
    )


with open('./config/config.json') as f:
    configuration = json.load(f)


if configuration['MaxCacheAge'] != 0: cache.clear(configuration['MaxCacheAge'])

intents = discord.Intents.all()
intents.members = True
intents.presences = True

queueMode = configuration["queueMode"]
client = commands.Bot(command_prefix='Vito ', intents=intents)
ytdl = YoutubeDL(configuration['ytdl_format_options'])
Stop = False
FirstTimeSetup = True
path = str("D:/Music/FLAC_baby!!!")     #Default path
queue = []
queue_title = []
queue_index = int(0)
playlist = []

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        global filename,queue,queue_title,queue_index,Stop,FirstTimeSetup

        try:
            data = ytdl.extract_info(url, download=False)
        except Exception as e:
            click.echo(str(e))
            logging.error(str(e))
            if len(queue) == 1: 
                Stop = True
                FirstTimeSetup = True
            temp = queue[queue_index].split("=")[-1].replace("\n","")
            del queue[queue_index]
            del queue_title[queue_index]
            click.secho(functions.timestamp()+"{} removed from queue".format(temp),fg="red")
            logging.info('{} removed from queue'.format(temp))
            temp = None
            return 0

        # loop = loop or asyncio.get_event_loop()
        # data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)

        return cls(discord.FFmpegPCMAudio(filename, **configuration['ffmpeg_options']), data=data)


async def play_next(ctx):
    global Stop,queue_index,filename,msg,FirstTimeSetup, queueMode
    if Stop == True:
        return 0

    if ctx.voice_client is None:
        logging.warning("ctx.voice_client is None, stoping playback")
        FirstTimeSetup = True
        Stop = True
        return 0


    if queue_index < len(queue):
        if functions.queue_type(queue[queue_index]) == 0: 
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(queue[queue_index]), 1)                               #local music source
        else: 
            source = await YTDLSource.from_url(queue[queue_index], loop=client.loop, stream=True)                           #online music source
            await asyncio.sleep(configuration['ffmpegWait'])                                                                #wait for ffmpeg to start
            if source == 0:
                queue_index += 1
                await play_next(ctx)
                return 0

        try:
            if queue_index < len(queue):
                msg = ('**`'+'Now playing track {}: {}'.format(queue_index,queue_title[queue_index])+'`**')
                if Stop == False: await ctx.send(msg,delete_after=10)       #now playing message
                ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))

                queue_index += 1

        except Exception as e:
            logging.error("play error: "+str(e))
            queue_index = queue_index + 1                                                                                   #move to next song in list (on error)
            await play_next(ctx)

    else:
        #print(functions.timestamp()+"play_next() - looping back to start")                                                            #play again from the start of the queue
        if queueMode == "loop":
            queue_index = 0
            await play_next(ctx)
        elif queueMode == "none":
            #stop
            Stop = True
            FirstTimeSetup = True
            return 0

async def check_if_connected_and_connect(ctx):
    if ctx.voice_client is None:
        try:
            channel = ctx.author.voice.channel

            logging.info("bot not connected to a channel, auto connecting - channel: "+str(channel))

            await channel.connect()

            if configuration["JoinLeaveMessages"]: await ctx.send(pack.pick(0))

            return True
        except discord.errors.ClientException:
            await ctx.send("You have to be connected to a voice channel")
            return False
        except Exception as e:
            logging.error(str(e))
            return False
    

class Folder_Exploration(commands.Cog):
    """Folder exploration"""
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["fp"])
    async def fplay(self, ctx, *, index):
        """Queues a file from the local filesystem"""
        global queue,FirstTimeSetup,Stop
        x_list = functions.sorted_alphanumeric(os.listdir(path))
        Stop = False

        if await check_if_connected_and_connect(ctx) == False: return 0

        if str(index.split(" ")[0]) == "range":
            await ctx.send("Queued: "+str(abs(int(index.split(" ")[1])-int(index.split(" ")[2])))+" tracks")
        elif str(index.split(" ")[0]) == "all":
            await ctx.send("Queued whole directory")   
        elif ctx.voice_client.is_playing() == True:
            await ctx.send("Queued: "+x_list[int(index)])   
                
        if index.split(" ")[0] == "range":
            for i in range(int(index.split(" ")[1]),int(index.split(" ")[2])+1):
                queue.append(path+'/'+x_list[int(i)])
                queue_title.append(x_list[int(i)])
        elif index.split(" ")[0] == "all":
            for i in range(0,len(x_list)-1):
                queue.append(path+'/'+x_list[int(i)])
                queue_title.append(x_list[int(i)])
        else:
            queue.append(path+'/'+x_list[int(index)])
            queue_title.append(x_list[int(index)])

        if FirstTimeSetup == True:
            FirstTimeSetup = False
            await play_next(ctx)

    @commands.command()
    async def cd(self, ctx, *, number):
        """Change directory using list index. Use ../ to go back one directory"""
        global path
        list_list = os.listdir(path)

        if number == '../':
            z = ""
            y = path.replace("\\","/").split("/")
            for i in range(0,len(y)-1): z = z +'/'+ y[i] #combine all splits except the last one
            path = z.replace("/","",1)

            click.secho(functions.timestamp()+"cd() - directory set to: "+path,fg="green")
            await ctx.send("Directory set to: "+path)
            await ctx.send(file=discord.File(functions.generate_dir_list(path)))
        
        elif os.path.isdir(path+'/'+list_list[int(number)]) == True:  
            try:
                path = path+'/'+list_list[int(number)]
                click.secho(functions.timestamp()+"cd() - directory set to: "+path,fg="green")
                await ctx.send("Directory set to: "+path)
                await ctx.send(file=discord.File(functions.generate_dir_list(path)))

            except: await ctx.send("Index: "+number+" out of range")
        else: await ctx.send('That is not a folder')

    @commands.command()
    async def list(self, ctx):
        """Lists all files in the current album/directory"""
        click.secho(functions.timestamp()+"list() - sending list",fg="green")
        file = functions.generate_dir_list(path)
        await ctx.send(file=discord.File(file))
        os.remove(file)

    @commands.command()
    async def folder(self, ctx, *, directory):
        """Select a folder directory that will be played"""
        global path

        if os.path.isdir(directory) == True:     
            old_path = path
            path = directory

            await ctx.send("Path set to: "+path)
            click.secho(functions.timestamp()+"folder() - folder path changed to: "+path+" Old: "+old_path,fg="green")

        else: await ctx.send('Directory: "'+path+'" does not exist')

class Media_Controls(commands.Cog):
    """Media controls"""
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pause(self, ctx):
        """Pauses music playback"""
        if await check_if_connected_and_connect(ctx) == False: return 0
        try:
            ctx.voice_client.pause()
            logging.info("Paused music playback")

            await ctx.send("Paused music playback")
        except:
            await ctx.send("Music is not playing")

    @commands.command()
    async def resume(self, ctx):
        """Resumes music playback"""
        if await check_if_connected_and_connect(ctx) == False: return 0
        try:
            ctx.voice_client.resume()
            logging.info("resumed music playback")
            await ctx.send("Resumed music playback")
        except:
            await ctx.send("Music is not paused")

    @commands.command()
    async def now(self, ctx):
        """Shows current track"""
        if await check_if_connected_and_connect(ctx) == False: return 0
        x = str(queue[queue_index-1])

        if 'http' not in x:
            x = str(queue_title[queue_index-1])

        await ctx.send("Currently playing:\n"+x)

    @commands.command()
    async def fuck(self, ctx):
        """Fixes everything, sorry im working on the shitty bugs"""
        global FirstTimeSetup,Stop,msg
        if await check_if_connected_and_connect(ctx) == False: return 0

        Stop = True
        FirstTimeSetup = True
        logging.info("stoping")

        ctx.voice_client.stop()
        await ctx.send("I hope it's fixed")

        await Media_Controls.clear(self,ctx)

    @commands.command()
    async def shuffle(self, ctx):
        global queue,queue_0je
        """Shuffles the queue"""
        if await check_if_connected_and_connect(ctx) == False: return 0
        x = random.randint
        random.Random(x).shuffle(queue)
        random.Random(x).shuffle(queue_title)
        #jump to the first song
        await Media_Controls.jump(self,ctx,number=0)
        await ctx.send("YES JAGOR THE SHUFFLE COMMAND WORKS")
        
    @commands.command(aliases=["j"])
    async def jump(self, ctx, *, number,s=False):
        """Jump to certain track using list index"""
        global queue,queue_index,FirstTimeSetup,Stop
        if await check_if_connected_and_connect(ctx) == False: return 0
        Stop = False

        try: 
            number = int(number)
        except:
            await ctx.send("Bruh thats not a number")
            return 0
    
        if len(queue)*-1 <= number < len(queue):
            if number < 0: number = len(queue)+number
            queue_index = number
            logging.info("jumping to track: "+str(number))
            ctx.voice_client.stop()     #Zaustavlja pjesmu sto ce pokrenuti after funkciju u ctx.voice_client.play
        else: await ctx.send("Number out of range [{}..{}]".format((len(queue)-1)*-1,len(queue)-1))

        if FirstTimeSetup == True:
            FirstTimeSetup = False
            await play_next(ctx)            

    @commands.command(aliases=["s"])
    async def skip(self, ctx,s=False):
        """Skips current track"""
        if await check_if_connected_and_connect(ctx) == False: return 0
        if FirstTimeSetup == True: 
            await ctx.send("Shit must be playing first before you can skip")
        else:
            logging.info("skiping to track: "+str(queue_index))
            ctx.voice_client.stop()     #Zaustavlja pjesmu sto ce pokrenuti after funkciju u ctx.voice_client.play

    @commands.command(aliases=["b"])
    async def back(self, ctx,s=False):
        global queue_index
        """Plays previous track"""
        if await check_if_connected_and_connect(ctx) == False: return 0

        if len(queue) == 0: 
            await ctx.send("Shit must be playing first before you can go back")
        else:
            await Media_Controls.jump(self,ctx,number=queue_index-2)

    @commands.command()
    async def yt(self, ctx):
        try:
            await ctx.send(file=discord.File('packs/cb3.png'))
        except:
            pass
        await ctx.send('Of course, there still is YouTube support, but the yt command has been replaced with the play command')


    @commands.command(aliases=["p"])
    async def play(self, ctx, *, search):
        """Plays music, obviously. What did you expect?"""
        global queue,queue_title,FirstTimeSetup,Stop
        if await check_if_connected_and_connect(ctx) == False: return 0

        t = functions.play_type(search)

        if t == 1:
            #PLaylist
            playlist = youtubeAPI.playlist(search)

            if playlist is None: 
                await ctx.send("Error, view console for more info")
                return

            queue.extend(playlist[0])
            queue_title.extend(playlist[1])
            await ctx.send("**[YouTube]** Queued "+str(len(playlist[1]))+" tracks")
        elif t == 0:
            #YT link

            c = cache.load(search,2)

            if c == None:
                queue.append(search)
                title = functions.get_title(search)
                queue_title.append(title)

                cache.save(search,search,title,2)
            else:
                queue.append(c['url'])
                title = c['title']
                queue_title.append(title)


            if ctx.voice_client.is_playing() == True: await ctx.send("Queued: "+title)
        elif t == 2:
            #URL
            if functions.is_supported(search) == False:
                await ctx.send("Unsupported URL")
                return 0

            queue_title.append(search)
            queue.append(search)
            if ctx.voice_client.is_playing() == True: await ctx.send("Queued: "+search)
        elif t == 3:
            #Spotify playlist
            search = search.split('playlist/')[-1].split('?')[0]

            c = cache.load(search,1)

            if c == None:
                tracks = spotify.playlist(search)

                await ctx.send('**[Spotify]** Converting tracks this may kill the bot for a bit')
                #convert to yt
                tracks = await functions.youtube_search_thread(tracks)

                queue.extend(tracks[0])
                queue_title.extend(tracks[1])

                cache.save(search, tracks[0], tracks[1], 1)

                await ctx.send("**[Spotify]** Queued "+str(len(tracks[0]))+" tracks")
            else:
                queue.extend(c['url'])
                queue_title.extend(c['title'])

                await ctx.send("**[Spotify]** Queued "+str(len(c['url']))+" tracks")


        else:

            if configuration["UseYoutubeSearchAPI"]:
                search = youtubeAPI.search(search)
            else:
                search = functions.youtube_search(search)

            if search == None:
                await ctx.send("No results found")
                return 0

            queue.append(search[0])
            queue_title.append(search[1])
            if ctx.voice_client.is_playing() == True: 
                await ctx.send("**[YouTube]** Queued: "+search[1])

        if FirstTimeSetup == True:
            Stop = False
            FirstTimeSetup = False
            await play_next(ctx)


    @commands.command(aliases=["queue"])
    async def q(self, ctx):
        """View the queue"""
        with open("cache/queue.txt", "w", encoding="utf-8") as f:

            if len(queue_title) == 0: 
                await ctx.send("The queue is empty dumbass")
                return 0

            for i in range(len(queue_title)):
                if i == queue_index-1: 
                    f.write('\t--> {}: {} <--\n'.format(i,queue_title[int(i)].replace('\n','')))
                else:
                    f.write('{}: {}\n'.format(i,queue_title[int(i)].replace('\n','')))

        await ctx.send(file=discord.File('cache/queue.txt'))
        os.remove("cache/queue.txt")

    @commands.command(aliases=["del","remove"])
    async def delete(self, ctx, integer):
        """Delete specific queued track"""
        if int(queue_index)-1 == int(integer): ctx.voice_client.stop() 
        await ctx.send("Removed: "+queue_title[int(integer)])
        del queue[int(integer)]
        del queue_title[int(integer)]

    @commands.command()
    async def clear(self, ctx):
        """Clears the queue"""
        global queue,queue_title,queue_index,Stop,FirstTimeSetup
        if len(queue_title) == 0:
            return None
        if await check_if_connected_and_connect(ctx) == False: return 0
        ctx.voice_client.stop()
        Stop = True
        queue = []
        queue_title = []
        queue_index = int(0)
        FirstTimeSetup = True

        logging.info("cleared")

    @commands.command()
    async def loop(self, ctx):
        """Toggles looping"""
        global queueMode
        if queueMode == "loop":
            queueMode = "none"
            logging.info("looping disabled")

            await ctx.send("Looping disabled")
        else:
            queueMode = "loop"
            logging.info("looping enabled")

            await ctx.send("Looping the queue")


    @commands.command(name="/0")
    async def stoper(self, ctx):
        """Outputs 5 divided by 0"""
        global FirstTimeSetup,Stop,msg

        if configuration["AllowEndSession"] == False and ctx.author.id not in configuration["Admins"]: return 0

        if await check_if_connected_and_connect(ctx) == False: return 0
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        Stop = True
        FirstTimeSetup = True
        logging.info("stoping")
        await asyncio.sleep(0.5)
        exit()  
          

@client.command()
async def clear_cache(ctx):
    """clears playlist cache"""
    if configuration["AllowClearCache"] == False and ctx.author.id not in configuration["Admins"]: return 0

    for item in os.listdir("cache/playlist"):
        os.remove("cache/playlist/"+item)
    
    logging.info("cleared")
    await ctx.send("Cleared cache")

@client.command()
async def recommend(ctx,* x):
    """Adds similar tracks"""
    for item in x:
        try:
            limit = int(item)
        except:
            pass

    if '-yt' in x:
        try:
            tracks = youtubeAPI.related(queue[queue_index-1],amount=limit)
            queue.extend(tracks[0])
            queue_title.extend(tracks[1])

            await ctx.send("**[Youtube]** Queued "+str(len(tracks[0]))+" tracks")
        except:
            pass
    else:
        tracks = spotify.getRecommendation(queue_title[queue_index-1],limit)
        await ctx.send('**[Spotify]** Converting tracks this may take a bit')
        
        tracks = await functions.youtube_search_thread(tracks)

        queue.extend(tracks[0])
        queue_title.extend(tracks[1])

        await ctx.send("**[Spotify]** Queued "+str(len(tracks[0]))+" tracks")


@client.command()
async def join(ctx):
    """Joins a voice channel"""
    await check_if_connected_and_connect(ctx)

@client.command(aliases=["exit","disconnect","fuck off"])
async def leave(ctx):
    global loopMode
    """Leaves a voice channel"""
    await Media_Controls.clear(0,ctx)
    loopMode = configuration["queueMode"]
    if configuration["JoinLeaveMessages"]: await ctx.send(pack.pick(1))
    await ctx.voice_client.disconnect()
    

@client.event
async def on_voice_state_update(member,before,after):
    global Stop, queue, queue_title, queue_index, FirstTimeSetup, loopMode
    if before.channel != None:
        vc = client.get_channel(before.channel.id)

        if client.user.id in vc.voice_states and len(vc.voice_states) == 1:
            # disconnect if the bot is the only one in the voice channel
            logging.info("Bot is alone disconnecting in {} seconds".format(configuration["AloneTime"]))
            await asyncio.sleep(configuration["AloneTime"])
        else:
            return 0

        vc = client.get_channel(before.channel.id)

        if client.user.id in vc.voice_states and len(vc.voice_states) == 1:
            guild = client.get_guild(before.channel.guild.id)
            guild.voice_client.stop()

            await member.guild.voice_client.disconnect()
            Stop = True
            loopMode = configuration["queueMode"]
            queue = []
            queue_title = []
            queue_index = int(0)
            FirstTimeSetup = True
            logging.info("disconnected")
        else:
            logging.info("disconnect canceled")

    else:
        return 0

@client.event
async def on_ready():
    await client.add_cog(Media_Controls(client))
    logging.info('Logged in as {0} ({0.id}) -Version 4.7'.format(client.user))

    await client.change_presence(activity=discord.Game(name="with your mother"))
    #logging.info('Configuration:\n'+json.dumps(configuration,indent=4))




if configuration["AllowHostLocalFiles"]: client.add_cog(Folder_Exploration(client))
#if configuration["EnableTestCommands"]: client.add_cog(Test_Commands(client))

with open('./config/token.json', 'r') as f:
    token = json.load(f)

if token['token'] == 'DISCORD_BOT_TOKEN':
    click.secho('Add your discord bot token in ./config/token.json',fg='red')
    exit()

if '--debug' in sys.argv:
    click.secho("debugMode is enabled",fg="yellow")
    try:
        token = token['token_debug']
    except:
        token = token['token']  
else:
    token = token['token']


client.run(token)

