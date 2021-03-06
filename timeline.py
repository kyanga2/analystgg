'''
Created on Oct 1, 2015

Timeline class and functions to build time-series objects from RIOT api match data
for modular event definition

@author: Kevin Yang
'''

from apiCaller import API_caller
import time
import sys
import json

'''
Each match json contains the following fields we care about:

match_id - unique id for the match
match_creation = not really needed since we have the match timestamp, should be identical
participants = game info about all 10 match_participants
timeline = big timeline of events within the match
participantIdentities = maps participantId to the summoner data, includes IMPORTANT matchHistoryURL

Timeline is broken into frames, each of which encompasses a minute of the game.

Each frame contains:    timestamp (beginning of frame), 
                        participantFrames (dict) snapshot of all 10 players
                        events (dict) list of events occurring within the frame 


Event Handling types:
each EVENT has an optional: assistingParticipantIds field for other participants (list type)

Skill:  SKILL_LEVEL_UP:  level up skill event, by participant + skillslot
            LEVEL_UP_TYPE: EVOLVE for viktor/khazix/??syndra??, NORMAL for everything else

Item:   ITEM_PURCHASE - buy
        ITEM_SOLD - sell
        ITEM_UNDO - undo buy or sell (item_before indicates what item was, item_after...)
        ITEM_DESTROYED - item used (potions)

Ward:   WARD_PLACED - timestamp, type, creatorID
        WARD_KILL - killerID, timetamp, type

Champ kill:   
        assistingParticipantIds (list)
        killerId
        position (x,y on the map)

ELITE_MONSTER_KILL:
        monsterType:  Baron, dragon
        killerId

BUILDING_KILL:
        assistingParticipantIds
        buildingType - tower, inhib
        killerID
        laneType - BOT, MID, TOP
        towerType - OUTER, INNER, BASE, NEXUS, UNDEFINED (azir)


EVENT PRIORITY:
    ITEM_PURCHASED
    ITEM_DESTROYED - matches with WARD_PLACED
    SKILL_LEVEL_UP
    WARD_PLACED*
    CHAMPION_KILL*
    WARD_KILL*
    BUILDING_KILL*
    ITEM_SOLD
    ITEM_UNDO
    ELITE_MONSTER_KILL*

'''

_role_dict = {'TOPSOLO' : 'TOP',
                'MIDSOLO' : 'MID',
                'MIDDLESOLO': 'MID',
                'NONEJUNGLE': 'JUNGLE',
                'JUNGLENONE': 'JUNGLE',
                'BOTTOMNONE': 'JUNGLE',
                'BOTTOMDUO_SUPPORT': 'SUPPORT',
                'BOTTOMDUO': 'SUPPORT',
                'MIDDUO_SUPPORT': 'SUPPORT',
                'MIDDLEDUO_SUPPORT': 'SUPPORT',
                'TOPDUO_SUPPORT': 'SUPPORT',
                'BOTTOMDUO_CARRY': 'ADC',
                'MIDDUO_CARRY': 'ADC',
                'MIDDLEDUO_CARRY': 'ADC',
                'TOPDUO_CARRY': 'ADC',
                'BOTTOMSOLO': 'TROLL', #odd cases being dropped due to roaming support
                'MIDDUO': 'TROLL',
                'MIDDLEDUO': 'TROLL',
                'TOPDUO': 'TROLL'}

_level_thresholds = {1: 0,
                     2: 280,
                     3: 660,
                     4: 1140,
                     5: 1720,
                     6: 2400,
                     7: 3180,
                     8: 4060,
                     9: 5040,
                     10: 6120,
                     11: 7300,
                     12: 8580,
                     13: 9960,
                     14: 11440,
                     15: 13020,
                     16: 14700,
                     17: 16480,
                     18: 18360}

_state_fields = ['jungleMinionsKilled', 
                 'level', 
                 'minionsKilled', 
                 'totalGold', 
                 'xp']

