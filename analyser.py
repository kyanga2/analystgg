'''
Created on Sep 14, 2015

Analyzer class containing methods that intake a match object and output
varius statistics about the 10 players within the match

@author: Kevin Yang
'''

from apiCaller import API_caller
import time

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
                'TOPDUO_SUPPORT': 'SUPPORT',
                'BOTTOMDUO_CARRY': 'ADC',
                'MIDDUO_CARRY': 'ADC',
                'TOPDUO_CARRY': 'ADC',
                'BOTTOMSOLO': 'TROLL',
                'MIDDUO': 'TROLL',
                'TOPDUO': 'TROLL'}

def pull_stats(match): 
    stats_out = [{'id':x} for x in xrange(1,11)]

    #initialize counter variables for calculating stats
    '''
    Cs/min by phase of game
        laning phase (0-1st tower)
        early-mid game (until a team loses 3 towers)
        mid game (until a team loses 6 towers)
        late game (6 or more towers downed on a team)

    solo kills in lane
    solo kills in game
    laning phase solo deaths
    laning phase deaths to jungler
    sight ward-minutes
    vision wards-placed
    wards killed
    lane advantage flag


    '''
    game_phase = 0
    cs_min_counter = [0]*10
    r_tower_kills = 0
    b_tower_kills = 0
    solo_kills_lane = [0]*10
    solo_kills_game = [0]*10
    solo_deaths_lane = [0]*10
    gank_deaths_lane = [0]*10
    deaths_picked_off = [0]*10  #killed but no friendly dies in 5 seconds, enemy in 20 seconds
    ward_minutes = [0]*10
    lane_advantage = [0]*10
    jg_invade_red = False
    jg_invade_blue = False
    invade_offense = [0]*10
    invade_defense = [0]*10
    invade_deaths = [0]*10
    invade_kills = [0]*10

    '''
    Initialize all 10 participant roles
    '''

    for i in xrange(0,10):
        stats_out[i]['role'] = _role_dict[match['participants'][i]['timeline']['lane']+match['participants'][i]['timeline']['role']]



    #iterate through all frames within the timeline, one minute at a time.
    #no dynamic data in 0 frame, occasionally no events occur during 2 frame

    '''
    Check for invades which occur during frames 1 and 2
    100 = blue team, 200 = red team
    x+y < 13500 = blue side
    x+y > 16500 = red side
    inbetween = river

    '''
    print 'trying'
    for i in xrange(1,3):
        print i
        for event in match['timeline']['frames'][i]['events']:
            print event['eventType']
            if event['eventType'] == u'CHAMPION_KILL':
                v_id = event['victimId']-1
                invade_deaths[v_id] += 1
                invade_kills[event['killerId']-1] += 1
                x_coord = event['position']['x']
                y_coord = event['position']['y']
                print "kill found", v_id+1, x_coord, y_coord
                if x_coord + y_coord  < 14500:
                    #blue side invaded
                    if v_id <= 4:
                        invade_defense[v_id] -= 1
                        invade_offense[event['killerId']-1] += 1
                        if 'assistingParticipantIds' in event:
                            for champ in event['assistingParticipantIds']:
                                print champ, v_id +1
                                invade_offense[champ] += 1
                    else:
                        invade_offense[v_id] -= 1
                        invade_defense[event['killerId']-1] += 1
                        if 'assistingParticipantIds' in event:
                            for champ in event['assistingParticipantIds']:
                                print champ, v_id +1
                                invade_defense[champ] += 1

                else:
                    print "red side kill"
                    #red side invaded, river brawls credited to red side
                    if v_id <= 4:
                        invade_offense[v_id] -= 1
                        invade_defense[event['killerId']-1] += 1
                        if 'assistingParticipantIds' in event:
                            for champ in event['assistingParticipantIds']:
                                print champ, v_id +1
                                invade_defense[champ] += 1
                    else:
                        invade_defense[v_id] -= 1
                        invade_offense[event['killerId']-1] += 1
                        if 'assistingParticipantIds' in event:
                            for champ in event['assistingParticipantIds']:
                                print champ, v_id +1
                                invade_offense[champ] += 1
                    print invade_defense
                    print invade_offense


    for i in xrange(3,len(match['timeline']['frames'])):

        #iterate through events for minute ending in i

        for event in match['timeline']['frames'][i]['events']:
            #list of event

            pass

        for pId, pFrame in match['timeline']['frames'][i]['participantFrames'].iteritems():
            pNum = int(pId)-1 #for internal indexing
            ftmz = '' #first ten minute zero (for nice formattting)
            cs_at = pFrame['minionsKilled']+pFrame['jungleMinionsKilled']
            if i<10: ftmz = '0'
            stats_out[pNum]['csmin'+ftmz+str(i)] =cs_at - cs_min_counter[pNum]
            cs_min_counter[pNum] = cs_at            



    for i in xrange(10):
        stats_out[i]['invade_offense'] = invade_offense[i]
        stats_out[i]['invade_defense'] = invade_defense[i]
        stats_out[i]['invade_kills'] = invade_kills[i]
        stats_out[i]['invade_deaths'] = invade_deaths[i]


    return stats_out



def survey_stats(match, event_types):
    #survey frequency of events
    for i in xrange(1,len(match['timeline']['frames'])):
        #iterate through events for minute ending in i
        try:
            for event in match['timeline']['frames'][i]['events']:
                etype = event['eventType']
                if etype in event_types:
                    event_types[etype] += 1
                else:
                    event_types[etype] = 1
        except KeyError:
            print KeyError, "frame", i, "from match", match['matchId']


def run_time(matches):
    for i in xrange(len(matches)):
        pull_stats(matches[i])


def start_kernel():
    apic = API_caller()
    summ_list = apic.get_summoner_ids('na', 'vaior swift, female champs only, lumiere ombre')
    match_list = apic.get_match_list('na', summ_list['vaiorswift'], '')
    counter = 0
    event_types = {}
    time.sleep(11)
    match = []
    match_list_sorted = sorted(match_list.keys(), reverse=True)
    for i in xrange(10):
        try:
            match.append(apic.get_match('na',match_list_sorted[i], True)) #catches 404s
            counter +=1
            if counter == 10:
                counter = 0
                time.sleep(12)
        except KeyError:
            print KeyError, "match", match_list.keys()[i]
