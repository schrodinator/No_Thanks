#!/usr/bin/python3
import sys
import random
from random import randint
from statistics import mean, median_low, median_high, median

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


class Table(object):
    """The Table object contains a Deck object, 3-5 Player objects, 
       and the core game logic"""

    def __init__(self, players=None, num_ai_players=3, num_cards=33, offset=3, \
                 dis=9, verbose=1):
        """
        Args:
          players = list of user-created objects of class Player
          num_ai_players = number of computer-generated players desired
          num_cards = number of cards in the setup deck (prior to discarding)
          offset = the lowest card value
          dis = number of cards to discard
          verbose = verbosity level. Options:
                   0  friendly to computer parsing but not human reading
                   1  default human readable
                   2  detailed human readable
        """
        self.players = []
        self.verbosity = verbose
        self.whose_turn = 0
        self.pot = 0
        self.deck = Deck(num_cards, offset, dis)
        try:
            num_nonrandom_players = len(players)
        except TypeError:
            num_nonrandom_players = 0
        self.num_players = num_nonrandom_players + num_ai_players
        if self.num_players > 5:
            sys.exit("Too many players! Max = 5")
        else:
            given_pos = []
            if num_nonrandom_players > 0:
                self.players = players
                for player in players:
                    given_pos.append(player.pos)
                # check given player positions for sanity
                if max(given_pos) >= self.num_players or min(given_pos) < 0:
                    sys.exit("Player position out of bounds")
                for i in range(4):
                    cnt = given_pos.count(i)
                    if cnt > 1:
                        sys.exit("Duplicate player positions")
                    if cnt > 0 and i >= self.num_players:
                        sys.exit("Player position out of bounds")
            for pos in range(self.num_players):
                if pos not in given_pos:
                    # add randomized AI player at this position
                    self.add_player(pos)
            self.players.sort(key=lambda x: x.pos)
        if self.verbosity > 0:
            print("\nInitial deck:", self.deck.cards)
        self.card_up = self.deck.draw()
        if self.verbosity > 0:
            print("Card up:", self.card_up)

    def add_player(self, pos):
        """
        Add a player with random attributes
        (card_thresohld, token_threshold, and eff_val_threshold)
        """
        init_threshold = randint(self.deck.min_card, self.deck.max_card - 1)
        eff_val_threshold = randint(0, 6)
        token_threshold = randint(0, 10)
        pot_threshold = randint(6, 20)
        self.players.append( \
             Player(pos, init_threshold, eff_val_threshold, token_threshold, \
                    pot_threshold)
        )
        if self.verbosity > 0:
            print("Created Player", pos+1, "at position", pos, \
                  "with init_threshold:", self.players[pos].init_threshold, \
                  "and token_threshold:", self.players[pos].token_threshold, \
                  "and eff_val_threshold:", self.players[pos].eff_val_threshold)

    def other_player_cards(self):
        """
        Returns a list of all cards currently held by all players
        other than the current player.
        """
        player = self.players[self.whose_turn]
        other_player_cards = []
        for other_player in self.players:
            if other_player != player:
                other_player_cards += other_player.cards
        return other_player_cards

    def get_effective_value(self):
        """
        Returns the effective value of card_up to the current player.
        The effective value is the amount by which taking the card 
        and the pot woudl alter the player's current score.
        """
        for player in self.players:
            if self.card_up + 1 in player.cards:
                if self.card_up - 1 in player.cards:
                    # Bridging card - connects two cards/runs in the player's
                    # hand. Would lower player's score by the value of the
                    # higher run.
                    effective_value = -(self.card_up + 1)
                else:
                    # If taken, card_up would become the lowest card in a run.
                    # Would lower player's score by 1 point.
                    effective_value = -1
            elif self.card_up - 1 in player.cards:
                # If taken, card_up would go at the end of a run.
                # Doesn't change player's score.
                effective_value = 0
            elif self.card_up + 2 in player.cards:
                # card_up is 1 card away from being connected in a run.
                if self.card_up + 1 in self.other_player_cards():
                    # The bridging card has already been taken:
                    # no chance of completing the run.
                    effective_value = self.card_up
                else:
                    # Effective value depends on probability of completing the
                    # run.
                    prob = float(len(self.deck.cards)) / float(self.deck.tot_orig_cards)
                    # Calculate expectation value.
                    effective_value = -2.0*prob + self.card_up*(1.0 - prob)
                    if self.verbosity == 2:
                        print("  eff_val =", effective_value - self.pot, \
                              "to player", player.pos + 1)
            else:
                effective_value = self.card_up
            # Card value is offset by the number of tokens in the pot.
            effective_value -= self.pot
            player.eff_val = effective_value

    def milking_potential(self):
        """
        If a card is desirable to one player but highly undesirable to all of
        the others, the player may deliberately pass with the intention of
        "milking" the others for tokens.
        """
        player = self.players[self.whose_turn]
        # Don't milk if any player has no cards in hand
        for other_player in self.players:
            if other_player != player:
                if len(other_player.cards) == 0:
                    return 0
        if self.card_up == self.deck.max_card:
            # At best, this card will improve the player's score by 0 points
            # (that is, if the player has max_card-1 and possibly
            # max_card-2...max_card-n). Always better to force someone else to
            # take the highest card in the game, until tokens become a
            # consideration.
            if len(self.deck.cards) == 0 or self.pot < player.pot_threshold:
                return 1
        # Ensure the effective value is high enough that the card will come
        # back to the milking player, i.e. its effective value will not
        # drop to/below 4 before all other players have passed.
        num = len(self.players)
        for other_player in self.players:
            if other_player != player:
                if other_player.tokens < num \
                   or other_player.eff_val < num + 4:
                    if self.verbosity == 2:
                        print("  too risky, not milking")
                    return 0
        if self.verbosity == 2:
            print("  milking")
        return 1

    def vindictive_potential(self):
        """
        A player who is losing may, out of vindictiveness, take a card
        desired by a player who is milking -- even though the card hurts
        her own score. This method returns 1 if the player feels vindictive
        and 0 if vindictiveness is not warranted.
        """
        player = self.players[self.whose_turn]
        score = player.get_score()
        thresh = randint(20, 40)
        val = 0
        if len(self.deck.cards) > len(self.players):
            # Don't be vindictive until late in the game.
            return 0
        for other_player in self.players:
            if other_player != player:
                if other_player.get_score() + thresh > score:
                    # Player is not losing, or is not trailing by enough points,
                    # to risk taking the card.
                    return 0
                if other_player.eff_val < val:
                    val = other_player.eff_val
        if val < 0:
            if self.verbosity == 2:
                print("  player takes card out of spite")
            return 1

    def play(self):
        """
        Core game logic. Decide whether a player will take or pass on the card
        card_up, based on the player's attributes (init_threshold,
        token_threshold, eff_val_threshold) and circumstances of the game
        (value of card_up, number of cards remaining in deck, cards in other
        players' possession, etc.)
        """
        player = self.players[self.whose_turn]
        self.get_effective_value()
        if player.tokens == 0:
            if self.verbosity == 2:
                print("  no tokens left")
            self.player_takes_card()
        elif player.tokens < player.token_threshold \
                  and self.pot > player.pot_threshold:
            if self.verbosity == 2:
                print("  take it for the pot. tokens:", \
                      player.tokens, "  pot:", self.pot)
            self.player_takes_card()
        elif len(player.cards) == 0:
            # No cards in hand yet.
            if player.eff_val <= player.init_threshold:
                if self.verbosity == 2:
                    print("  no cards in hand, card within threshold: take")
                self.player_takes_card()
            else:
                self.player_passes()
        else:
            if player.eff_val < 1.0:
                # Note: < 1 instead of < 0 because it costs 1 to pass
                # (by playing a token)
                if self.verbosity == 2:
                    print("  eff_val < 1")
                if self.milking_potential():
                    self.player_passes()
                else:
                    self.player_takes_card()
            elif len(self.deck.cards) > 0 \
                and player.eff_val <= player.eff_val_threshold \
                and ( \
                     self.pot > 0  \
                     or self.card_up - 1 not in self.other_player_cards() \
                     or self.card_up + 1 not in self.other_player_cards() \
                ):
                # The player may choose to take a card with a positive
                # effective value (i.e. one which increases the player's score)
                # in order to obtain the pot and the card for constructing
                # potential future runs.
                # Note: Saving tokens for future use doesn't matter in the final
                # round -- only the effective value matters at the end of the 
                # game.
                if self.verbosity == 2:
                    print("  eff_val below threshold")
                self.player_takes_card()
            elif self.vindictive_potential():
                self.player_takes_card()
            else:
                if self.verbosity == 2:
                    print("  pass")
                self.player_passes()

    def player_passes(self):
        """
        The current player plays a token from her token reserve,
        then it's the next player's turn.
        """
        player = self.players[self.whose_turn]
        player.play_token()
        if self.verbosity > 0:
            print("Player", self.whose_turn + 1, sorted(player.cards),\
                  "plays token, has", player.tokens, "remaining")
        self.pot += 1
        self.whose_turn = (self.whose_turn + 1) % self.num_players
        self.play()

    def player_takes_card(self):
        """
        The current player takes the card card_up. If no cards remain in the
        deck, the game ends. Otherwise, the game continues: a new card is drawn
        and the same player may either take it or play a token and pass.
        """
        player = self.players[self.whose_turn]
        if self.verbosity > 0:
            print("Player", self.whose_turn + 1, sorted(player.cards), \
                  "takes card:", self.card_up)
        player.take_card(self.card_up, self.pot)
        self.pot = 0
        self.card_up = self.deck.draw()
        if (self.card_up):
            if self.verbosity > 0:
                print("Card up:", self.card_up)
            self.play()
        else:
            if self.verbosity > 0:
                print("Game Over\n")
            return 0

    def score(self):
        """
        Obtain scores of all players and print (or return) them.
        If verbosity = 0, scores and game info are returned as a list of
        features for analysis. If verbosity > 0, scores are printed to screen.
        """
        scores = []
        for i, player in enumerate(self.players):
            player.get_score()
            scores.append(player.score)
            if self.verbosity > 0:
                print("Player", i+1, " score:", player.score, \
                      " tokens:", player.tokens, \
                      " cards:", sorted(player.cards))
        if self.verbosity > 0:
            return 0
        # construct computer-readable feature vector
        low = min(scores)
        wins = 0
        for player in self.players:
            if player.score == low:
                player.win = 1
                wins += 1
        if wins > 1:
            for player in self.players:
                if player.win == 1:
                    player.win = 2
        features = []
        for player in self.players:
            feature = []
            feature.append(player.pos)
            feature.append(player.win)
            feature.append(player.score)
            feature.append(player.init_threshold)
            feature.append(player.token_threshold)
            feature.append(player.eff_val_threshold)
            feature.append(player.pot_threshold)
            feature.append(min(player.token_history))
            feature.append(max(player.token_history))
            feature.append(mean(player.token_history))
            feature.append(median_low(player.token_history))
            feature.append(min(player.eff_val_history))
            feature.append(max(player.eff_val_history))
            feature.append(mean(player.eff_val_history))
            feature.append(median_low(player.eff_val_history))
            feature.append(len(player.cards))
            feature.append(player.num_runs)
            feature.append(player.cards[0])
            feature.append(min(player.cards))
            feature.append(max(player.cards))
            feature.append(mean(player.cards))
            feature.append(median_low(player.cards))
            #feature.append(player.cards)
            features.append(feature)
        return features


def main():
    mytable = Table(num_ai_players=3, verbose=2)
    mytable.play()
    mytable.score()


if __name__ == "__main__":
    main()
