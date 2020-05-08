# api.py


class Player:
    """ Represents a player with the contents returned by the API. """

    def __init__(self, player_data):
        """ Set attributes. """
        self.steam = player_data['steam']
        self.discord = player_data['discord']
        self.discord_name = player_data['discord_name']
        self.id = player_data['id']
        self.is_banned = player_data['isBanned']
        self.score = player_data['score']
        self.kills = player_data['kills']
        self.deaths = player_data['deaths']
        self.assists = player_data['assists']
        self.suicides = player_data['suicides']
        self.tk = player_data['tk']
        self.shots = player_data['shots']
        self.hits = player_data['hits']
        self.headshots = player_data['headshots']
        self.connected = player_data['connected']
        self.rounds_tr = player_data['rounds_tr']
        self.rounds_ct = player_data['rounds_ct']
        self.lastconnect = player_data['lastconnect']
        self.knife = player_data['knife']
        self.glock = player_data['glock']
        self.hkp2000 = player_data['hkp2000']
        self.usp_silencer = player_data['usp_silencer']
        self.p250 = player_data['p250']
        self.deagle = player_data['deagle']
        self.elite = player_data['elite']
        self.fiveseven = player_data['fiveseven']
        self.tec9 = player_data['tec9']
        self.cz75a = player_data['cz75a']
        self.revolver = player_data['revolver']
        self.nova = player_data['nova']
        self.xm1014 = player_data['xm1014']
        self.mag7 = player_data['mag7']
        self.sawedoff = player_data['sawedoff']
        self.bizon = player_data['bizon']
        self.mac10 = player_data['mac10']
        self.mp9 = player_data['mp9']
        self.mp7 = player_data['mp7']
        self.ump45 = player_data['ump45']
        self.p90 = player_data['p90']
        self.galilar = player_data['galilar']
        self.ak47 = player_data['ak47']
        self.scar20 = player_data['scar20']
        self.famas = player_data['famas']
        self.m4a1 = player_data['m4a1']
        self.m4a1_silencer = player_data['m4a1_silencer']
        self.aug = player_data['aug']
        self.ssg08 = player_data['ssg08']
        self.sg556 = player_data['sg556']
        self.awp = player_data['awp']
        self.g3sg1 = player_data['g3sg1']
        self.m249 = player_data['m249']
        self.negev = player_data['negev']
        self.hegrenade = player_data['hegrenade']
        self.flashbang = player_data['flashbang']
        self.smokegrenade = player_data['smokegrenade']
        self.inferno = player_data['inferno']
        self.decoy = player_data['decoy']
        self.taser = player_data['taser']
        self.mp5sd = player_data['mp5sd']
        self.breachcharge = player_data['breachcharge']
        self.head = player_data['head']
        self.chest = player_data['chest']
        self.stomach = player_data['stomach']
        self.left_arm = player_data['left_arm']
        self.right_arm = player_data['right_arm']
        self.left_leg = player_data['left_leg']
        self.right_leg = player_data['right_leg']
        self.c4_planted = player_data['c4_planted']
        self.c4_exploded = player_data['c4_exploded']
        self.c4_defused = player_data['c4_defused']
        self.ct_win = player_data['ct_win']
        self.tr_win = player_data['tr_win']
        self.hostages_rescued = player_data['hostages_rescued']
        self.vip_killed = player_data['vip_killed']
        self.vip_escaped = player_data['vip_escaped']
        self.vip_played = player_data['vip_played']
        self.mvp = player_data['mvp']
        self.damage = player_data['damage']
        self.match_win = player_data['match_win']
        self.match_draw = player_data['match_draw']
        self.match_lose = player_data['match_lose']
        self.first_blood = player_data['first_blood']
        self.no_scope = player_data['no_scope']
        self.no_scope_dis = player_data['no_scope_dis']
        self.in_match = player_data['inMatch']

        # Convert player_data values to int
        for attr, val in self.__dict__.items():
            if attr != 'discord_name' and attr != 'in_match':  # These attributes are already the correct type
                setattr(self, attr, 0 if val is None else int(val))  # Convert to ints with None being 0

    @property
    def steam_profile(self):
        """ Generate the player's Steam profile link. """
        return f'https://steamcommunity.com/profiles/{self.steam}'

    @property
    def matches_played(self):
        """ Calculate and return matches played. """
        return self.match_win + self.match_draw + self.match_lose

    @property
    def win_percent(self):
        """ Calculate and return win percentage. """
        try:
            return self.match_win / (self.match_win + self.match_lose)
        except ZeroDivisionError:
            return 0

    @property
    def kd_ratio(self):
        """ Calculate and return K/D ratio. """
        try:
            return self.kills / self.deaths
        except ZeroDivisionError:
            return 0

    @property
    def adr(self):
        """ Calculate and return average damage per round. """
        try:
            return self.damage / (self.rounds_tr + self.rounds_ct)
        except ZeroDivisionError:
            return 0

    @property
    def hs_percent(self):
        """ Calculate and return headshot kill percentage. """
        try:
            return float(self.headshots / self.kills)
        except ZeroDivisionError:
            return 0

    @property
    def first_blood_rate(self):
        try:
            return self.first_blood / (self.rounds_tr + self.rounds_ct)
        except ZeroDivisionError:
            return 0


