import re

import discord
import asyncio
import random
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import help_commands

from discord.ext import commands


class misc_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sent_message = False

    @commands.is_owner()
    @commands.command(aliases=["del"])
    async def delete_messages(self, ctx, amount=1):
        async for message in ctx.channel.history(limit = int(amount)+1):
            await message.delete()

    @commands.command()
    async def repeat(self, ctx, *, words):
        await ctx.send(words)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        try:
            prefix = help_commands.get_prefix(message)
            if "prefix" in message.content and not message.content.startswith(
                    f"{prefix}prefix"):
                await message.channel.send(f"My prefix is \"{prefix}\"")
        except Exception as e:
            print("from on_message prefix func: error occured", e)

def setup(bot):
    bot.add_cog(misc_commands(bot))
