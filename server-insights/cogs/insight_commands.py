import asyncio
import math
import random

import matplotlib.pyplot as plt
import time
import csv
import discord
import os

import numpy as np
import pytz
from datetime import datetime, timedelta
from discord.ext import commands
import server_insights as si
import help_commands as hc
import matplotlib
import datetime as dt

async def archive_exists(ctx):
    if os.path.exists(f"server_archives/archive_{ctx.guild.id}.csv"):
        return True
    else:
        await ctx.send(f"To use this command, you must first archive the server by using the **{hc.get_prefix(ctx)}archive** command.")
        return False



class insight_commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def archive(self, ctx):
        await ctx.send("Archiving all messages. This could take a while, depending on the size of your server. "
                       "I will let you know when I've finished.")

        start_time = time.time()
        num_messages = 0

        try:
            all_messages = []
            channels = ctx.guild.text_channels
            for channel in channels:
                channel_messages = await channel.history(limit=None).flatten()
                channel_messages = [message for message in channel_messages if message.content != ""]
                all_messages.extend(channel_messages)
            with open(f"server_archives/archive_{ctx.guild.id}.csv", "w", newline="", encoding='utf-8', errors='ignore') as w:
                writer = csv.writer(w)
                writer.writerow(["user_name", "user_id", "display_name", "channel", "from_bot", "time_sent_UTC", "message"])
                for message in all_messages:
                    created_at = message.created_at
                    date = f"{created_at.year};{created_at.month};{created_at.day};{created_at.hour};{created_at.minute}"
                    writer.writerow([message.author.name, message.author.id, message.author.display_name, message.channel.name, message.author.bot, date, message.content.replace("\n", "\\n")])
                    num_messages += 1
        except Exception as e:
            ctx.send("There was an error archiving the server. I am sorry for the inconvenience (please contact ogen#3091).")
            raise e


        elapsed_time = round(time.time() - start_time)
        minutes = math.floor(elapsed_time / 60)
        seconds = math.floor(elapsed_time % 60)
        time_passed = f"{minutes} minutes and {seconds} seconds"

        await ctx.send(f"Finished archiving (took {time_passed} to archive {num_messages} messages).\n\n"
                       f"If you would like to download the archive as a csv file you can do the {hc.get_prefix(ctx)}getarchive command.\n\n"
                       f"Also, keep in mind that analyses will **not** take into account any messages "
                       f"from this point onwards (you will have to run this command again).")

    @commands.check(archive_exists)
    @commands.command(aliases=["givearchive"])
    async def getarchive(self, ctx):
        await ctx.send("Here is a file containing every message sent up until the last archive:"
                       , file=discord.File(f"server_archives/archive_{ctx.guild.id}.csv"))


    @commands.check(archive_exists)
    @commands.command(aliases=["br", "bd", "b"])
    async def breakdown(self, ctx, *, args=""):

        # checks for which type of analysis & graph to do
        analysis_type = "member"
        if "member" in args:
            args = args.replace("member", "")
        if "channel" in args:
            analysis_type = "channel"
            args = args.replace("channel", "")
        elif "findswear" in args:
            analysis_type = "findswear"
            args = args.replace("findswear", "")
        elif "emoji" in args:
            analysis_type = "emoji"
            args = args.replace("emoji", "")
        elif "find" in args:
            analysis_type = "find"
            args = args.replace("find", "")

        graph_type = "bar"
        if "bar" in args:
            args = args.replace("bar", "")
        if "text" in args:
            graph_type = "text"
            args = args.replace("text", "")
        elif "pie" in args:
            graph_type = "pie"
            args = args.replace("pie", "")

        all_time_weekly = None
        if "time" in args:
            analysis_type = "time"
            args = args.replace("time", "")
            if "day" in args:
                all_time_weekly = False
                args = args.replace("day", "")
            elif "week" in args and "weekly" not in args:
                all_time_weekly = True
                args = args.replace("week", "")

            graph_type = "all"
            if "all" in args:
                args = args.replace("all", "")
            elif "weekly" in args:
                graph_type = "weekly"
                args = args.replace("weekly", "")
            elif "daily" in args:
                graph_type = "daily"
                args = args.replace("daily", "")

        send = True
        if "user" in args:
            analysis_type = "user"
            args = args.replace("user", "")
            send = False

        include_bots = "False"
        if "include" in args:
            include_bots = "True"
            args = args.replace("include", "")

        args = args.strip()
        args = args.replace("`", " ")

        # read file
        all_messages = read_all_messages(ctx)

        amount_per = {}

        weekly_threshold = 140

        # over time setups
        graph_title = "Amount of Messages Sent Over Time"
        #days_since_first_message = 0
        if graph_type == "weekly":
            graph_title = "Average Amount of Messages Sent Per Day"
            amount_per = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
        elif graph_type == "daily":
            graph_title = "Average Amount of Messages Sent By Hour"
            for i in range(25):
                if i < 10:
                    amount_per[f"0{i}:00"] = 0
                else:
                    amount_per[f"{i}:00"] = 0
            #print(f"dict: {amount_per}")
        elif graph_type == "all":

            # get days since first message
            oldest_message_time = get_first_message_time(all_messages)
            utc = pytz.utc
            eastern = pytz.timezone('US/Eastern')
            utc_time = utc.localize(ctx.message.created_at)
            est_time = utc_time.astimezone(eastern)
            days_since_first_message = (est_time - oldest_message_time).days

            date_list = [est_time - dt.timedelta(days=x) for x in range(days_since_first_message)]
            date_list.reverse()

            if all_time_weekly is None:
                all_time_weekly = days_since_first_message < weekly_threshold

            if all_time_weekly:
                graph_title = "Amount of Messages Sent Per Week"
            else:
                graph_title = "Amount of Messages Sent Per Day"

            for date in date_list:
                if all_time_weekly:
                    amount_per[date.strftime("%B '%y%U")] = 0
                else:
                    amount_per[date.strftime("%b %d '%y")] = 0

        swears_list = get_swear_words()

        for message in all_messages:
            if message[4] == "True" and include_bots == "False":
                continue

            if analysis_type == "find":
                if args.lower() in message[-1].lower():
                    if message[0] not in amount_per:
                        amount_per[message[0]] = 1
                    else:
                        amount_per[message[0]] += 1
            elif analysis_type == "findswear":
                for swear in swears_list:
                    if f"{swear}" in message[-1].lower():
                        if message[0] not in amount_per:
                            amount_per[message[0]] = 1
                        else:
                            amount_per[message[0]] += 1
            # elif analysis_type == "findswear":
            #     if f"{swear}" in message[-1].lower():
            #         if message[0] not in amount_per:
            #             amount_per[message[0]] = 1
            #         else:
            #             amount_per[message[0]] += 1

            elif analysis_type == "user":
                # if message.
                if message[1] == args:
                    if message[3] not in amount_per:
                        amount_per[message[3]] = 1
                    else:
                        amount_per[message[3]] += 1

            else:
                if analysis_type == "channel":
                    looking_for = message[3]
                elif analysis_type == "time":
                    string_time = message[5].split(";")
                    message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
                    utc = pytz.utc
                    eastern = pytz.timezone('US/Eastern')
                    utc_time = utc.localize(message_time)
                    message_time = utc_time.astimezone(eastern)

                    if graph_type == "all":
                        if all_time_weekly:
                            looking_for = message_time.strftime("%B '%y%U")
                        else:
                            looking_for = message_time.strftime("%b %d '%y")

                    elif graph_type == "weekly":
                        looking_for = message_time.strftime("%a")
                    else:
                        # daily
                        looking_for = message_time.strftime("%H:00")
                        #print(f"looking for: {looking_for}")

                else:
                    # analysis type is message
                    looking_for = message[0]

                if looking_for not in amount_per:
                    amount_per[looking_for] = 1
                    #print(f"adding to {looking_for}")
                else:
                    amount_per[looking_for] += 1

        if analysis_type == "time":

            if graph_type == "all":
                keys = (list(amount_per.keys()))
                values = (list(amount_per.values()))
                if all_time_weekly:
                    keys = keys[:-1]
                    values = values[:-1]
                    tick_every_n = round(len(keys) / 4)
                else:
                    tick_every_n = round(len(keys) / 5)

                if len(keys) < 4:
                    await ctx.send("This server has not existed long enough to create that graph.")
                    return
                await line_graph(ctx, keys, values, graph_title, tick_every_n, all_time_weekly)
                return

            for key in amount_per:
                amount_per[key] /= len(amount_per)

            if graph_type == "weekly":
                await bar_graph(ctx, list(amount_per.keys()), list(amount_per.values()), graph_title, self.bot)
            else:
                # daily
                await line_graph(ctx, list(amount_per.keys()), list(amount_per.values()), graph_title, 3, False)
            return

        sorted_amounts = sorted(amount_per.items(), key=lambda n: n[1], reverse=True)

        # graph title
        graph_title = "Messages Per Member"
        if analysis_type == "channel":
            graph_title = "Messages Per Channel"
        elif analysis_type == "find":
            graph_title = f'# of times each member has said "{args}"'
        elif analysis_type == "findswear":
            graph_title = f'# of times each member has sworn'
        elif analysis_type == "user":
            graph_title = f"{(discord.utils.find(lambda m: m.id == int(args), ctx.guild.members)).name}'s Messages Per Channel"

        if graph_type == "text":
            await send_as_text(ctx, sorted_amounts, graph_title)
            return

        # sort data
        x = []
        y = []
        for i in range(len(sorted_amounts)):
            x.append(sorted_amounts[i][0])
            y.append(sorted_amounts[i][1])

        if len(y) == 0:
            if analysis_type == "find":
                await ctx.send(f'"{args}" has never been said.')
            else:
                pass
                # findswear
                # await ctx.send(f'No one has ever sworn.')
            return

        if graph_type == "pie":
            await pie_graph(ctx, x, y, graph_title, send=send)
        else:
            await bar_graph(ctx, x, y, graph_title, self.bot)

    @commands.check(archive_exists)
    @commands.command(aliases=["ov", "ovv"])
    async def overview(self, ctx, *, user: discord.User=None):

        if user is None:
            user = ctx.author

        await self.breakdown(ctx, args=f"user pie {user.id}")

        messages = [message for message in read_all_messages(ctx) if int(message[1]) == user.id]
        amount_sent = len(messages)

        if amount_sent == 0:
            await ctx.send(f"I could not find any messages sent by {user}. "
                     f"Either they have not sent any messages yet, or they changed their username since the last archive.")
            return

        oldest_message = messages[0]
        string_time = oldest_message[5].split(";")
        message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
        utc = pytz.utc
        eastern = pytz.timezone('US/Eastern')
        utc_time = utc.localize(message_time)
        oldest_time = utc_time.astimezone(eastern)

        swears = []
        swears_list = get_swear_words()

        for message in messages:

            # calculate time
            string_time = message[5].split(";")
            message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
            utc = pytz.utc
            eastern = pytz.timezone('US/Eastern')
            utc_time = utc.localize(message_time)
            eastern_time = utc_time.astimezone(eastern)
            if eastern_time < oldest_time:
                oldest_message = message
                oldest_time = eastern_time

            for swear in swears_list:
                if f"{swear}" in message[-1].lower():
                    swears.append(message)

        desc = f"**Messages Sent:** {amount_sent}\n\n"

        desc += f'**Oldest Message:**\n"{oldest_message[-1]}"\n(on {oldest_time.strftime("%A, %B %d, %Y, at %H:%M")})\n\n'

        swears_shown = 0
        amount_of_swears = len(swears)
        desc += f"Sworn **{amount_of_swears}** Times ({(amount_of_swears/amount_sent)*100:.2f}%). "
        if amount_of_swears > 0:
            desc += f"For Example:\n"
            while amount_of_swears > 0 and swears_shown < 3:
                index = random.randint(0, len(swears)) - 1
                swear_message = swears.pop(index)

                # message time
                string_time = swear_message[5].split(";")
                message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
                utc = pytz.utc
                eastern = pytz.timezone('US/Eastern')
                utc_time = utc.localize(message_time)
                swear_message_time = utc_time.astimezone(eastern)

                desc += '"' + swear_message[-1].replace("\\n", "\n") + '"' + f' (on {swear_message_time.strftime("%Y-%m-%d")})\n'
                amount_of_swears -= 1
                swears_shown += 1




        file = discord.File("graph.png")



        embed = discord.Embed(colour=discord.Colour.from_rgb(250, 250, 250), timestamp=ctx.message.created_at,
                              description=desc)
        embed.set_author(name=f'Overview of {user.display_name}', icon_url=user.avatar_url)
        embed.set_image(url="attachment://graph.png")
        #await ctx.send(embed=embed)
        await ctx.send(embed=embed, file=file)
        plt.clf()
        plt.subplots_adjust(left=0.125)


    @commands.check(archive_exists)
    @commands.command(aliases=["random", "rand", "r"])
    async def send_random_message(self, ctx, *, args=""):

        filters = {"swear": False, "channel": None, "user": None, "amount": 1}
        if "swear" in args:
            filters["swear"] = True
            args = args.replace("swear", "")
        if "in" in args:
            args = args.replace("in", "", 1)
            remaining_args = args.strip().split(" ")
            channel = None
            for arg in remaining_args:
                channel = discord.utils.find(lambda m: m.name.lower() == arg.lower(), ctx.guild.text_channels)
                if channel is not None:
                    args = args.replace(arg, "")
                    break
            if channel is None:
                await ctx.send(f'There has never been a message that fulfills that criteria. '
                               f'Is the channel name spelt correctly?')
                return
            else:
                filters["channel"] = channel.name
        if "by" in args or "from" in args:
            if "by" in args:
                args = args.replace("by", "", 1)
            if "from" in args:
                args = args.replace("from", "", 1)
            remaining_args = args.strip().split(" ")
            user = None
            for arg in remaining_args:
                arg = arg.replace("_", " ")
                user = discord.utils.find(lambda m: m.name.lower() == arg.lower() or m.display_name.lower() == arg.lower(), ctx.guild.members)
                if user is not None:
                    args = args.replace(arg, "")
                    break
            if user is None:
                await ctx.send(f'There has never been a message that fulfills that criteria. '
                               f'Are you sure there\'s a member who\'s user name or display name matches your message?')
                return
            else:
                filters["user"] = user.id
        if "amount" in args:
            args = args.replace("amount", "", 1)
            args = args.strip()
            try:
                amount = int(args)
                if amount < 1 or amount > 5:
                    raise
                filters["amount"] = amount
            except:
                await ctx.send(f'You have to enter a valid number after "amount" (cannot be less than 1 or greater than 5).')
                return




        all_messages = read_all_messages(ctx)

        if filters["channel"] is not None:
            all_messages = [message for message in all_messages if message[3].lower() == filters["channel"]]

        if filters["user"] is not None:
            all_messages = [message for message in all_messages if int(message[1]) == filters["user"]]

        if filters["swear"]:
            swears_list = get_swear_words()
            new_messages = []
            for message in all_messages:

                for swear in swears_list:
                    if f"{swear}" in message[-1].lower():
                        new_messages.append(message)
            all_messages = new_messages

        if len(all_messages) == 0:
            await ctx.send("There has never been a message that fulfills that criteria.")
            return

        str_to_send = ""

        for i in range(filters["amount"]):
            message = all_messages[random.randint(0, len(all_messages))]
            all_messages.remove(message)
            date = get_EST_time(message[5])

            str_to_send += f'"{message[-1]}"\n\n'
            str_to_send += f'- {message[0]}'

            if message[0] != message[2]:
                str_to_send += f'/{message[2]}'

            str_to_send += f' in the "{message[3]}" channel'
            str_to_send += f' on '
            str_to_send += f'{date.strftime("%A, %B %d, %Y, at %I:%M %p")}\n\n\n'

        await ctx.send(str_to_send)




