# teamdraft.py

import discord
from discord.ext import commands
import random

CAPTAINS = 'high score'


class PickError(ValueError):
    """ Raised when a team draft pick is invalid for some reason. """

    def __init__(self, message):
        """ Set message parameter. """
        self.message = message


class TeamDraftMenu(discord.Message):
    """ Message containing the components for a team draft. """

    def __init__(self, message, bot, users):
        """ Copy constructor from a message and specific team draft args. """
        # Copy all attributes from message object
        for attr_name in message.__slots__:
            try:
                attr_val = getattr(message, attr_name)
            except AttributeError:
                continue

            setattr(self, attr_name, attr_val)

        # Add custom attributes
        self.bot = bot
        self.users = users
        emoji_numbers = [u'\u0031\u20E3',
                         u'\u0032\u20E3',
                         u'\u0033\u20E3',
                         u'\u0034\u20E3',
                         u'\u0035\u20E3',
                         u'\u0036\u20E3',
                         u'\u0037\u20E3',
                         u'\u0038\u20E3',
                         u'\u0039\u20E3',
                         u'\U0001F51F']
        self.pick_emojis = dict(zip(emoji_numbers, users))
        self.users_left = None
        self.teams = None

    def _picker_embed(self, title):
        """ Generate the menu embed based on the current status of the team draft. """
        embed = self.bot.embed_template(title=title)
        embed.set_footer(text='React to any of the numbers below to pick the corresponding user')

        for team in self.teams:
            team_name = '__Team__' if len(team) == 0 else f'__Team {team[0].display_name}__'

            if len(team) == 0:
                team_players = '_Empty_'
            else:
                team_players = '\n'.join(p.display_name for p in team)

            embed.add_field(name=team_name, value=team_players)

        users_left_str = ''

        for emoji, user in self.pick_emojis.items():
            if not any(user in team for team in self.teams):
                users_left_str += f'{emoji}  {user.display_name}\n'
            else:
                users_left_str += f':heavy_multiplication_x:  ~~{user.display_name}~~\n'

        embed.insert_field_at(1, name='__Players Left__', value=users_left_str)
        return embed

    def _pick_player(self, picker, pickee):
        """ Process a team captain's player pick. """
        if any(team == [] for team in self.teams) and picker in self.users:
            picking_team = self.teams[self.teams.index([])]  # Get the first empty team
            self.users_left.remove(picker)
            picking_team.append(picker)
        elif picker == self.teams[0][0]:
            picking_team = self.teams[0]
        elif picker == self.teams[1][0]:
            picking_team = self.teams[1]
        elif picker in self.users:
            raise PickError(f'Picker {picker.mention} is not a team captain')
        else:
            raise PickError(f'Picker {picker.mention} is not a user in the team draft')

        if len(picking_team) > len(self.users) // 2:  # Team is full
            raise PickError(f'Team {picker.mention} is full')

        if not picker == pickee:
            self.users_left.remove(pickee)
            picking_team.append(pickee)

    async def _update_menu(self, title):
        """ Update the message to reflect the current status of the team draft. """
        await self.edit(embed=self._picker_embed(title))

        for emoji, user in self.pick_emojis.items():
            if user not in self.users_left:
                await self.clear_reaction(emoji)

    async def _process_pick(self, reaction, user):
        """ Handler function for player pick reactions. """
        # Check that reaction is on this message and user is in the team draft
        if reaction.message.id != self.id or user not in self.users:
            return

        # Check that picked player is in the player pool
        pick = self.pick_emojis.get(str(reaction.emoji), None)

        if pick is None or pick not in self.users_left:
            return

        # Attempt to pick the player for the team
        try:
            self._pick_player(user, pick)
        except PickError as e:  # Player not picked
            title = e.message
        else:  # Player picked
            title = f'**Team {user.display_name}** picked {pick.display_name}'

        if len(self.users_left) == 1:
            fat_kid_team = self.teams[0] if len(self.teams[0]) <= len(self.teams[1]) else self.teams[1]
            fat_kid_team.append(self.users_left.pop(0))
            title = 'Teams are set!'

        await self._update_menu(title)

    async def draft(self):
        """ Start the team draft and return the teams after it's finished. """
        # Initialize draft
        self.users_left = self.users.copy()  # Copy users to edit players remaining in the player pool
        self.teams = [[], []]

        if CAPTAINS == 'high score':
            players = await self.bot.api_helper.get_players(self.users_left)
            players.sort(reverse=True, key=lambda x: x.score)

            for team in self.teams:
                captain = self.bot.get_user(players.pop(0).discord)
                self.users_left.remove(captain)
                team.append(captain)
        elif CAPTAINS == 'random':
            rand_users = self.users_left.copy()  # Create new list to preserve original order
            random.shuffle(rand_users)

            for team in self.teams:
                captain = rand_users.pop()
                self.users_left.remote(captain)
                team.append(captain)

        await self.edit(embed=self._picker_embed('Team draft has begun!'))

        for emoji in self.pick_emojis:
            await self.add_reaction(emoji)

        # Add listener handlers and wait until there are no users left to pick
        self.bot.add_listener(self._process_pick, name='on_reaction_add')
        await self.bot.wait_for('reaction_add', check=lambda r, u: self.users_left == [], timeout=600.0)
        self.bot.remove_listener(self._process_pick, name='on_reaction_add')
        return self.teams


class TeamDraftCog(commands.Cog):
    """ Handles the player drafter command. """

    def __init__(self, bot):
        """ Set attributes and initialize empty draft teams. """
        self.bot = bot
        self.guild_player_pool = {}  # Players participating in the draft for each guild
        self.guild_teams = {}  # Teams for each guild
        self.guild_msgs = {}  # Last team draft embed message sent for each guild

    @commands.Cog.listener()
    async def on_ready(self):
        """ Initialize an empty list for each giuld the bot is in. """
        for guild in self.bot.guilds:
            self.guild_player_pool[guild] = []
            self.guild_teams[guild] = [[], []]

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """ Initialize an empty list for guilds that are added. """
        self.guild_player_pool[guild] = []
        self.guild_teams[guild] = [[], []]

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """ Remove queue list when a guild is removed. """
        self.guild_player_pool.pop(guild, None)
        self.guild_teams.pop(guild, None)
        self.guild_msgs.pop(guild, None)

    async def draft_teams(self, message, users):
        """ Create a TeamDraftMenu from an existing message and run the draft. """
        menu = TeamDraftMenu(message, self.bot, users)
        teams = await menu.draft()
        return teams[0], teams[1]

    # @commands.command(brief='Start (or restart) a player draft from the last popped queue')  # Omit command for now
    # async def tdraft(self, ctx):
    #     """ Start a player draft by sending a player draft embed panel. """
    #     queue_cog = self.bot.get_cog('QueueCog')

    #     if not queue_cog:
    #         return

    #     queue = queue_cog.guild_queues.get(ctx.guild)

    #     if len(queue.active) < queue.capacity:
    #         embed_title = f'Cannot start player draft until the queue is full ({len(queue.active)}/{queue.capacity})'
    #         embed = self.bot.embed_template(title=embed_title)
    #         await ctx.send(embed=embed)
    #         return

    #     teams = await self.draft_teams(ctx, queue.active)

    #     if not teams:
    #         return

    #     # FINISH HERE
