#!/usr/bin/python3
import sys

class Player(object):
    """Define a player by her attributes (risk thresholds) and actions

    Attributes:
      pos (int): Position in play order (indexed from 0)
      win (int): 
      tokens (int): Number of tokens in the player's possession.
    """

    def __init__(self, pos, init_threshold=9, eff_val_threshold=0, \
                 token_threshold=0, pot_threshold=8):
        """
        Args:
          pos (int): Position in play order (starting from 0)
          init_threshold (int): Max effective value of card to take when player
                  has no cards in hand. Player will attempt to pass if this
                  value is exceeded.
          eff_val_threshold (int): Max effective value of card to take after
                  the first turn (used when player has at least 1 card in hand)
          token_threshold (int): Min number of tokens the player desires to
                  retain prior to the final round. If the player's number of
                  tokens falls below this threshold, she will consider the
                  pot threshold before considering the effective value of the
                  card.
          pot_threshold (int): Min number of tokens in the pot that will entice
                  the player to take the card, regardless of effective value.
        """
        self.pos = pos
        self.tokens = 11
        self.cards = []
        self.score = 0
        self.eff_val = 0
        self.init_threshold = init_threshold
        # Do not allow a token_threshold of 11: player will take all the cards.
        if token_threshold > 10 or token_threshold < 0:
            sys.exit("token_threshold must be 0-10")
        else:
            self.token_threshold = token_threshold
        self.pot_threshold = pot_threshold
        self.eff_val_threshold = eff_val_threshold
        self.win = 0
        self.num_runs = 0
        self.token_history = [ 11 ]
        self.eff_val_history = []

    def play_token(self):
        if self.tokens > 0:
            self.tokens -= 1
            self.token_history.append(self.tokens)
        else:
            sys.exit("Played an imaginary token!")

    def take_card(self, card, pot):
        self.cards.append(card)
        self.tokens += pot
        self.token_history.append(self.tokens)
        self.eff_val_history.append(self.eff_val)

    def get_score(self):
        """
        Calculate the player's current score.
        """
        cards = list(sorted(self.cards))
        tot = 0
        self.num_runs = 0
        if len(cards) == 0:
            self.score = 0
        else:
            low = cards.pop(0)
            prev = low
            self.num_runs = 1
            while len(cards) > 0:
                current = cards.pop(0)
                if current > prev + 1:
                    tot += low
                    low = current
                    self.num_runs += 1
                prev = current
            tot += low
            self.score = tot - self.tokens
        return self.score