def get_cutoff(graph_type, messages_sent, total_sent):
    if graph_type == "pie":
        cutoff = 0
        #cutoff = total_sent * 0.01
    else:
        if len(messages_sent) > 8:
            cutoff = messages_sent[8]
        else:
            cutoff = messages_sent[-1]
    return cutoff

async def bar_graph(ctx, x, y, title, bot):

    amount_left = len(y)

    graphs_to_send = math.ceil(len(y) / 12)

    if graphs_to_send > 3:
        message = await ctx.send(f"There are many data points in this graph, so I will have to split it up into {graphs_to_send} different graphs. "
                                 f"Is this ok? React to this message with ✅ within the next 10 seconds to confirm.")
        await message.add_reaction(emoji='✅')

        def check(_reaction, _user):
            return _user == ctx.author and str(_reaction.emoji) == '✅'
        try:
            _reaction, _user = await bot.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(
                "10 seconds is up. if you meant to react but ran out of time, you will have to do type the command again.")
            return

    max_bars_per_graph = math.ceil(len(y) / graphs_to_send)
    while amount_left > 0:
        if len(y) > max_bars_per_graph:
            amount = max_bars_per_graph
        else:
            amount = len(y)
        plt.title(title)
        plt.xticks(rotation=30, ha='right')
        plt.subplots_adjust(bottom=0.3)
        plt.bar(x[:amount], y[:amount])
        x = x[:1] + x[amount:]
        y = y[:1] + y[amount:]
        plt.savefig('graph.png')
        await ctx.send(file=discord.File('graph.png'))
        plt.clf()
        amount_left -= amount

