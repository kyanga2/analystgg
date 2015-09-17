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

def pullStats(match): 
    stats_out = [{'id':x} for x in xrange(1,11)]

    #initialize counter variables for calculating stats
    cs_min_counter = [0,0,0,0,0,0,0,0,0,0]
    r_t1_tower_kills = 0
    r_t2_tower_kills = 0
    r_i_tower_kills = 0
    b_t1_tower_kills = 0
    ward_time = [[0,0,0]]



    #iterate through all frames within the timeline, one minute at a time.
    #no important data in first frame
    for i in xrange(1,len(match['timeline']['frames'])):

        #iterate through events for minute ending in i

        for event in match['timeline']['frames'][i]['events']:
            #list of event

            pass

        for pId, pFrame in match['timeline']['frames'][i]['participantFrames'].iteritems():
            pNum = int(pId)-1 #for internal indexing
            ftmz = '' #first ten minute zero (for nice formattting)
            cs_at = pFrame['minionsKilled']
            if i<10: ftmz = '0'
            stats_out[pNum]['csmin'+ftmz+str(i)] =cs_at - cs_min_counter[pNum]
            cs_min_counter[pNum] = cs_at            

    return stats_out



def survey_stats(match, event_types):
    #survey frequency of events
    for i in xrange(1,len(match['timeline']['frames'])):
        #iterate through events for minute ending in i

        for event in match['timeline']['frames'][i]['events']:
            etype = event['eventType']
            if etype in event_types:
                event_types[etype] += 1
            else:
                event_types[etype] = 1  
     





if __name__ == '__main__':
    apic = API_caller()
    summ_list = apic.get_summoner_ids('na', 'vaior swift, female champs only, lumiere ombre')
    match_list = apic.get_match_list('na', summ_list['femalechampsonly'], '')
    counter = 0
    event_types = {}
    time.sleep(5)
    for i in xrange(273):
        survey_stats(apic.get_match('na',match_list.keys()[i], True), event_types)
        counter += 1
        time.sleep(1)
        if counter == 9:
            counter = 0
            time.sleep(3)
            print 'sleepin', i


