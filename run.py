#!/usr/bin/env python3

import discord
import os
import sys
import json
import asyncio
import logging
import websrv
import shutil
import requests
import datetime
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from _thread import start_new_thread

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

def load_opus_lib(opus_libs=OPUS_LIBS):
    if discord.opus.is_loaded():
        return True
    for opus_lib in opus_libs:
        try:
            discord.opus.load_opus(opus_lib)
            return
        except OSError:
            pass
    raise RuntimeError('Could not load an opus lib.')

conf = None

def loadConfig():
    global conf
    with open('bot.json') as data:
        conf = json.load(data)

loadConfig()
currentVoiceChannel = 0
voice = None
player = None
volume = conf['volume']
commandChannel = conf['commandChannel']
whiteList = conf['whitelist']
admins = conf['admins']
tenorapi = conf['tenor']
commandNames = None

def saveConfig():
    global conf
    global volume
    global commandChannel
    global whiteList
    global admins
    conf['volume'] = volume
    conf['commandChannel'] = commandChannel
    conf['whitelist'] = whiteList
    conf['admins'] = admins
    with open('bot.json', 'w') as data:
        json.dump(conf, data)
    loadConfig()

client = commands.Bot(command_prefix=conf['invoker'])
client.remove_command('help')

def getAllCommandNames():
    global commandNames
    names = []
    for command in client.commands:
        names.append(command.name)
    commandNames = names

@client.event
async def on_ready():
    logger.info("bot started")
    await client.change_presence(activity=discord.Game(name='limpiarme el gasoducto'))
    load_opus_lib()
    getAllCommandNames()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error

@client.command()
async def test(ctx):
    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        channel = ctx.message.channel
        await channel.send("Hello :)")
		
@client.command(name='borrar', pass_context=True)
@has_permissions(administrator=True)
async def _clear(ctx):
    def is_me(m):
        return m.author == client.user
    try:
        deleted = await ctx.channel.purge(limit=99999, check=is_me)
        await ctx.send('Me chupé 5 pijas por cada uno de los {} mensajes que borré'.format(len(deleted)))
    except Exception:
        pass
        
@_clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send('**ERROR:** Ahre que no sos admin.')
        
        
@client.command(name='borrartodo', pass_context=True)
@has_permissions(administrator=True)
async def _clearall(ctx):
    try:
        await ctx.channel.purge(limit=99999)
        await ctx.send('Me metí todos los mensajitos en la cola.')
        await ctx.message.delete()
    except Exception:
        pass

