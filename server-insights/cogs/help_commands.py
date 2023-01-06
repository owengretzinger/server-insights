import asyncio
import json
import discord
from discord.ext import commands


def get_prefix(message):
    with open("prefixes.json", "r") as r:
        prefixes = json.load(r)

    try:
        if str(message.guild.id) in prefixes:
            return prefixes[str(message.guild.id)]
        else:
            return "!"
    except:
        return "!"

class help_commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="help")
    async def help(self, ctx):
        prefix = get_prefix(ctx)



        # desc = ""
        #
        # desc += f"**{prefix}prefix <new prefix>**\nChanges the bot's prefix to <new prefix>"
        #
        # desc += f"**{prefix}archive**\nArchives every message ever sent in the server so that I can perform analyses. " \
        #         f"You must do this in order to perform any of the other commands.\n\n"
        #
        # desc += f'**{prefix}breakdown <category> <type> <looking for> <include bots>**\nReturns a breakdown of messages sent by users through a graph.\n' \
        #         f'**<category>** is what type of breakdown you want, and can consist of "member", "channel", or "find":' \
        #         f'\n--- "member" gives an analysis based on how many messages each member has sent' \
        #         f'\n--- "channel" gives an analysis based on how many messages have been sent in each channel' \
        #         f'\n--- "find" allows you to see how many times each member has said a certain word/phrase (not case sensitive)' \
        #         f'\nIf you do not specify, the default is "member".\n' \
        #         f'**<type>** is the type of graph, and can consist of "bar", "pie", or "text".\nIf you do not specify, the default is "bar".\n' \
        #         f'**<looking for>** is only used with the "find" type, and consists of any letters/words/phrases/etc.\n' \
        #         f'**<include bots>** says whether you would like to include bots in the analysis. If you would, put "include", ' \
        #         f'otherwise the default does not include bots.\n' \
        #         f'**Tip:** You can also call this command by typing {prefix}b, {prefix}br, or {prefix}bd. ' \
        #         f'In addition, the order of <category> <type> <looking_for> and <include_bots> does not matter.\n' \
        #         f'**Example:** "!b text find sorry" would show you who the most aplogetic people in your server are, ' \
        #         f'by listing how many times each person has said "sorry". Try it out!\n\n'
        #
        # desc += f"**{prefix}getarchive**\nSends a csv file containing every message ever sent (user_name, user_number, display_name, channel, from_bot, message_contents).\n"
        #
        # embed = discord.Embed(colour=discord.Colour.from_rgb(250, 250, 250), timestamp=ctx.message.created_at,
        #                       description=desc)
        # embed.set_author(name='Help', icon_url=ctx.author.avatar_url)
        # await ctx.send(embed=embed)
        embed = discord.Embed(colour=discord.Colour.from_rgb(250, 250, 250), timestamp=ctx.message.created_at,
                              description="help")
        embed.set_author(name='Help', icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await breakdown_help(ctx, message)



async def edit_embed(ctx, message_to_edit, header, content):
    embed = discord.Embed(colour=discord.Colour.from_rgb(250, 250, 250), timestamp=ctx.message.created_at, description=content)
    embed.set_author(name=header, icon_url=ctx.author.avatar_url)
    await message_to_edit.edit(embed=embed)


async def archive_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**description**\n"
    desc += f""

    await edit_embed(ctx, message, "Other Commands", desc)


async def breakdown_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**This command is the main feature of the bot, and offers many different ways to analyze your server (there are *technically* 28 combinations).**\n\n"

    desc += f'**Usage:**\n{prefix}breakdown <analysis type> <graph type> <include bots>\n\n\n'

    desc += '**<analysis type>** is what type of breakdown you want, and can consist of "member", "channel", "find", "time", or "findswear" (default "member").\n\n'
    desc += '"member" gives an analysis based on how many messages each member has sent\n\n'
    desc += '"channel" gives an analysis based on how many messages have been sent in each channel\n\n'
    desc += '"find" allows you to see how many times each member has said a certain word/phrase (not case sensitive). ' \
            'This analysis also obviously requires you to specify what word/phrase to look for (see examples).\n\n'
    desc += '"time" gives analyses of messages over time, and is a somewhat special command with separate arguments. ' \
            'See farther down this help section to see how to use it.\n\n'
    desc += '"findswear" gives analyses of how many time each member has sworn.\n\n\n'

    desc += '**<graph type>** is the type of graph, and can consist of "bar", "pie", or "text" (default "bar").\n\n'
    desc += '"bar" shows data as a bar graph. If there are many data points, I may split up data across multiple graphs, and will ask you for confirmation ' \
            'before sending them if I have to send more than 3 graphs.\n\n'
    desc += '"pie" shows data as a pie chart/graph. If there are many data points, the categories with less than a few percent will not be labelled ' \
            '(also be warned that with many data points, the legend may be too large to entirely fit on the graph).\n\n'
    desc += '"text" shows data as text. This is the least visual, but it shows exact values and works just as well with many data points.\n\n\n'

    desc += '**<include bots>** decides whether to include bots in the analysis. For most purposes you should not worry about this, ' \
            'but if you do want to include bots, just write "include".\n\n\n'

    # desc += '**over time analysis** has 4 different methods. This may be confusing, so see the examples as well.\n\n'
    # desc += '"time all day" shows a line graph, with the x axis being every single **day** since the server was created, ' \
    #         'and the y axis being how many messages have been sent on each day.'
    # desc += '"time all week" shows a line graph, with the x axis being every **week** since the server was created, ' \
    #         'and the y axis being how many messages have been sent on each day.'
    # desc += '"time daily" shows a line graph of on average how many messages are sent at each hour in the day.'
    # desc += '"time weekly" shows a bar graph of on average how many messages are sent on each day of the week.'
    #
    # desc += '**Tips:** '
    # desc += ''
    #
    # desc += '**Examples:** '
    # desc += ''

    await edit_embed(ctx, message, f"Server Breakdown Command", desc)


async def overview_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**description**\n"

    desc += f'Usage:\n{prefix}commandname <args>'

    desc += '**argexplanation:** '
    desc += ''

    desc += '**Tips:** '
    desc += ''

    desc += '**Examples:** '
    desc += ''

    await edit_embed(ctx, message, "User Overview Command", desc)


async def random_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**description**\n"

    desc += f'Usage:\n{prefix}commandname <args>'

    desc += '**argexplanation:** '
    desc += ''

    desc += '**Tips:** '
    desc += ''

    desc += '**Examples:** '
    desc += ''

    await edit_embed(ctx, message, "Get Random Message Command", desc)


async def misc_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**description**\n"
    desc += f""

    await edit_embed(ctx, message, "Other Commands", desc)


async def secret_help(ctx, message):
    prefix = get_prefix(ctx)
    desc = "**description**\n"
    desc += f""

    await edit_embed(ctx, message, "Super Secret Commands :flushed:", desc)


def setup(bot):
    bot.add_cog(help_commands(bot))