_state_field_cont = [True,
                     False,
                     True,
                     True,
                     True]

class states_cont(object):
    '''
    data structure housing time-sensitive state information on actors

    Constructed using a series of discrete snapshots, containing both discrete and
    continuous fields.

    Intended usage: return the state of the system at any time within the
    time spanned by the dataset
    '''

    def __init__(self, series_id, fields=None, field_cont=None):
        '''
        Initializes a new states object, tied to a series_id.
        fields is a list of features we wish to maintain for each actor's states
        field_cont_type is a list of booleans indicating whether each field is continuous or discrete
             True: continuous, False: discrete
        '''

        self._series_id = series_id
        self._fields = fields
        self._field_cont = field_cont

        self._timestamps = []
        self._data = []

    #consider testing df vs 2-list performance

    
    def load_df(self, df, df_timestamp_col=0):
        '''
        loads in time series data from a Pandas dataframe format
        '''

        for row in df:
            pass

    def add_state_seq(self, timestamp, data_dict):
        '''
        Timestamps on participant_frames are at the minute
        Timestamps on events are in milliseconds
        Used to build the states using sequential snapshots in time order
        '''
        self._timestamps.append(timestamp)
        self._data.append(dict(zip(self._fields, [data_dict[item] for item in self._fields])))

    def pull_state(self, timestamp):
        '''
        Retrieves a dictionary the state at the time indicated in timestamp.
        Returns the most recent value for discrete fields.
        Returns extrapolated value for continuous fields.
        '''
        timestamp = float(timestamp)
        i_t = 0
        if timestamp >= self._timestamps[-1]:
            return self._data[-1]

        while self._timestamps[i_t+1] <= timestamp:
            i_t += 1

        #i_t = next(idx for idx,value in enumerate(self._timestamps) if value > timestamp)

        out_d = {}
        for k, v in enumerate(self._fields):
            if self._field_cont[k]:
                print v, i_t
                out_d[v] = float(self._data[i_t][v]) * (self._timestamps[i_t+1]  - timestamp)  \
                                        /(self._timestamps[i_t+1]-self._timestamps[i_t]) \
                        + float(self._data[i_t+1][v]) * (timestamp-self._timestamps[i_t])  \
                                        /(self._timestamps[i_t+1]-self._timestamps[i_t])
                print (timestamp-self._timestamps[i_t])
                print (self._timestamps[i_t+1] - self._timestamps[i_t]) 
                                        #/(self._timestamps[i_t+1]-self._timestamps[i_t])   
            else:
                out_d[v] = self._data[i_t][v]

        return out_d


class timeline(object):

    _m_id = -1
    _event_types = []
    _timestamps = []
    _data = []

    def __init__(self, m_id, event_types):
        self._m_id = m_id
        self._event_types = event_types
        self._timestamps = []
        self._data = []

    def add_event(self, event_type, event_data):
        pass




	
def start_env():
    sys.stdout.write('starting \n')
    sys.stdout.flush()
    with open('matches500.txt', 'r') as f:
		stuff = f.read()
		j_data = json.loads(stuff)
    match = []
    match_list_keys = sorted(j_data.keys(), reverse=True)
    i_c = 0
    for key in match_list_keys:
    	match.append(j_data[key])
        sys.stdout.write('\r%d imported, latest %d' % (i_c+1, int(key)))
        sys.stdout.flush()
        i_c += 1
    sys.stdout.write('\rdone\n imported %d matches' % i_c)
    sys.stdout.flush()

    return match


# start_time = timeit.default_timer()
# for i in xrange(100):
#     pull_stats(match[i])
# elapsed = timeit.default_timer() - start_time
# # print elapsed
# for i in xrange(500):
#     if not data[i][10]:
#         print i, [item['role'] for item in data[i][:10]], match_list_sorted[i]

# with open('matches500.txt', 'r') as infile:
#     stuff = infile.read()
#     data1 = json.loads(stuff)