@_clearall.error
async def clearall_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send('**ERROR:** Ahre que no sos admin.')
@client.command()
async def help(ctx):
    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        channel = ctx.message.channel
        helpmessage = ctx.message.author.mention + " **You can use the following commands with this bot:**\n\n"
        if ctx.message.author.id == conf['ownerID']:
            helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
            helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
            helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
            helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
            helpmessage += "**"+conf['invoker']+"whitelist [member1] [member2] [...]:** Add one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"addadmin [member1] [member2] [...]:** Add one or mulitple members as admins. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"removewhitelist [member1] [member2] [...]:** Remove one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"removeadmin [member1] [member2] [...]:** Remove one or multiple members as admins. Use an @-mention for each member. Only the owner can use this command.\n\n"
            helpmessage += "**"+conf['invoker']+"initsoundboard:** Initialize a channel as command channel. This is needed to be able to use the whitelist/addadmin commands.\n\n"
            helpmessage += "**"+conf['invoker']+"remove [sound]:** Remove a sound by its name. Only the owner/an admin can use this command. The sound is not really deleted, just moved to a directory called \"deleted_sounds\".\n\n"
            helpmessage += "**"+conf['invoker']+"clearremovedsounds:** Remove all sounds from the \"deleted_sounds\" directory. This can notbe reversed therefore is this command only available to the owner.\n\n"
            helpmessage += "**"+conf['invoker']+"restore [sound]:** Restore a sound from the \"deleted_sounds\" directory.\n\n"
            helpmessage += "**"+conf['invoker']+"listdeleted:** Lists all removed sounds.\n\n"
        elif ctx.message.author.id in conf['admins']:
            helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
            helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
            helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
            helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
            helpmessage += "**"+conf['invoker']+"whitelist [member1] [member2] [...]:** Add one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"addadmin [member1] [member2] [...]:** Add one or mulitple members as admins. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"removewhitelist [member1] [member2] [...]:** Remove one or multiple members to the whitelist. Use an @-mention for each member.\n\n"
            helpmessage += "**"+conf['invoker']+"remove [sound]:** Remove a sound by its name. Only the owner/an admin can use this command. The sound is not really deleted, just moved to a directory called \"deleted_sounds\".\n\n"
            helpmessage += "**"+conf['invoker']+"restore [sound]:** Restore a sound from the \"deleted_sounds\" directory.\n\n"
            helpmessage += "**"+conf['invoker']+"listdeleted:** Lists all removed sounds.\n\n"
        else:
            helpmessage += "**"+conf['invoker']+"help:** Shows this help text.\n\n"
            helpmessage += "**"+conf['invoker']+"list:** Lists all available sounds.\n\n"
            helpmessage += "**"+conf['invoker']+"stop:** Stops the current sound.\n\n"
            helpmessage += "**"+conf['invoker']+"volume [1-100]:** Sets a new volume.\n\n"
        embed = discord.Embed(title=None, description=helpmessage, color=0x56a80f)
        await channel.send(content=None, tts=False, embed=embed)

@client.command()
async def removewhitelist(ctx):
    global whiteList
    if ctx.message.channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            try:
                removedUsers = []
                notRemovedUsers = []
                for user in ctx.message.mentions:
                    if user.id in whiteList:
                        whiteList.remove(user.id)
                        removedUsers.append(user.mention)
                    else:
                        notRemovedUsers.append(user.mention)
                successMessage = ""
                if len(removedUsers) > 0:
                    successMessage += "Removed " + ", ".join(removedUsers) + " from the whitelist."
                if len(notRemovedUsers) > 0:
                    successMessage += ", ".join(notRemovedUsers) + " weren't on the whitelist in the first place :smile:"
                saveConfig()
                await ctx.message.channel.send(successMessage)
            except Exception as e:
                logger.debug(str(e))
                await ctx.message.channel.send("Something went wrong.")
        else:
            await ctx.message.channel.send("Only the owner/an admin can edit the whitelist.")

@client.command()
async def removeadmin(ctx):
    global admins
    if ctx.message.channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID']:
            try:
                removedUsers = []
                notRemovedUsers = []
                for user in ctx.message.mentions:
                    if user.id in admins:
                        admins.remove(user.id)
                        removedUsers.append(user.mention)
                    else:
                        notRemovedUsers.append(user.mention)
                successMessage = ""
                if len(removedUsers) > 0:
                    successMessage += "Removed " + ", ".join(removedUsers) + " as admin."
                if len(notRemovedUsers) > 0:
                    successMessage += ", ".join(notRemovedUsers) + " weren't admin in the first place :smile:"
                saveConfig()
                await ctx.message.channel.send(successMessage)
            except Exception as e:
                logger.debug(str(e))
                await ctx.message.channel.send("Something went wrong.")
        else:
            await ctx.message.channel.send("Only the owner can remove an admin.")

