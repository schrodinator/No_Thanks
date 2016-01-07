#!/usr/bin/python
import sys
import random
from random import randint

class Deck(object):

    def __init__(self, num = 33, offset = 3):
        if num < 1:
            sys.exit("cannot initialize Deck with less than 1 card!")
        self.num = num
        self.offset = offset
        self.cards = []
        for i in range(num):
        # in the official game, cards are numbered from 3 to 35
            self.cards.append(i + offset)
        self.shuffle()
        self.discard(9)

    def shuffle(self):
    # change to shuffle in-place by swapping random pairs of cards?
        b = []
        for i in range(self.num):
            j = random.choice(self.cards)
            self.cards.remove(j)
            b.append(j)
        self.cards = b

    def discard(self, begone = 1):
        for i in range(begone):
            self.cards.pop(0)
            self.num -= 1

    def draw(self):
        if self.num > 0:
            self.num -= 1
            card = self.cards.pop(0)
            return card
        else:
            return -1


class Player(object):

    def __init__(self, pos, card_threshold = 9, token_threshold = 0, eff_val_threshold = 3):
        # position in play order (starting from 0)
        self.pos = pos
        self.tokens = 11
        self.cards = []
        self.score = 0
        self.eff_val = 0
        # max value of card to take without passing when player has 0 cards
        self.card_threshold = card_threshold
        self.token_threshold = token_threshold
        self.eff_val_threshold = eff_val_threshold

    def play_token(self):
        if self.tokens > 0:
            self.tokens -= 1
        else:
            sys.exit("Played an imaginary token!")

    def take_card(self, card):
        self.cards.append(card)
        self.cards.sort()

    def get_score(self):
        cards = list(self.cards)
        tot = 0
        if len(cards) == 0:
            self.score = 0
        else:
            low = cards.pop(0)
            prev = low
            while len(cards) > 0:
                current = cards.pop(0)
                if current > prev + 1:
                    tot += low
                    low = current
                prev = current
            tot += low
            self.score = tot - self.tokens


class Table(object):

    def __init__(self, players=[], num_cards=33, offset=3, verbose=1):
        self.players = []
        self.num_players = 3
        self.verbosity = verbose
        self.whose_turn = 0
        self.pot = 0
        self.deck = Deck(num_cards, offset)
        for pos in range(3):
            self.add_player(pos)
            print "Player", pos+1, \
                  "has card_threshold:", self.players[pos].card_threshold, \
                  "and token_threshold:",self.players[pos].token_threshold, \
                  "and eff_val_threshold:",self.players[pos].eff_val_threshold
        if self.verbosity == 1:
            print "\nInitial deck:", self.deck.cards
        self.card_up = self.deck.draw()
        if self.verbosity == 1:
            print "Card up:", self.card_up

    def get_player_positions(self):
        positions = []
        if len(self.players) == 0:
            return positions
        try:
            for player in self.players:
                positions.append(player.pos)
            return positions.sort()
        except:
            sys.exit("Invalid player positions!")

    def add_player(self, pos):
        # Add a player with random attributes
        min_card = self.deck.offset
        max_card = min_card + self.deck.num - 1
        card_threshold = randint(min_card, max_card)
        # do not allow a token_threshold of 11: player will take all the cards
        token_threshold = randint(0, 10)
        eff_val_threshold = 3
        self.players.append(Player(pos, card_threshold, token_threshold, eff_val_threshold))

    def player_passes(self):
        player = self.players[self.whose_turn]
        player.play_token()
        if self.verbosity == 1:
            print "Player", self.whose_turn + 1, player.cards, "plays token, has", player.tokens, "remaining"
        self.pot += 1
        self.whose_turn = (self.whose_turn + 1) % self.num_players
        self.play()

    def player_takes_card(self):
        player = self.players[self.whose_turn]
        if self.verbosity == 1:
            print "Player", self.whose_turn + 1, player.cards, "takes card:", self.card_up
        player.take_card(self.card_up)
        player.tokens += self.pot
        self.pot = 0
        if self.deck.num > 0:
            self.card_up = self.deck.draw()
            if self.verbosity == 1:
                print "Card up:", self.card_up
            self.play()
        else:
            if self.verbosity == 1:
                print "Game Over\n"
            self.score()

    def get_effective_value(self, player):
        if self.card_up + 1 in player.cards:
            if self.card_up -1 in player.cards:
                # Bridging card - connects two cards/runs in the player's hand.
                # Would lower player's score by the value of the higher run.
                effective_value = -(self.card_up + 1)
            else:
                # If taken, card_up would become the lowest card in a run.
                # Would lower player's score by 1 point.
                effective_value = -1
        elif self.card_up - 1 in player.cards:
            # If taken, card_up would go at the end of a run.
            # Doesn't change player's score.
            effective_value = 0
        elif self.card_up +2 in player.cards:
            # card_up is 1 card away from being connected in a run
            other_player_cards = []
            for other_player in self.players:
                if other_player != player:
                    other_player_cards += other_player.cards
            if self.card_up + 1 in other_player_cards:
                # the bridging card has already been taken:
                # no chance of completing the run
                effective_value = self.card_up
            else:
                # effective value depends on probability of completing the run
                prob = float(self.deck.num) / (float(self.deck.num) + 9.0)
                # calculate expectation value
                effective_value = -2.0*prob + self.card_up*(1.0 - prob)
                print " ==", effective_value - self.pot
        else:
            effective_value = self.card_up
        effective_value -= self.pot
        player.eff_val = effective_value

    def milking_potential(self):
        player = self.players[self.whose_turn]
        thresh = 3
        vals = []
        for other_player in self.players:
            if other_player != player:
                if other_player.tokens == 0:
                    return 0
                vals.append(other_player.eff_val)
        if vals[0] > thresh and vals[1] > thresh:
            print " (milking)"
            return 1
        else:
            return 0

    def player_logic(self):
        player = self.players[self.whose_turn]
        if len(player.cards) == 0:
            # no cards in hand
            if self.card_up <= player.card_threshold:
                self.player_takes_card()
            elif player.tokens <= player.token_threshold:
                self.player_takes_card()
            else:
                self.player_passes()
        elif self.deck.num > 0:
            if player.tokens == 0:
                self.player_takes_card()
            else:
                if player.eff_val <= 0:
                    if self.milking_potential():
                        self.player_passes()
                    else:
                        self.player_takes_card()
                elif player.eff_val <= player.eff_val_threshold and self.pot >= player.token_threshold:
                    self.player_takes_card()
                else:
                    self.player_passes()
        else:
            # last round, token threshold doesn't matter
            if player.tokens == 0:
                self.player_takes_card()
            else:
                if player.eff_val <= 0:
                    if self.milking_potential():
                        self.player_passes()
                    else:
                        self.player_takes_card()
                else:
                    self.player_passes()
            

    def play(self):
        for player in self.players:
            self.get_effective_value(player)
        self.player_logic()

    def score(self):
        for player in self.players:
            player.get_score()


def main():
    mytable = Table(verbose=1)
    mytable.play()

    for i,player in enumerate(mytable.players):
         print "Player", i+1, "has cards:", player.cards, "  tokens:", player.tokens, "  total:", player.score


if __name__ == "__main__":
    main()
