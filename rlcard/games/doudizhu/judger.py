# -*- coding: utf-8 -*-
''' Implement Doudizhu Judger class
'''
import numpy as np

from rlcard.games.doudizhu.utils import CARD_TYPE
from rlcard.games.doudizhu.utils import cards2str, contains_cards


class DoudizhuJudger(object):
    ''' Determine what cards a player can play
    '''

    def __init__(self, players):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        all_cards_list = CARD_TYPE[1]
        self.playable_cards = [set() for _ in range(3)]
        self._recorded_removed_playable_cards = [[] for _ in range(3)]
        for player in players:
            player_id = player.player_id
            current_hand = cards2str(player.current_hand)
            for cards in all_cards_list:
                if contains_cards(current_hand, cards):
                    self.playable_cards[player_id].add(cards)

    def calc_playable_cards(self, player):
        ''' Recalculate all legal cards the player can play according to his
        current hand.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer
            init_flag (boolean): For the first time, set it True to accelerate
              the preocess.

        Returns:
            list: list of string of playable cards
        '''
        removed_playable_cards = []

        player_id = player.player_id
        current_hand = cards2str(player.current_hand)
        missed = None
        for single in player.singles:
            if single not in current_hand:
                missed = single
                break

        playable_cards = self.playable_cards[player_id].copy()

        if missed is not None:
            position = player.singles.find(missed)
            player.singles = player.singles[position+1:]
            for cards in playable_cards:
                if missed in cards or (not contains_cards(current_hand, cards)):
                    removed_playable_cards.append(cards)
                    self.playable_cards[player_id].remove(cards)
        else:
            for cards in playable_cards:
                if not contains_cards(current_hand, cards):
                    #del self.playable_cards[player_id][cards]
                    removed_playable_cards.append(cards)
                    self.playable_cards[player_id].remove(cards)
        self._recorded_removed_playable_cards[player_id].append(removed_playable_cards)
        return self.playable_cards[player_id]

    def restore_playable_cards(self, player_id):
        ''' restore playable_cards for judger for game.step_back().
            
        Args:
            player_id: The id of the player whose playable_cards need to be restored
        '''
        removed_playable_cards = self._recorded_removed_playable_cards[player_id].pop()
        self.playable_cards[player_id].update(removed_playable_cards)
            

    def get_playable_cards(self, player):
        ''' Provide all legal cards the player can play according to his
        current hand.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer
            init_flag (boolean): For the first time, set it True to accelerate
              the preocess.

        Returns:
            list: list of string of playable cards
        '''
        return self.playable_cards[player.player_id]


    @staticmethod
    def judge_game(players, player_id):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        player = players[player_id]
        if not player.current_hand:
            return True
        return False

    @staticmethod
    def judge_payoffs(landlord_id, winner_id):
        payoffs = np.array([0, 0, 0])
        if winner_id == landlord_id:
            payoffs[landlord_id] = 1
        else:
            for index, _ in enumerate(payoffs):
                if index != landlord_id:
                    payoffs[index] = 1
        return payoffs
