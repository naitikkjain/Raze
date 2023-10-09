import discord
import jishaku
import discord.ui
import wavelink
import sqlite3
import random
import os
import datetime
from discord.ext import commands
from collections import deque
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
from discord.ext.commands import has_role
import json
import psutil
badges_data_file = "badges_data.json"
con = sqlite3.connect('database.db')
cur = con.cursor()
ignored_channels = []
blacklist = []

async def get_prefix(client, message):
  cur.execute(f"SELECT users FROM Np")
  NP = cur.fetchall()
  if message.author.id in ([int(i[0]) for i in NP]):
    a = commands.when_mentioned_or('', "?")(client, message)
    return sorted(a, reverse=True)
  else:
    return commands.when_mentioned_or("?")(client, message)

start_time = datetime.datetime.now()

queuee = deque()
client = commands.Bot(command_prefix=get_prefix,
                      intents=discord.Intents.all(),
                      case_insensitive=True,
                      strip_after_prefix=True)

def load_ignored_channels():
    with open('ignored_channels.json', 'r') as f:
        ignored_channels.extend(json.load(f))

def save_ignored_channels():
    with open('ignored_channels.json', 'w') as f:
        json.dump(ignored_channels, f)

def load_blacklist():
    with open('blacklist.json', 'r') as f:
        blacklist.extend(json.load(f))

def save_blacklist():
    with open('blacklist.json', 'w') as f:
        json.dump(blacklist, f)    

def is_music_dj():
    async def predicate(ctx):
        music_role = discord.utils.get(ctx.guild.roles, name='dj')
        if music_role in ctx.author.roles:
            return True
        else:
            rode1 = discord.Embed(
            description=f"You need the `dj` role to use this command.",
            colour=0x2b2d31)
            rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode1)
            return False
    
    return commands.check(predicate)

afk_file = "afk_data.json"
with open(afk_file, "w") as f:
    json.dump({}, f)
        
if not os.path.exists(badges_data_file):
    with open(badges_data_file, "w") as f:
        json.dump({}, f)

predefined_badges = {
    "Dev": "Developer",
    "Owner": "Owner",
    "Special": "Special",
    "Friend": "Friend",
}

#on_Ready
@client.event
async def on_connect():
  await client.change_presence(status=discord.Status.idle,
                               activity=discord.Activity(
                                 type=discord.ActivityType.listening,
                                 name="?help"))

@client.event
async def setup_hook():
  cur.execute("CREATE TABLE IF NOT EXISTS Np(users)")
  print("Table Initated")

#jsk/ready
@client.event
async def on_ready():
  await client.load_extension("jishaku")
  client.owner_ids = [1137444075151311028]
  client.loop.create_task(node_connect())
  print(f"Connected as {client.user}")
  load_ignored_channels()
  load_blacklist()

#node connect
async def node_connect():
  await client.wait_until_ready()
  await wavelink.NodePool.create_node(bot=client,
                                      host="lava4.horizxon.studio",
                                      port=80,
                                      password="horizxon.studio",
                                      https=False)


@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
  print(f"Node {node.identifier} is ready")

