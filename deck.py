#!/usr/bin/python3
import sys
import random
from random import randint

class Deck(object):
    """A deck of cards.

    Attributes:
      cards (List[int])
      min_card (int)
      max_card (int)
      tot_orig_cards (int)
      tot_cards (int)

    Methods:
      shuffle()
      discard()
      draw()
    """

    def __init__(self, num=33, offset=3, dis=9):
        """
        Args::
          num (int): number of cards in initial setup (default 33)
          offset (int): lowest numbered card (default 3)
          dis (int): number of cards to discard in setup (default 9)

        Note:
          Defaults are official game values: cards are numbered from 3 to 35,
          i.e. 33 cards with an offset of 3, 9 of which are discarded 
          (giving a final deck of 24 cards).
        """
        if num < 1:
            sys.exit("Cannot initialize Deck with less than 1 card!")
        if offset < 1:
            sys.exit("A positive offset value is required")
        if num <= dis:
            sys.exit("Discarding all the cards...")
        self.min_card = offset
        self.max_card = num + offset - 1
        self.tot_orig_cards = num
        self.tot_cards = num - dis
        self.cards = []
        for i in range(num):
            self.cards.append(i + offset)
        self.shuffle()
        self.discard(dis)

    def shuffle(self):
        """Randomize the order of cards in the deck."""
        shuffled = []
        while len(self.cards) > 0:
            j = random.choice(self.cards)
            self.cards.remove(j)
            shuffled.append(j)
        self.cards = shuffled

    def discard(self, begone=1):
        """Remove a number of cards from the deck.

        Args:
            begone (int):  number of cards to discard
        """
        if begone < 0 or begone > len(self.cards):
            sys.exit("Cannot discard", begone, "cards!")
        while begone > 0:
            self.cards.pop(0)
            begone -= 1

    def draw(self):
        """Remove a card from the deck and return its value.

        Returns:
            int: value of card, or 0 if no cards in deck
        """
        try:
            card = self.cards.pop(0)
            return card
        except IndexError:
            return 0