async def pie_graph(ctx, names, y, title, send=True):
    ### old
    # amount = sum(y)
    # cutoff = amount * 0.03
    # #cutoff = 0
    # names = ["Other"]
    # percents = [0]
    # labels = []
    # for i in range(len(y)):
    #     if y[i] > cutoff:
    #         names.append(x[i])
    #         percents.append((y[i] / amount) * 100)
    #     else:
    #         percents[0] += (y[i] / amount) * 100
    # if percents[0] != 0:
    #     percents.append(percents.pop(0))
    #     names.append(names.pop(0))
    # else:
    #     percents.pop(0)
    #     names.pop(0)
    #labels = [f"{p:.1f}%" for p in percents]


    # getting labels and percents
    amount = sum(y)
    percents = []
    labels = []
    for number in  y:
        percent = (number / amount) * 100
        percents.append(percent)
        if percent > 4:
            labels.append(f"{percent:.1f}%")
        else:
            labels.append("")

    # plotting the graph
    plt.subplots_adjust(left=0.4)
    plt.pie(percents, labels=labels, labeldistance=1.05, startangle=90, radius=1.2)

    plt.title(title, y=1.1)
    plt.legend(names, loc='upper center', bbox_to_anchor=(-0.45, 1.2))
    plt.savefig('graph.png')
    if send:
        await ctx.send(file=discord.File('graph.png'))
        plt.clf()
        plt.subplots_adjust(left=0.125)