class MatchServer:
    """ Represents a match server with the contents returned by the API. """

    def __init__(self, json):
        """ Set attributes. """
        self.id = json['match_id']
        self.ip = json['ip']
        self.port = json['port']

    @property
    def connect_url(self):
        """ Format URL to connect to server. """
        return f'steam://connect/{self.ip}:{self.port}'

    @property
    def connect_command(self):
        """ Format console command to connect to server. """
        return f'connect {self.ip}:{self.port}'


class ApiHelper:
    """ Class to contain API request wrapper functions. """

    def __init__(self, session, base_url, api_key):
        """ Set attributes. """
        self.session = session
        self.session.raise_for_status = True
        self.base_url = base_url
        self.api_key = api_key

    @property
    def headers(self):
        """ Default authentication header the API needs. """
        return {'authentication': self.api_key}

    async def generate_link_url(self, user):
        """ Get custom URL from API for user to link accounts. """
        url = f'{self.base_url}/discord/generate/{user.id}'

        async with self.session.get(url=url, headers=self.headers) as resp:
            resp_json = await resp.json()

            if resp_json.get('discord') and resp_json.get('code'):
                return f'{self.base_url}/discord/{resp_json["discord"]}/{resp_json["code"]}'

    async def is_linked(self, user):
        """ Check if a user has their account linked with the API. """
        url = f'{self.base_url}/discord/check/{user.id}'

        async with self.session.get(url=url, headers=self.headers) as resp:
            resp_json = await resp.json()

            if resp_json.get('linked'):
                return resp_json['linked']
            else:
                return False

    async def update_discord_name(self, user):
        """ Update a users API name to their current Discord display name. """
        url = f'{self.base_url}/discord/update/{user.id}'
        data = {'discord_name': user.display_name}

        async with self.session.post(url=url, headers=self.headers, data=data) as resp:
            return resp.status == 200

    async def get_player(self, user):
        """ Get player data from the API. """
        url = f'{self.base_url}/player/discord/{user.id}'

        async with self.session.get(url=url, headers=self.headers) as resp:
            return Player(await resp.json())

    async def get_players(self, users):
        """ Get multiple players' data from the API. """
        url = f'{self.base_url}/players/discord'
        discord_ids = {"discordIds": [user.id for user in users]}

        async with self.session.post(url=url, headers=self.headers, json=discord_ids) as resp:
            players = await resp.json()
            return [Player(player_data) for player_data in players]

    async def ban_player(self, user):
        """ Ban a player from the service. """
        url = f'{self.base_url}/player/discord/{user.id}/ban'

        async with self.session.get(url=url, headers=self.headers) as resp:
            return resp  # Placeholder for return value, if any

    async def unban_player(self, user):
        """ Unban a player from the service. """
        url = f'{self.base_url}/player/discord/{user.id}/unban'

        async with self.session.get(url=url, headers=self.headers) as resp:
            return resp  # Placeholder for return value, if any

    async def start_match(self, team_one, team_two):
        """ Get a match server from the API. """
        url = f'{self.base_url}/match/start'
        teams = {
            'team_one': {user.id: user.display_name for user in team_one},
            'team_two': {user.id: user.display_name for user in team_two}
        }

        async with self.session.post(url=url, headers=self.headers, json=teams) as resp:
            return MatchServer(await resp.json())
