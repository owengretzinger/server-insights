import csv

import matplotlib.pyplot as plt
import time
import json
import discord
import asyncio
import os

import numpy as np
from discord.ext import commands


intents = discord.Intents.default()
intents.members = True
intents.guilds = True

#allowed_mentions = discord.AllowedMentions(everyone=False, users=False, roles=False)

async def get_prefix(_bot, message):
    if not message.guild:
        return commands.when_mentioned_or("!")(_bot, message)

    with open("prefixes.json", "r") as r:
        prefixes = json.load(r)

    if str(message.guild.id) not in prefixes:
        return commands.when_mentioned_or("!")(_bot, message)

    new_prefix = prefixes[str(message.guild.id)]
    return commands.when_mentioned_or(new_prefix)(_bot, message)

bot = commands.Bot(command_prefix=get_prefix, intents=intents, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))
bot.remove_command('help')


@bot.event
async def on_ready():
    print("bot is ready")
    await bot.change_presence(activity=discord.Game('analyzing servers 📊'))

@bot.event
async def on_guild_join(guild):
    channel = discord.utils.get(guild.channels, name='general')
    if channel is None:
        channel = discord.utils.get(guild.channels, name='bot-commands')
    if channel is None:
        channel = guild.channels[0]
    try:
        await channel.send('Thank you for adding me to your server. My default prefix is **"!"** (which you can change if you wish). '
                           'To get started, you should enter the **"!help"** command, as well as the **!archive** command.\n\n'
                           'If there are any issues, do not hesitate to contact _.')
    except Exception as e:
        print("Could not find a channel to send on_guild_join message to.")
        raise e


# async def read_all_messages(guild):
#     messages = []
#     channels = guild.text_channels
#     for channel in channels:
#         channel_messages = await channel.history(limit=None).flatten()
#         messages.extend(channel_messages)
#     return messages


# @bot.command()
# async def amount(ctx, user: discord.User):
#     start_time = time.time()
#     await ctx.send("searching through messages, check back in a minute...")
#
#     user_messages = []
#     all_messages = await read_all_messages(ctx.guild)
#     for message in all_messages:
#         if message.author.id == user.id:
#             user_messages.append(message)
#     messages_sent = len(user_messages)
#
#     elapsed_time = round(time.time() - start_time)
#     messages_per_sec = round(len(all_messages) / elapsed_time)
#
#     await ctx.send(f"{user} has sent {messages_sent} message (took {elapsed_time} seconds at {messages_per_sec} msgs/s)")
#
#     with open("lookup_times.csv", "a", newline="") as a:
#         messages_per_sec = round(len(all_messages) / elapsed_time)
#         writer = csv.writer(a)
#         writer.writerow([len(all_messages), elapsed_time, messages_per_sec])


@bot.command()
async def prefix(ctx, *, new_prefix):
    with open("prefixes.json", "r") as r:
        prefixes = json.load(r)

    prefixes[str(ctx.guild.id)] = new_prefix
    await ctx.send(f'new prefix is "{new_prefix}"')

    with open("prefixes.json", "w") as w:
        json.dump(prefixes, w, indent=4)


for cog in os.listdir("cogs"):
    if cog.endswith(".py") and not cog.startswith("_"):
        try:
            cog = f'cogs.{cog.replace(".py", "")}'
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} cannot be loaded:")
            raise e


# @bot.command()
# async def graph(ctx):
#     fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
#
#     wedges, texts = ax.pie(percents, startangle=-40)
#
#     bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
#     kw = dict(arrowprops=dict(arrowstyle="-"),
#               bbox=bbox_props, zorder=0, va="center")
#
#     for i, p in enumerate(wedges):
#         ang = (p.theta2 - p.theta1) / 2. + p.theta1
#         y = np.sin(np.deg2rad(ang))
#         x = np.cos(np.deg2rad(ang))
#         horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
#         connectionstyle = "angle,angleA=0,angleB={}".format(ang)
#         kw["arrowprops"].update({"connectionstyle": connectionstyle})
#         ax.annotate(names[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
#                     horizontalalignment=horizontalalignment, **kw)
#
#     ax.set_title(title)
#
#     plt.savefig('graph.png')
#     if send:
#         await ctx.send(file=discord.File('graph.png'))
#         plt.clf()
#         plt.subplots_adjust(left=0.125)







bot.run("token")