@client.command()
async def whitelist(ctx):
    global whiteList
    if ctx.message.channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            try:
                addedUsers = []
                notAddedUsers = []
                for user in ctx.message.mentions:
                    if not user.id in whiteList:
                        whiteList.append(user.id)
                        addedUsers.append(user.mention)
                    else:
                        notAddedUsers.append(user.mention)
                successMessage = ""
                if len(addedUsers) > 0:
                    successMessage += "Added " + ", ".join(addedUsers) + " to the whitelist."
                if len(notAddedUsers) > 0:
                    successMessage += "Did not add " + ", ".join(notAddedUsers) + " for a second time."
                saveConfig()
                await ctx.message.channel.send(successMessage)
            except Exception as e:
                logger.debug(str(e))
                await ctx.message.channel.send("Something went wrong.")
        else:
            await ctx.message.channel.send("Only the owner/an admin is allowed to add people to the whitelist!")

@client.command()
async def addadmin(ctx):
    global admins
    if ctx.message.channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            try:
                addedUsers = []
                notAddedUsers = []
                for user in ctx.message.mentions:
                    if not user.id in admins:
                        admins.append(user.id)
                        addedUsers.append(user.mention)
                    else:
                        notAddedUsers.append(user.mention)
                successMessage = ""
                if len(addedUsers) > 0:
                    successMessage = "Added " + ", ".join(addedUsers) + " as admin."
                if len(notAddedUsers) > 0:
                    successMessage += "Did not add " + ", ".join(notAddedUsers) + " for a second time."
                saveConfig()
                await ctx.message.channel.send(successMessage)
            except Exception as e:
                logger.debug(str(e))
                await ctx.message.channel.send("Something went wrong.")
        else:
            await ctx.message.channel.send("Only the owner/an admin can add another admin.")

@client.command()
async def initsoundboard(ctx):
    global commandChannel
    if not ctx.message.channel is discord.DMChannel and not ctx.message.channel is discord.GroupChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            channel = ctx.message.channel
            try:
                commandChannel = ctx.message.channel.id
                saveConfig()
                await channel.send("Initialized this channel as command channel.")
            except Exception as e:
                logger.debug(str(e))
                await channel.send("Something went wrong. Please try again.")
        else:
            await ctx.message.channel.send("Only the owner/an admin can bind the bot to a text channel.")

@client.command(name="remove")
async def remove_sound(ctx):
    global commandChannel
    channel = ctx.message.channel
    if type(channel) is discord.DMChannel or channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            try:
                if not os.path.isdir("deleted_sounds"):
                    os.makedirs("deleted_sounds")

                removedOne = False
                for format in conf['fileformats']:
                    if os.path.exists("sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format):
                        removedOne = True
                        os.rename("sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format, "deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "remove "):] + format)
                        await channel.send("Removed sound successfully.")
                        break
                if not removedOne:
                    await channel.send("This sound doesn't exist. What are you trying to do? :smile:")

            except Exception as e:
                logger.debug(str(e))
                await channel.send("Something went wrong.\n")
        else:
            await channel.send("Only the owner/an admin can remove a sound.")

