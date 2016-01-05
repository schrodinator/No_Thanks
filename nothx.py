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

    def __init__(self, card_threshold = 9, token_threshold = 0):
        self.tokens = 11
        self.cards = []
        self.score = 0
        self.card_threshold = card_threshold
        self.token_threshold = token_threshold

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

    def logic(self, card_up, pot):
        # returns 1 if player takes card_up, 0 if player passes (spends a token)
        if len(self.cards) < 2 and card_up < self.card_threshold:
            return 1
        if card_up - 1 in self.cards:
            return 1
        if self.tokens > self.token_threshold:
            return 0
        else:
            return 1


class Table(object):

    def __init__(self, players=[], num_players=0, num_cards=33, offset=3, verbose=1):
        self.players = players
        self.verbosity = verbose
        self.whose_turn = 0
        self.pot = 0
        self.deck = Deck(num_cards, offset)
        if len(players) > 0:
            self.num_players = len(players)
        else:
            if num_players > 0:
                self.num_players = num_players
                for i in range(self.num_players):
                    self.add_player()
            else:
                sys.exit("Need players!")
        if self.verbosity == 1:
            print "\nInitial deck:", self.deck.cards
        self.card_up = self.deck.draw()
        if self.verbosity == 1:
            print "Card up:", self.card_up

    def add_player(self):
        # Add a player with random attributes
        min_card = self.deck.offset
        max_card = min_card + self.deck.num - 1
        card_threshold = randint(min_card, max_card)
        token_threshold = randint(0, 10)
        self.players.append(Player(card_threshold, token_threshold))
        if self.verbosity == 1:
            print "Created Player with card_threshold:", card_threshold,"and token_threshold:",token_threshold

    def next_turn(self):
        self.players[self.whose_turn].play_token()
        if self.verbosity == 1:
            print "Player", self.whose_turn + 1, "plays token, has", self.players[self.whose_turn].tokens, "remaining"
        self.pot += 1
        self.whose_turn = (self.whose_turn + 1) % self.num_players
        self.play()

    def player_takes_card(self):
        if self.verbosity == 1:
            print "Player", self.whose_turn + 1, "takes card:", self.card_up
        self.players[self.whose_turn].take_card(self.card_up)
        self.players[self.whose_turn].tokens += self.pot
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

    def play(self):
        if self.players[self.whose_turn].logic(self.card_up, self.pot) == 1:
            self.player_takes_card()
        else:
            self.next_turn()

    def score(self):
        for player in self.players:
            player.get_score()


def main():
    #myplayers = []
    #myplayers.append(Player(card_threshold=11, token_threshold=5))
    #myplayers.append(Player(card_threshold=9, token_threshold=4))
    #myplayers.append(Player(card_threshold=5, token_threshold=8))

    mytable = Table(num_players=3)
    mytable.play()

    for i,player in enumerate(mytable.players):
         print "Player", i+1, "has cards:", player.cards, "  tokens:", player.tokens, "  total:", player.score


if __name__ == "__main__":
    main()