async def line_graph(ctx, x, y, title, tick_every_n, all_time):

    if all_time:
        x[0] = x[0][:-2]
        x[round(len(x)/2)-1] = x[round(len(x)/2)-1][:-2]
        x[-1] = x[-1][:-2]

    plt.title(title)
    #plt.xticks(rotation=30, ha='right')
    #plt.subplots_adjust(bottom=0.3)
    line_width = 1
    if len(x) > 100:
        line_width = 0.7

    plt.plot(x, y, linewidth=line_width)
    if all_time:
        plt.xticks([0, round(len(x)/2)-1, len(x)-1])

    else:
        plt.xticks(np.arange(0, len(x)-1, tick_every_n))
    # ax = plt.gca()
    # temp = ax.xaxis.get_ticklabels()
    # # temp = list(set(temp) - set(temp[::tick_every_n]))
    # for tick in temp:
    #     tick.label = "test"

    plt.savefig('graph.png')
    await ctx.send(file=discord.File('graph.png'))
    plt.clf()


async def send_as_text(ctx, sorted_amounts, title):
    message_to_send = f"{title}:\n"
    for person in sorted_amounts:
        username = person[0]
        message_to_send += f"    - {username}: {person[1]}\n"
    await ctx.send(message_to_send)

def read_all_messages(ctx):
    all_messages = []
    with open(f"server_archives/archive_{ctx.guild.id}.csv", encoding='utf-8', errors='ignore') as r:
        r.readline()
        reader = csv.reader(r)
        for line in reader:
            all_messages.append(line)
    return all_messages

