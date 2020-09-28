# leaguebot.py

import discord
from discord.ext import commands
import logging
import sys
import traceback

from . import cogs


class LeagueBot(commands.AutoShardedBot):
    """ Sub-classed AutoShardedBot modified to fit the needs of the application. """

    def __init__(self, discord_token, api_base_url, api_key, db_connect_url, emoji_dict, donate_url=None):
        """ Set attributes and configure bot. """
        # Call parent init
        super().__init__(command_prefix=('q!', 'Q!'), case_insensitive=True)

        # Set argument attributes
        self.discord_token = discord_token
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.db_connect_url = db_connect_url
        self.emoji_dict = emoji_dict
        self.donate_url = donate_url

        # Set constants
        self.description = 'An easy to use, fully automated system to set up and play CS:GO pickup games'
        self.color = 0x000000
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="noobs type q!help")  # TODO: Make help command string dynamic
        self.logger = logging.getLogger('csgoleague.bot')

        # Create session for API
        self.api_helper = cogs.utils.ApiHelper(self.loop, self.api_base_url, self.api_key)

        # Create DB helper to use connection pool
        self.db_helper = cogs.utils.DBHelper(self.db_connect_url)

        # Initialize set of errors to ignore
        self.ignore_error_types = set()

        # Add check to not respond to DM'd commands
        self.add_check(lambda ctx: ctx.guild is not None)
        self.ignore_error_types.add(commands.errors.CheckFailure)

        # Trigger typing before every command
        self.before_invoke(commands.Context.trigger_typing)

        # Add cogs
        self.add_cog(cogs.LoggingCog(self))
        self.add_cog(cogs.HelpCog(self))
        self.add_cog(cogs.AuthCog(self))
        self.add_cog(cogs.QueueCog(self))
        self.add_cog(cogs.MatchCog(self))
        self.add_cog(cogs.StatsCog(self))

        if self.donate_url:
            self.add_cog(cogs.DonateCog(self))

    async def get_context(self, message, *, cls=None):
        """ Override parent method to use CustomContext """
        return await super().get_context(message, cls=cls or cogs.utils.LeagueBotContext)

    def get_users(self, user_ids):
        """"""
        return [self.get_user(uid) for uid in user_ids]

    def embed_template(self, **kwargs):
        """ Implement the bot's default-style embed. """
        kwargs['color'] = self.color
        return discord.Embed(**kwargs)

    @commands.Cog.listener()
    async def on_ready(self):
        """ Synchronize the guilds the bot is in with the guilds table. """
        await self.db_helper.sync_guilds(*(guild.id for guild in self.guilds))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """ Insert the newly added guild to the guilds table. """
        await self.db_helper.insert_guilds(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """ Delete the recently removed guild from the guilds table. """
        await self.db_helper.delete_guilds(guild.id)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """ Send help message when a mis-entered command is received. """
        if type(error) not in self.ignore_error_types:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def run(self):
        """ Override parent run to automatically include Discord token. """
        super().run(self.discord_token)

    async def close(self):
        """ Override parent close to close the API session also. """
        await super().close()
        await self.api_helper.close()
        await self.db_helper.close()
