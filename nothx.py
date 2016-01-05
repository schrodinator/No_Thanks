#!/usr/bin/python
import sys
import random
from random import randint

class Deck(object):

    def __init__(self, num = 33):
        self.num = num
        self.cards = []
        for i in range(num):
            self.cards.append(i + 3)
        self.discard(9)
        self.shuffle()

    def shuffle(self):
    # learn how to shuffle in-place
        b = []
        for i in range(self.num):
            j = random.choice(self.cards)
            self.cards.remove(j)
            b.append(j)
        self.cards = b

    def discard(self, begone):
        for j in range(begone):
            i = randint(0,self.num-1)
            del self.cards[i]
            self.num -= 1

    def draw(self):
        if self.num > 0:
            self.num -= 1
            card = self.cards.pop()
            print "Card up:", card
            return card


class Player(object):

    def __init__(self):
        self.chips = 11
        self.cards = []
        self.score = 0

    def play_chip(self):
        if self.chips > 0:
            self.chips -= 1
        else:
            sys.exit("Played an imaginary chip!")

    def take_card(self, card):
        self.cards.append(card)
        self.cards.sort()

    def get_score(self):
        cards = list(self.cards)
        tot = 0
        low = cards.pop(0)
        prev = low
        while len(cards) > 0:
            current = cards.pop(0)
            if current > prev + 1:
                tot += low
                low = current
            prev = current
        tot += low
        self.score = tot - self.chips


class Table(object):

    def __init__(self, num_players = 3):
        if num_players < 1:
            sys.exit("Need players!")
        self.deck = Deck()
        self.num_players = num_players
        self.players = []
        for i in range(num_players):
            self.add_player()
        self.whose_turn = 0
        self.pot = 0
        self.card_up = self.deck.draw()

    def add_player(self):
        self.players.append(Player())

    def next_turn(self):
        self.players[self.whose_turn].play_chip()
        print "Player", self.whose_turn, "plays chip, has", self.players[self.whose_turn].chips, "remaining"
        self.pot += 1
        self.whose_turn = (self.whose_turn + 1) % self.num_players
        self.play()

    def player_takes_card(self):
        print "Player", self.whose_turn, "takes card:", self.card_up
        self.players[self.whose_turn].take_card(self.card_up)
        self.players[self.whose_turn].chips += self.pot
        self.pot = 0
        if self.deck.num > 0:
            self.card_up = self.deck.draw()
            self.play()
        else:
            self.score()

    def play(self):
        if self.card_up < 9:
            self.player_takes_card()
        else:
            if self.players[self.whose_turn].chips > 0:
                self.next_turn()
            else:
                self.player_takes_card()

    def score(self):
        for player in self.players:
            player.get_score()


def main():
    mytable = Table()
    mytable.play()
    for player in mytable.players:
         print "cards:", player.cards, "  chips:", player.chips, "  total:", player.score


if __name__ == "__main__":
    main()