@client.command(name="restore")
async def restore_sound(ctx):
    global commandChannel
    channel = ctx.message.channel
    if type(channel) is discord.DMChannel or channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            try:
                restoredOne = False
                for format in conf['fileformats']:
                    if os.path.exists("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format):
                        restoredOne = True
                        os.rename("deleted_sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format, "sounds/" + ctx.message.content[len(conf['invoker'] + "restore "):] + format)
                        await channel.send("Restored sound successfully.")
                        break
                if not restoredOne:
                    await channel.send("This sound doesn't exist. What are you trying to do? :smile:")
            except Exception as e:
                logger.debug(str(e))
                await channel.send("Something went wrong.\n")
        else:
            await channel.send("Only the owner/an admin can restore a sound.")

@client.command(name="clearremovedsounds")
async def clear_sounds(ctx):
    global commandChannel
    channel = ctx.message.channel
    if type(channel) is discord.DMChannel or channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID']:
            try:
                shutil.rmtree("deleted_sounds")
                await channel.send("Removed all sounds in the \"deleted_sounds\" directory.")
            except Exception as e:
                logger.debug(str(e))
                await channel.send("Something went wrong. Please try again.")
        else:
            await channel.send("This command can only be used by the owner!")


@client.command()
async def list(ctx):
    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        channel = ctx.message.channel
        if ctx.message.author.dm_channel == None:
            try:
                await ctx.message.author.create_dm()
            except Exception as e:
                logger.debug(str(e))
        try:
            f = []
            dirs = os.listdir("sounds/")
            for file in dirs:
                f.append(conf['invoker'] + file[:file.rfind('.')])
            f.sort()
            fs = "\n".join(f)
            embed = discord.Embed(title="Use one of the following commands to play a sound:", description=fs, color=0xcc2f00)
            await channel.send(content=None, tts=False, embed=embed)
        except Exception as e:
            logger.debug(str(e))

@client.command(name="listdeleted")
async def list_deleted_sounds(ctx):
    global commandChannel
    channel = ctx.message.channel
    if type(channel) is discord.DMChannel or channel.id == commandChannel:
        if ctx.message.author.id == conf['ownerID'] or ctx.message.author.id in conf['admins']:
            if ctx.message.author.dm_channel == None:
                try:
                    await ctx.message.author.create_dm()
                except Exception as e:
                    logger.debug(str(e))

            if not os.path.isdir("deleted_sounds"):
                os.makedirs("deleted_sounds")

            try:
                f = []
                dirs = os.listdir("deleted_sounds/")
                for file in dirs:
                    f.append(file[:file.rfind('.')])
                f.sort()
                fs = "\n".join(f)
                if fs == "":
                    title = "There are no sounds to be restored."
                else:
                    title = "Following sounds can be restored:"
                embed = discord.Embed(title=title, description=fs, color=0xcc2f00)
                await channel.send(content=None, tts=False, embed=embed)
            except Exception as e:
                logger.debug(str(e))

@client.command()
async def stop(ctx):
    global voice
    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        if voice != None:
            voice.stop()

@client.command(name="volume")
async def set_volume(ctx):
    global volume
    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        channel = ctx.message.channel
        try:
            v = float(ctx.message.content[ctx.message.content.find(' ')+1:])
            v = int(v)
            if v < 1:
                volume = 0.01
            elif v > 100:
                volume = 1.0
            else:
                volume = float(v/100)
            saveConfig()
            await channel.send(content="Changed the volume to " + str(int(volume*100)))
        except Exception as e:
            await channel.send(content="There was an error setting the volume.")
            logger.debug(str(e))

def getListOfAliases():
    f = []
    dirs = os.listdir("sounds/")
    for file in dirs:
        f.append(file[:file.rfind('.')])
    return f

@client.command(aliases=getListOfAliases())
async def play_sound(ctx):
    global currentVoiceChannel
    global voice
    global volume
    logger.info("play sound received")

    if type(ctx.message.channel) is discord.DMChannel or ctx.message.channel.id == commandChannel:
        channel = ctx.message.channel
        guild = None
        for guilds in client.guilds:
            guild = guilds
            vchannel = ctx.message.author.voice.channel
        perm = None
        if vchannel != None:
            perm = vchannel.permissions_for(vchannel.guild.me).connect
        else:
            perm = False

        if vchannel and perm:
            try:
                if voice != None:
                    voice.stop()
                if currentVoiceChannel != vchannel:
                    if voice != None:
                        await voice.disconnect()
                    voice = await vchannel.connect()
                    currentVoiceChannel = vchannel

                for format in conf['fileformats']:
                    if os.path.exists("sounds/" + ctx.message.content[len(conf['invoker']):] + format):
                        sourceToPlay = discord.FFmpegPCMAudio('sounds/' + ctx.message.content[len(conf['invoker']):] + format)
                        sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
                        sourceToPlay.volume = volume
                        voice.play(sourceToPlay)
                        break
            except Exception as e:
                logger.debug("error while playing sound" + str(e))
        else:
            await channel.send("You're not in a voice channel or you're connected to a channel which I can't access.")

@client.event
async def on_voice_state_update(member,before,after):
    global voice
    global currentVoiceChannel
    global volume
    user = member
    perm = None
    if after.channel != None:
        perm = after.channel.permissions_for(after.channel.guild.me).connect
    else:
        perm = False

    if user != client.user and after.channel != None and perm and after.channel != before.channel:
        try:
            if voice != None:
                voice.stop()

            if currentVoiceChannel != after.channel:
                if voice != None:
                    await voice.disconnect()
                logger.debug("joining voice channel")
                voice = await after.channel.connect()
                currentVoiceChannel = after.channel

            for format in conf['fileformats']:
                if os.path.exists("sounds/" + user.name + format):
                    sourceToPlay = discord.FFmpegPCMAudio('sounds/' + user.name + format)
                    sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
                    sourceToPlay.volume = volume
                    voice.play(sourceToPlay)
                    break
        except Exception as e:
            logger.debug("error in playing join sound" + str(e))
            
@client.command()
async def reiniciar(ctx):
    await ctx.send('Ay me llaman para comerme la torta, ya vengo...')
    await asyncio.sleep(1*5)
    await ctx.bot.logout()  
    
@client.event
async def on_message(message):
    global commandNames
    if not message.author.bot:
        channel = message.channel
        if type(message.channel) is discord.DMChannel:
            if message.author.id in conf['whitelist'] or message.author.id == conf['ownerID'] or message.author.id in conf['admins']:
                if len(message.attachments) > 0:
                    logger.debug("attachement detected")
                    if message.attachments[0].filename[message.attachments[0].filename.rfind('.'):] in conf['fileformats']:
                        exists = False
                        for format in conf['fileformats']:
                            if os.path.exists("sounds/" + message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] + format):
                                exists = True

                        if message.attachments[0].filename[:message.attachments[0].filename.rfind('.')] in commandNames:
                            exists = True

                        if not exists:
                            logger.debug("trying to save new sound")
                            try:
                                await message.attachments[0].save("sounds/" + message.attachments[0].filename)
                                client.get_command("play_sound").aliases.append(message.attachments[0].filename[:message.attachments[0].filename.rfind('.')])
                                ncmd = client.get_command("play_sound")
                                client.all_commands[message.attachments[0].filename[:message.attachments[0].filename.rfind('.')]] = ncmd
                                logger.debug("file successfully received")
                                await channel.send("Sound successfully added!")
                            except Exception as e:
                                logger.debug(str(e))
                                await channel.send("Something went wrong. Please try again.")
                        else:
                            await channel.send("This sound does already exist or is the name of a command.")
                    else:
                        reply = "This is an invalid filetype. Files can be of the type:\n"
                        reply += ", ".join(conf['fileformats'])
                        await channel.send(reply)
                        logger.debug("invalid filetype")
                else:
                    await client.process_commands(message)
            else:
                await channel.send("Your are not allowed to use this bot. Please contact your admin to be added to the whitelist.")
        else:
            if len(message.attachments) > 0:
                pass
            else:
                if message.content.startswith(conf['invoker']):
                    if message.channel.id == conf['commandChannel']:
                        if message.author.id in conf['whitelist'] or message.author.id == conf['ownerID'] or message.author.id in conf['admins']:
                            await client.process_commands(message)
                        else:
                            await channel.send("You are not allowed to use this bot. Please contact your admin to be added to the whitelist.")
                    elif conf['commandChannel'] == 0:
                        if message.content.startswith(conf['invoker'] + "initsoundboard"):
                            await client.process_commands(message)
                        else:
                            if message.author.dm_channel == None:
                                try:
                                    await message.author.create_dm()
                                except Exception as e:
                                    logger.debug(str(e))
                            await message.author.dm_channel.send("The bot is not yet configured to be used in a public text channel. Please contact your admin or, if you are one, use " + conf['invoker'] + "initsoundboard to bind the bot to a text channel.")
    
    # Random gifs from tenor                    
    if message.content.startswith("-gif"):
        message_random = message.content
        split_random = message_random.split()
        datetime_now = datetime.datetime.now()
        time = datetime_now.strftime("%d/%m/%Y %H:%M:%S")
        if len(split_random) == 1:
            await message.channel.send("{} You must add a question".format(message.author.mention))
        elif len(split_random) >= 2:
            search_random = "https://api.tenor.com/v1/random?key={}&q={}&limit=1&media_filter=basic".format(tenorapi, split_random[1:])
            random_request = requests.get(search_random)
            if random_request.status_code == 200:
                try:
                    json_random = random_request.json()['results']
                    gif = json_random[0]
                    title = gif['title']
                    ID = gif['id']
                    url = gif['url']
                    gif = gif.get("media")
                    gif = gif[0]
                    gif = gif.get("gif")
                    gif = gif.get("url")
                    if title == "":
                        title = "None" 
                    random_embed = discord.Embed(title="Gif Random como tu vieja", colour=discord.Colour.blue())
                    random_embed.set_image(url=gif)
                    random_embed.set_footer(text="You sent requests at {}".format(time), icon_url=client.user.avatar_url)
                    await message.channel.send(embed=random_embed)
                except:
                    await message.channel.send("{} Tipo que ni da no encontrar nada!".format(message.author.mention))
                    
    # Random ricardo gifs from tenor                    
    if message.content.startswith("-ricardo"):
        message_random = message.content
        split_random = message_random.split()
        datetime_now = datetime.datetime.now()
        time = datetime_now.strftime("%d/%m/%Y %H:%M:%S")
        if len(split_random) == 2:
            await message.channel.send("{} Capo... vamo' arriba usa el -gif".format(message.author.mention))
        elif len(split_random) >= 1:
            search_random = "https://api.tenor.com/v1/random?key={}&q=ricardo%20milos&limit=1&media_filter=basic".format(tenorapi, split_random[1:])
            random_request = requests.get(search_random)
            if random_request.status_code == 200:
                try:
                    json_random = random_request.json()['results']
                    gif = json_random[0]
                    title = gif['title']
                    ID = gif['id']
                    url = gif['url']
                    gif = gif.get("media")
                    gif = gif[0]
                    gif = gif.get("gif")
                    gif = gif.get("url")
                    if title == "":
                        title = "None" 
                    random_embed = discord.Embed(title="Ricardo es amor ❤", colour=discord.Colour.red())
                    random_embed.set_image(url=gif)
                    random_embed.set_footer(text="no-homo", icon_url="https://i.imgur.com/4aUMTga.jpg")
#                    random_embed.set_thumbnail(url="https://i.ibb.co/dKtMKmG/tenor-logo.jpg")
                    await message.channel.send(embed=random_embed)
                except:
                    await message.channel.send("{} A perro, algo salio mal.".format(message.author.mention))
                    
def srv_sound(sound):
    global voice
    logger.info("message received")
    if voice != None:
        voice.stop()
        if voice.is_connected():
            for format in conf['fileformats']:
                if os.path.exists("sounds/" + sound + format):
                    sourceToPlay = discord.FFmpegPCMAudio('sounds/' + sound + format)
                    sourceToPlay = discord.PCMVolumeTransformer(sourceToPlay)
                    sourceToPlay.volume = volume
                    voice.play(sourceToPlay)

def srv_volume(vol):
    global volume
    try:
        v = int(vol)
        if v < 1:
            volume = 0.01
        elif v > 100:
            volume = 1.0
        else:
            volume = float(v/100)
        logger.info("set volume to" + str(volume))

    except Exception as e:
        logger.debug(str(e))

websrv.play_sound=srv_sound
websrv.set_volume=srv_volume
start_new_thread(websrv.app.run, (conf['host'], conf['port']))
client.run(conf['token'])