#play
@client.command(aliases=['p'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def play(ctx: commands.Context, *, search: wavelink.YouTubeTrack):
  if not ctx.voice_client:
    vc = wavelink.player = await ctx.author.voice.channel.connect(
      cls=wavelink.Player)
  if not getattr(ctx.author.voice, "channel", None):
    rode9 = discord.Embed(
    description="You are not in a voice channel!",
    colour=0x2b2d31,
    )
    rode9.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode9, mention_author=False)

  else:
    vc: wavelink.Player = ctx.voice_client
  if not vc.is_playing() and not queuee:
    await vc.play(search)
    rode2 = discord.Embed(
      description=f"Started playing: {search.title}",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode2, mention_author=False)

  else:
    queuee.append(search)
    rode = discord.Embed(
      description=f"Added to queue: {search.title}",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)   
    
#pause
@client.command()
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def pause(ctx):
  if not ctx.voice_client:
    rode3 = discord.Embed(
      description="I am not playing anything!",
      colour=0x2b2d31,
    )
    rode3.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode3, mention_author=False)
  elif not getattr(ctx.author.voice, "channel", None):
    rode2 = discord.Embed(
      description="You are not in a voice channel!",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode2, mention_author=False)
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.pause()
  rode = discord.Embed(
    description="Paused the player!",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#resume
@client.command()
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def resume(ctx):
  if not ctx.voice_client:
    rode3 = discord.Embed(
      description="I am not playing anything!",
      colour=0x2b2d31,
    )
    rode3.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode3, mention_author=False)
  elif not getattr(ctx.author.voice, "channel", None):
    rode2 = discord.Embed(
      description="You are not in a voice channel!",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode2, mention_author=False)
  else:
    vc: wavelink.Player = ctx.voice_client
  await vc.resume()
  rode = discord.Embed(
    description="Resumed the player!",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#stop
@client.command(aliases=['dc'])
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def stop(ctx):
  if not ctx.voice_client:
    rode3 = discord.Embed(
      description="I am not playing anything!",
      colour=0x2b2d31,
    )
    rode3.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode3, mention_author=False)
  elif not getattr(ctx.author.voice, "channel", None):
    rode2 = discord.Embed(
      description="You are not in a voice channel!",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    return await ctx.reply(embed=rode2, mention_author=False)

  vc: wavelink.Player = ctx.voice_client
  if queuee:
    queuee.clear()

  await vc.stop()
  await vc.disconnect()
  rode = discord.Embed(
    description="Stopped the music and disconnected!",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#queue
@client.command(aliases=['q'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def queue(ctx: commands.Context):
  if not queuee:
    rode2 = discord.Embed(
      description="The queue is empty!",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode2, mention_author=False)

  else:
    queue_list = "\n".join(
      [f"{index+1}. {track.title}" for index, track in enumerate(queuee)])
    rode = discord.Embed(
      description=f"Queue:\n{queue_list}",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#volume
@client.command(aliases=['vol'])
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def volume(ctx: commands.Context, volume: int):
  if not ctx.voice_client:
    rode4 = discord.Embed(
      description="I am not in a vc!",
      colour=0x2b2d31,
    )
    rode4.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode4, mention_author=False)
    return

  vc: wavelink.Player = ctx.voice_client

  if not vc.is_playing:
    rode3 = discord.Embed(
      description="I am not playing anything!",
      colour=0x2b2d31,
    )
    rode3.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode3, mention_author=False)
    return

  if not 0 <= volume <= 100:
    rode2 = discord.Embed(
      description="Please provide a volume to set in between 0 to 100!",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode2, mention_author=False)
    return

  await vc.set_volume(volume)
  rode = discord.Embed(
    description=f"Volume set to {volume}%",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#clearqueue
@client.command(aliases=['cq'])
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def clearqueue(ctx: commands.Context):
  queuee.clear()
  rode = discord.Embed(
    description="Cleared The Queue!",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#remove
@client.command(aliases=['r'])
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def remove(ctx: commands.Context, index: int):
  if index < 1 or index > len(queuee):
    rode = discord.Embed(
      description="Invalid index!",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    removed_track = queuee[index - 1]
    queuee.remove(removed_track)
    rode2 = discord.Embed(
      description=f"Removed from queue: {removed_track.title}",
      colour=0x2b2d31,
    )
    rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode2, mention_author=False)

#skip
@client.command(aliases=['s'])
@is_music_dj()
@commands.cooldown(1, 5, commands.BucketType.user)
async def skip(ctx: commands.Context):
  vc: wavelink.Player = ctx.voice_client

  if not vc or not vc.is_playing():
    rode = discord.Embed(
      description="I am not playing anything!",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
    return

  await vc.stop()
  rode2 = discord.Embed(
    description="Skipped the current song!",
    colour=0x2b2d31,
  )
  rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode2, mention_author=False)

  if queue:
    next_track = queuee.popleft()
    await vc.play(next_track)
    rode3 = discord.Embed(
      description=f"Started playing: {next_track.title}",
      colour=0x2b2d31,
    )
    rode3.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode3, mention_author=False)

#np
@client.command(aliases=['anp'])
@commands.is_owner()
async def npadd(ctx, user: discord.User):

  cur.execute("SELECT users FROM Np")
  result = cur.fetchall()

  if user.id not in [int(i[0]) for i in result]:
    cur.execute(f"INSERT INTO Np(users) VALUES(?)", (user.id, ))
    rode = discord.Embed(
      description=f"Successfully added {user} to no prefix!",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

  else:

    await ctx.reply("That user is already in no prefix!", mention_author=False)

  con.commit()

@client.command(aliases=['rnp'])
@commands.is_owner()
async def npremove(ctx, user: discord.User):

  cur.execute("SELECT users FROM Np")
  result = cur.fetchall()

  if user.id in [int(i[0]) for i in result]:
    cur.execute(f"DELETE FROM Np WHERE users = ?", (user.id, ))
    rode = discord.Embed(
      description=f"Successfully removed {user} from no prefix!",
      colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

  else:
    await ctx.reply("That user isn't in no prefix!", mention_author=False)

  con.commit()

#ping
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
  rode = discord.Embed(
    description=f"My Latency is {round(client.latency*1000)} ms",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#uptime
@client.command(aliases=['up'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def uptime(ctx):
  current_time = datetime.datetime.now()
  uptime = current_time - start_time
  hours, remainder = divmod(int(uptime.total_seconds()), 3600)
  minutes, seconds = divmod(remainder, 60)
  days, hours = divmod(hours, 24)
  uptime_str = f"{days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s)"
  rode = discord.Embed(
    description=f"Uptime: {uptime_str}",
    colour=0x2b2d31,
  )
  rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#Ban
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ban(ctx, member: discord.Member, *, reason=None):
  if ctx.author.guild_permissions.ban_members:
    await member.ban(reason=reason)
    rode = discord.Embed(color=0x2b2d31, description=f"**{member.name}** has now been banned\nReason:**{reason}**")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to ban members", mention_author=False)

#unban
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
      if ctx.author.guild_permissions.ban_members:
        try:
           await ctx.guild.fetch_ban(user)
        except discord.NotFound:
            return await ctx.reply(f"That user is not banned.", mention_author=False)
        
        await ctx.guild.unban(user=user)
        rode = discord.Embed(color=0x2b2d31, description=f"Sucessfully Unbanned **{user.name}**")
        rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode, mention_author=False)
    

#hide
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def hide(ctx, channel: discord.TextChannel):
  if ctx.author.guild_permissions.manage_channels:
    await channel.set_permissions(ctx.guild.default_role, view_channel=False)
    rode = discord.Embed(color=0x2b2d31, description=f"**{channel.name}** has now been hidden")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to manage channels", mention_author=False)

#unhide
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def unhide(ctx, channel: discord.TextChannel):
  if ctx.author.guild_permissions.manage_channels:
    await channel.set_permissions(ctx.guild.default_role, view_channel=True)
    rode = discord.Embed(color=0x2b2d31, description=f"**{channel.name}** has now been unhidden")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to manage channels", mention_author=False)

#lock
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def lock(ctx, channel: discord.TextChannel):
  if ctx.author.guild_permissions.manage_channels:
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    rode = discord.Embed(color=0x2b2d31, description=f"**{channel.name}** has now been locked")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to manage channels", mention_author=False)

#unlock
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def unlock(ctx, channel: discord.TextChannel):
  if ctx.author.guild_permissions.manage_channels:
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    rode = discord.Embed(color=0x2b2d31, description=f"**{channel.name}** has now been unlocked")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to manage channels", mention_author=False)

#kick
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def kick(ctx, member: discord.Member, *, reason=None):
  if ctx.author.guild_permissions.kick_members:
    await member.kick(reason=reason)
    rode = discord.Embed(color=0x2b2d31, description=f"Sucessfully Kicked **{member.name}**\nReason:**{reason}**")
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  else:
    await ctx.reply("You don't have permission to kick members", mention_author=False)

#invite
@client.command(aliases=['inv'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def invite(ctx):
    rode = discord.Embed(
    description= "Will Come Soon",
    color= 0x2b2d31
  )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)
  

#support
@client.command(aliases=['sup'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def support(ctx):
    rode = discord.Embed(
    description= "Will Come Soon",
    color= 0x2b2d31
  )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

#gay
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def gay(ctx, *, user: discord.Member = None):
  if user is None:
    user = ctx.author
  gay_percent = random.randint(0, 100)
  response = f"The gay percentage of {user.display_name} is {gay_percent}%"
  rode = discord.Embed(color=0x2b2d31)
  rode.set_author(name=response, icon_url=ctx.author.display_avatar.url)
  await ctx.reply(embed=rode, mention_author=False)

#kiss
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def kiss(ctx, member: discord.Member):
  kiss_gifs = [
    "https://e1.pxfuel.com/desktop-wallpaper/805/403/desktop-wallpaper-hot-kiss-anime-2011-wall-blogspot-iphone-computer-kiss-anime-thumbnail.jpg"
  ]
  kiss_gif = random.choice(kiss_gifs)
  response = f"{ctx.author.display_name} Smoothly kissed {member.display_name}!"

  rode = discord.Embed(color=0x2b2d31)
  rode.set_author(name=response, icon_url=ctx.author.display_avatar.url)
  rode.set_image(url=kiss_gif)
  await ctx.reply(embed=rode, mention_author=False)

#say
@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def say(ctx, *, message):
  rode = discord.Embed(
    color=0x2b2d31,
    description=f"**{ctx.author.name} said:** {message}"
  )
  await ctx.reply(embed=rode, mention_author=False)

#stats
@client.command(aliases=['bi'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def stats(ctx):
    mem = psutil.virtual_memory()
    total_mem = round(mem.total / (1024 ** 3), 1)
    used_mem = round(mem.used / (1024 ** 3), 1)
    available_mem = round(mem.available / (1024 ** 3), 1)
    dis = psutil.disk_usage('/')
    total_dis = round(dis.total / (1024 ** 3), 1)
    used_dis = round(dis.used / (1024 ** 3), 1)
    avail_dis = round(dis.free / (1024 ** 3), 1)
    per_dis = dis.percent
    total_users = sum([i.member_count for i in client.guilds])
    rode = discord.Embed(color=0x2b2d31)
    rode.add_field(name="Statics",value=f"Cores: {psutil.cpu_count()}\nCPU Usage: {psutil.cpu_percent()}%\nMemory: {used_mem}/{total_mem} GB\nMemory Available: {available_mem} GB\nDisk: {used_dis}/{total_dis} GB ({per_dis} %)\nDisk Available: {avail_dis} GB",inline=False)
    rode.add_field(name="Cache Info",value=f"Guilds: {len(client.guilds)}\nUsers: {total_users}\nLatency: {round(client.latency * 1000)} MS\nChannels: {len(list(client.get_all_channels()))}",inline=False)
    rode.set_author(name=client.user.name + "Stats", icon_url=client.user.display_avatar.url)
    rode.set_footer(text=f"Request By {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

#Ignore add/remove
@client.command(aliases=['aig'])
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(administrator=True)
async def ignoreadd(ctx, channel: discord.TextChannel):
    ignored_channels.append(channel.id)
    save_ignored_channels()
    rode = discord.Embed(
    description=f"I will now ignore messages in {channel.mention}",
    color=0x2b2d31)
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

@client.command(aliases=['rig'])
@commands.cooldown(1, 5, commands.BucketType.user)
@commands.has_permissions(administrator=True)
async def ignoreremove(ctx, channel: discord.TextChannel):
    ignored_channels.remove(channel.id)
    save_ignored_channels()
    rode = discord.Embed(
    description=f"I will no longer ignore messages in {channel.mention}",
    color=0x2b2d31)
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

#bl add/remove
@client.command(aliases=['abl'])
@commands.is_owner()
async def bladd(ctx, user: discord.User):
    blacklist.append(user.id)
    save_blacklist()
    rode = discord.Embed(
    description=f"I will now ignore messages from {user.mention}",
    color=0x2b2d31)
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

@client.command(aliases=['rbl'])
@commands.is_owner()
async def blremove(ctx, user: discord.User):
    blacklist.remove(user.id)
    save_blacklist()
    rode = discord.Embed(
    description=f"I will no longer ignore messages from {user.mention}",
    color=0x2b2d31)
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

#gleave
@client.command()
@commands.is_owner()
async def gleave(ctx, guild: discord.Guild):
    await guild.leave()

#ignore and bl event
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.author.id in blacklist:
        return

    if message.channel.id in ignored_channels:
        return
    
    if not message.author.bot:
        with open(afk_file, "r") as f:
            afk_data = json.load(f)

        for user_id, afk_message in afk_data.items():
            user = message.guild.get_member(int(user_id))
            if user and user in message.mentions:
                rode1 = discord.Embed(
                description=f"**{user.name}** is now AFK: {afk_message}",
                colour=0x2b2d31)
                rode1.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                await message.reply(embed=rode1, mention_author=False)
                break
        else:
            if str(message.author.id) in afk_data:
                del afk_data[str(message.author.id)]
                rode2 = discord.Embed(
                description=f"Welcome back, **{message.author.name}**! Your AFK status has been removed.",
                colour=0x2b2d31)
                rode2.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                await message.reply(embed=rode2, mention_author=False)

        with open(afk_file, "w") as f:
            json.dump(afk_data, f)
                

    if message.content == client.user.mention: 
        
      embed = discord.Embed(description=f"Hey {message.author.name},\nMy prefix here is `?` and I come with `36` commands\nI am the best music bot out there in the industry.")
      embed.set_footer(text="Made With Love By Sky.!", icon_url="https://images-ext-1.discordapp.net/external/rNzkDgsK97dy-_of1vUIxxtdS_cjzrjbc8csdwbxaxw/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1145325240705093683/9976356251d3915f198dd8439464a4e6.png?width=600&height=600")
      embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
      #button = discord.ui.Button(label="Rode", url="https://discord.com/api/oauth2/authorize?client_id=1145325240705093683&permissions=8&scope=bot%20applications.commandsn")
      embed.color = 0x2b2d31
     # view = discord.ui.View().add_item(button)
      await message.reply(embed=embed, mention_author=False)

    await client.process_commands(message)
    
    
#badges/pr
@client.command(aliases=['pr'])
async def profile(ctx):
    user_id = str(ctx.author.id)
  
    with open(badges_data_file, "r") as f:
        badges_data = json.load(f)

    if user_id in badges_data:
        user_badges = badges_data[user_id]
        badge_display = "\n".join([f"{predefined_badges[badge]}" for badge in user_badges])
        embed = discord.Embed(
        color=0x2b2d31,
        description=f"**Badges:\n{badge_display}**"
        )
        embed.set_footer(text="Made With Love By Sky.!", icon_url="https://images-ext-1.discordapp.net/external/rNzkDgsK97dy-_of1vUIxxtdS_cjzrjbc8csdwbxaxw/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/1145325240705093683/9976356251d3915f198dd8439464a4e6.png?width=600&height=600")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False)
    else:
        await ctx.reply(f"**{ctx.author.name}** has no badges.", mention_author=False)

#give/removebadge
@client.command(aliases=['gb'])
@commands.is_owner()
async def givebadge(ctx, member: discord.Member, badge_name: str):
    if badge_name not in predefined_badges:
        await ctx.reply("Invalid badge name. Choose from the predefined badges.", mention_author=False)
        return

    user_id = str(member.id)

    with open(badges_data_file, "r") as f:
        badges_data = json.load(f)

    if user_id not in badges_data:
        badges_data[user_id] = []

    if badge_name not in badges_data[user_id]:
        badges_data[user_id].append(badge_name)

        with open(badges_data_file, "w") as f:
            json.dump(badges_data, f)
        rode = discord.Embed(
        description=f"Gave the **{badge_name}** badge to **{member.name}**.",
        colour=0x2b2d31,
    )
        rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode, mention_author=False)
    else:
        rode2 = discord.Embed(
        description=f"**{member.name}** already has the **{badge_name}** badge.",
        colour=0x2b2d31,
    )
        rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode2, mention_author=False)

@client.command(aliases=['gab'])
@commands.is_owner()
async def giveallbadges(ctx, member: discord.Member):
    user_id = str(member.id)

    with open(badges_data_file, "r") as f:
        badges_data = json.load(f)

    if user_id not in badges_data:
        badges_data[user_id] = []
      
    for badge_name in predefined_badges:
        if badge_name not in badges_data[user_id]:
            badges_data[user_id].append(badge_name)

    with open(badges_data_file, "w") as f:
        json.dump(badges_data, f)
    rode = discord.Embed(
        description=f"Added all predefined badges to **{member.name}**.",
    colour=0x2b2d31,
    )
    rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
    await ctx.reply(embed=rode, mention_author=False)

@client.command(aliases=['rb'])
@commands.is_owner()
async def removebadge(ctx, member: discord.Member, badge_name: str):
    user_id = str(member.id)

    with open(badges_data_file, "r") as f:
        badges_data = json.load(f)

    if user_id in badges_data:
        user_badges = badges_data[user_id]

        if badge_name in user_badges:
            user_badges.remove(badge_name)

            with open(badges_data_file, "w") as f:
                json.dump(badges_data, f)
            rode = discord.Embed(
            description=f"Removed the **{badge_name}** badge from **{member.name}**.",
            colour=0x2b2d31,
    )
            rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode, mention_author=False)
        else:
            rode2 = discord.Embed(
            description=f"**{member.name}** does not have the **{badge_name}** badge.",
            colour=0x2b2d31,
    )
            rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode2, mention_author=False)
    else:
        await ctx.reply(f"**{member.name}** has no badges.", mention_author=False)

@client.command(aliases=['rab'])
@commands.is_owner()
async def removeallbadges(ctx, member: discord.Member):
    user_id = str(member.id)

    with open(badges_data_file, "r") as f:
        badges_data = json.load(f)

    if user_id in badges_data:
        badges_data[user_id] = []

        with open(badges_data_file, "w") as f:
            json.dump(badges_data, f)
        rode = discord.Embed(
        description=f"Removed all badges from **{member.name}**.",
        colour=0x2b2d31,
    )
        rode.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode, mention_author=False)
    else:
        await ctx.reply(f"**{member.name}** has no badges.", mention_author=False)

#move
@client.command()
async def move(ctx):
    if ctx.author.voice:
        destination_channel = ctx.author.voice.channel

        if ctx.voice_client:
            await ctx.voice_client.move_to(destination_channel)
            rode1 = discord.Embed(
            description=f"Sucessfully moved to {destination_channel.name}",
            colour=0x2b2d31)
            rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode1, mention_author=False)
        else:
            await ctx.reply("I'm not currently in a voice channel.", mention_author=False) 
    else:
        await ctx.reply("You need to be in a voice channel to use this command.", mention_author=False)   
        
#Dj role
DATABASE_FILE = 'dj_roles.json'
@client.command(aliases=['cdj'])
@commands.has_permissions(administrator=True)
async def djcreate(ctx):
        new_role = await ctx.guild.create_role(name='dj')
        
        with open(DATABASE_FILE, 'r') as file:
            data = json.load(file)
        
        data['roles'].append({
            'name': new_role.name,
            'id': new_role.id
        })
        
        with open(DATABASE_FILE, 'w') as file:
            json.dump(data, file, indent=4)
        rode1 = discord.Embed(
        description=f"Dj Role has been created and registered!",
        colour=0x2b2d31)
        rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode1, mention_author=False)
        
@client.command(aliases=['gdj'])
@commands.has_permissions(administrator=True)
async def giveDJ(ctx, member: discord.Member):
        with open(DATABASE_FILE, 'r') as file:
            data = json.load(file)
        
        for role_info in data['roles']:
            if role_info['name'] == "dj":
                dj_role = discord.utils.get(ctx.guild.roles, id=role_info['id'])
                if dj_role:
                    await member.add_roles(dj_role)
                    rode1 = discord.Embed(
                    description=f"{member.name} now has the DJ role!",
                    colour=0x2b2d31)
                    rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
                    await ctx.reply(embed=rode1, mention_author=False)
                else:
                    await ctx.reply("The DJ role is not available.", mention_author=False)
                return
        
        await ctx.reply("The DJ role has not been registered. Use `createdj` to create and register it.", mention_author=False)

@client.command(aliases=['rdj'])
@commands.has_permissions(administrator=True)
async def removeDJ(ctx, member: discord.Member):
        with open(DATABASE_FILE, 'r') as file:
            data = json.load(file)
        
        for role_info in data['roles']:
            if role_info['name'] == "dj":
                dj_role = discord.utils.get(ctx.guild.roles, id=role_info['id'])
                if dj_role:
                    await member.remove_roles(dj_role)
                    rode1 = discord.Embed(
                    description=f"{member.name} no longer has the DJ role!",
                    colour=0x2b2d31)
                    rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
                    await ctx.reply(embed=rode1, mention_author=False)
                else:
                    await ctx.reply("The DJ role is not available.", mention_author=False)
                return
        
        await ctx.reply("The DJ role has not been registered. Use `createdj` to create and register it.", mention_author=False)  
        
#afk        
@client.command()
async def afk(ctx, *, message=None):
    user = ctx.author
    afk_data = {}

    if message:
        afk_data[user.id] = message
        rode1 = discord.Embed(
        description=f"**{user.name}** is now AFK: {message}",
        colour=0x2b2d31)
        rode1.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=rode1, mention_author=False)
    else:
        with open(afk_file, "r") as f:
            afk_data = json.load(f)

        if user.id in afk_data:
            del afk_data[user.id]
            rode2 = discord.Embed(
            description=f"Welcome back, **{user.name}**! Your AFK status has been removed.",
            colour=0x2b2d31)
            rode2.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode2, mention_author=False)
        else:
            afk_data[user.id] = None
            rode69 = discord.Embed(
            description=f"**{user.name}** is now AFK",
            colour=0x2b2d31)
            rode69.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=rode69, mention_author=False)
            
    with open(afk_file, "w") as f:
        json.dump(afk_data, f)
        
      
        
#join/leave logs
#@client.event
#async def on_guild_join(guild :discord.Guild):
#    rode = discord.Embed(title="Joined A Guild", description=f"**ID:** {guild.id}\n**Name:** {guild.name}\n**MemberCount:** {len(guild.members)}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>", color=0x2b2d31)
#    channel = client.get_channel(1145347249472290878)
#    await channel.send(embed=rode)
    
#@client.event
#async def on_guild_remove(guild: discord.Guild):
#        rode = discord.Embed(title="Left A Guild", description=f"**ID:** {guild.id}\n**Name:** {guild.name}\n**MemberCount:** {len(guild.members)}\n**Created:** <t:{int(guild.created_at.timestamp())}:R>", color=0x2b2d31)   
#        channel = client.get_channel(1145347259328901140)
#        await channel.send(embed=rode)

#help removed
client.remove_command("help")

#help
@client.command(aliases=['h'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def help(ctx):
  rode = discord.Embed(
    description=
    f"Heyy {ctx.message.author.name} I am the best music bot out there.",
    colour=0x2b2d31)
  rode.add_field(name="Moderation Commands", value="`Ban`, `Hide`, `Kick`, `Lock`, `Unban`, `Unhide`, `Unlock`, `Afk`", inline=False)
  rode.add_field(name="Info Commands", value="`Help`, `Invite`, `Ping`, `Stats`, `Support`, `Uptime`, `Profile`", inline=False)
  rode.add_field(name="Fun Commands", value="`Say`, `Kiss`, `Gay`", inline=False)
  rode.add_field(name="Music Commands", value="`Play`, `Pause`, `Resume`, `Queue`, `Volume`, `Skip`, `Stop`, `Clearqueue`, `Remove`, `Move`", inline=False)
  rode.add_field(name="Setting Commands", value="`Ignoreadd`, `Ignoreremove`, `Createdj`, `Givedj`, `Removedj`")
  rode.add_field(name="Owner Commands", value="`Bladd`, `Blremove`, `Jsk`, `Gleave`, `Npadd`, `Npremove`, `Givebadge`, `Removebadge`", inline=False)
  rode.set_author(name=client.user.name + "HelpMenu",
                   icon_url=client.user.display_avatar.url)
  rode.set_footer(text=f"Request By {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
  view = discord.ui.View()
  #button = discord.ui.Button(label="Rode", url="https://discord.com/api/oauth2/authorize?client_id=1145325240705093683&permissions=8&scope=bot%20applications.commands")
  #view.add_item(button)
 
  await ctx.reply(embed=rode, mention_author=False)

#errors + cooldown
@client.event
async def on_command_error(ctx, error):
  error = getattr(error, 'original', error)

  if isinstance(error, commands.MissingRequiredArgument):
    help_embed = discord.Embed(
      description=
      f"You are missing a required argument for the command `{ctx.command}`.",
      color=0x2b2d31)
    help_embed.set_author(name=client.user.name + " Error",
                          icon_url=client.user.display_avatar.url)

    help_embed.timestamp = datetime.datetime.utcnow()
    return await ctx.reply(embed=help_embed, mention_author=False)

  if isinstance(error, commands.BotMissingPermissions):
    permissions = ', '.join(perm for perm in error.missing_permissions)
    error_embed = discord.Embed(
      description=f"The bot needs {permissions} to execute this command.",
      color=0x2b2d31)
    error_embed.timestamp = datetime.datetime.utcnow()
    error_embed.set_author(name=client.user.name + " Error",
                           icon_url=client.user.display_avatar.url)
    return await ctx.reply(embed=error_embed, mention_author=False)

  if isinstance(error, commands.CommandOnCooldown):
    bucket = commands.CooldownMapping.from_cooldown(1, 5,
                                                    commands.BucketType.user)
    retry_after = bucket.get_bucket(ctx.message).update_rate_limit()

    if retry_after:
      return

    cooldown_embed = discord.Embed(
      description=
      f"You're on cooldown. Try again in {round(error.retry_after, 2)} seconds.",
      color=0x2b2d31)
    cooldown_embed.set_author(name=client.user.name + " Error",
                              icon_url=client.user.display_avatar.url)
    cooldown_embed.timestamp = datetime.datetime.utcnow()
    return await ctx.reply(embed=cooldown_embed, mention_author=False)

  if isinstance(error, commands.UserNotFound):
    user_not_found_embed = discord.Embed(
      description="The specified user was not found.", color=0x2b2d31)
    user_not_found_embed.timestamp = datetime.datetime.utcnow()
    user_not_found_embed.set_author(name=client.user.name + " Error",
                                    icon_url=client.user.display_avatar.url)
    return await ctx.reply(embed=user_not_found_embed, mention_author=False)

  if isinstance(error, commands.MemberNotFound):
    member_not_found_embed = discord.Embed(
      description="The specified member was not found.", color=0x2b2d31)
    member_not_found_embed.timestamp = datetime.datetime.utcnow()
    member_not_found_embed.set_author(name=client.user.name + " Error",
                                      icon_url=client.user.display_avatar.url)
    return await ctx.reply(embed=member_not_found_embed, mention_author=False)

  if isinstance(error, commands.RoleNotFound):
    role = error.argument
    role_not_found_embed = discord.Embed(
      description=f"The role `{role}` was not found.", color=0x2b2d31)
    role_not_found_embed.timestamp = datetime.datetime.utcnow()
    role_not_found_embed.set_author(name=client.user.name + " Error",
                                    icon_url=client.user.display_avatar.url)
    return await ctx.reply(embed=role_not_found_embed, mention_author=False)

  if isinstance(error, commands.ChannelNotFound):
    channel = error.argument
    channel_not_found_embed = discord.Embed(
      description=f"The channel '{channel}' was not found.", color=0x2b2d31)
    channel_not_found_embed.timestamp = datetime.datetime.utcnow()
    channel_not_found_embed.set_author(name=client.user.name + " Error",
                                       icon_url=client.user.display_avatar.url)
    return await ctx.reply(embed=channel_not_found_embed, mention_author=False)

  if isinstance(error, commands.MaxConcurrencyReached):
    max_concurrency_embed = discord.Embed(description=f"{ctx.author} {error}",
                                          color=0x2b2d31)
    max_concurrency_embed.timestamp = datetime.datetime.utcnow()
    return await ctx.reply(embed=max_concurrency_embed, mention_author=False)

  if isinstance(error, commands.CheckAnyFailure):
    for err in error.errors:
      if isinstance(err, commands.MissingPermissions):
        permissions_embed = discord.Embed(
          description=
          f"You don't have enough permissions to run the command `{ctx.command.qualified_name}`",
          color=0x2b2d31)
        permissions_embed.timestamp = datetime.datetime.utcnow()
        permissions_embed.set_author(name=client.user.name + " Error",
                                     icon_url=client.user.display_avatar.url)
        return await ctx.reply(embed=permissions_embed, delete_after=5, mention_author=False)

  if isinstance(error, commands.CheckFailure):
    return



client.run("MTE0OTA0ODU4MTM0OTcxNjAxOA.GbhC4M.5eRKQ73At5m-G-dlOMJSllNPX8T4ElifAa5XiM")