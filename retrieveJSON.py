'''
Created on Sep 13, 2015

@author: Caracal
'''

import json
import urllib2


#constants
_api_key = '74ed8037-673b-4a7f-8742-bfd10a2ab39e'

_ranked_queues = 'rankedQueues=RANKED_SOLO_5x5&'
_role_dict = {'TOPSOLO' : 'TOP',
                'MIDSOLO' : 'MID',
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

'''
Define all parameters for match retrieval API call
'''
summ_id = '53809338'
summ_id2 = '49229950'
region = 'na'

_match_list_url_base = 'https://na.api.pvp.net/api/lol/'
_match_list_url_1 = '/v2.2/matchlist/by-summoner/'
_api_key_string = 'api_key=' + _api_key
conditionals = _ranked_queues

_match_list_url =   _match_list_url_base + region + _match_list_url_1 + summ_id2 + '?' + conditionals + _api_key_string


#yaml more readable, but json better performance

def retrieve_match_list():
    match_list = []
    print 'Attempting to call:',_match_list_url
    try:
        matches = json.load(urllib2.urlopen(_match_list_url))
    except urllib2.URLError, e:
        print 'Error code, failed to retrieve match list', e
    for match in matches['matches']:
        if match['lane']+match['role'] in _role_dict:
            #Format matchid, matchTime, champion, role
            match_list.append((match['matchId'], match['timestamp'], match['champion'], _role_dict[match['lane']+match['role']], match['lane']+match['role']))
        else:
            print match['lane']+match['role']+str(match['matchId'])
            match_list.append((match['matchId'], match['timestamp'], match['champion'], 'REKT', match['lane']+match['role']))

    return match_list


if __name__ == '__main__':
    print json.load(urllib2.urlopen(_match_list_url))
    match_list = retrieve_match_list()
    print len(match_list)