def get_swear_words():
    with open("swear_words.txt") as r:
        swears = []
        for line in r:
            line = line.strip('\n')
            line = line.replace("_", " ")
            swears.append(line)
        return swears

def get_first_message_time(messages):
    oldest_message = messages[0]
    string_time = oldest_message[5].split(";")
    message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
    utc = pytz.utc
    eastern = pytz.timezone('US/Eastern')
    utc_time = utc.localize(message_time)
    oldest_time = utc_time.astimezone(eastern)
    for message in messages:
        # calculate time
        string_time = message[5].split(";")
        message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
        utc = pytz.utc
        eastern = pytz.timezone('US/Eastern')
        utc_time = utc.localize(message_time)
        eastern_time = utc_time.astimezone(eastern)
        if eastern_time < oldest_time:
            oldest_time = eastern_time
    return oldest_time


def get_EST_time(file_time):
    string_time = file_time.split(";")
    message_time = datetime(int(string_time[0]), int(string_time[1]), int(string_time[2]), int(string_time[3]), int(string_time[4]))
    utc = pytz.utc
    eastern = pytz.timezone('US/Eastern')
    utc_time = utc.localize(message_time)
    est_time = utc_time.astimezone(eastern)
    return est_time



def setup(bot):
    bot.add_cog(insight_commands(bot))