'''
Created on Sep 13, 2015

@author: Caracal
'''

import json
import urllib2
import time

class API_caller():
    #constants
    _api_key = '74ed8037-673b-4a7f-8742-bfd10a2ab39e'
    _ranked_queues = 'rankedQueues=RANKED_SOLO_5x5&'
    _url_base = 'https://na.api.pvp.net/api/lol/'
    _match_list_url = '/v2.2/matchlist/by-summoner/'
    _summoner_id_url_base = '/v1.4/summoner/by-name/'
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
    def __init__(self):

        '''
        Define all parameters for match retrieval API call
        '''

        self._api_key_string = 'api_key=' + self._api_key




    def retrieve_summoner_ids(self, region, summ_names):
        '''
        takes in comma separated list of summoner names, followed by region code
        returns dict of name:summid
        '''

        summ_names = summ_names.replace(' ','')
        summ_url = self._url_base + region + self._summoner_id_url_base + summ_names + '?' + self._api_key_string
        try:
            summs = json.load(urllib2.urlopen(summ_url))
        except urllib2.URLError, e:
            print 'Error code, failed to retrieve match list', e
            return
        summ_ids = {}

        #using .keys() because only 10 values, enumerate not working on dict for some reason
        for k in summs.keys():
            summ_ids[k] = summs[k]['id']
        if len(summs) != len(summ_names.split(',')):
            print 'Incomplete list of ids retrieved, check spelling of names'
        return summ_ids



    def retrieve_match_list(self, summ_id, region, conditionals):
        '''
        takes in comma summonerid, followed by region code
        conditionals not yet implemented
        returns dict
        '''
        conditionals += self._ranked_queues
        summ_id_str = str(summ_id)
        match_list_url =   self._url_base + region + self._match_list_url + summ_id_str + '?' + conditionals + self._api_key_string

        match_list = {}
        try:
            matches = json.load(urllib2.urlopen(match_list_url))
        except urllib2.URLError, e:
            print 'Error code, failed to retrieve match list', e
            return
        for match in matches['matches']:
            if match['lane']+match['role'] in self._role_dict:
                #Format matchid, matchTime, champion, role
                match_list['matchid'] = (match['timestamp'], match['champion'], self._role_dict[match['lane']+match['role']], match['lane']+match['role'])
            else:
                print match['lane']+match['role']+str(match['matchId'])
                match_list['matchid'] = (match['timestamp'], match['champion'], 'REKT', match['lane']+match['role'])

        return match_list


if __name__ == '__main__':
    apic = API_caller()
    match_list = apic.retrieve_summoner_ids('na', 'vaior swift, female champs only, lumiere ombre')
    print match_list
