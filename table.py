import sys
from random import randint
from player import Player
from deck import Deck

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
        eff_val_threshold = randint(0, 8)
        token_threshold = randint(0, 8)
        pot_threshold = randint(6, 20)
        self.players.append( \
             Player(pos, init_threshold, eff_val_threshold, token_threshold, \
                    pot_threshold)
        )
        if self.verbosity > 0:
            print("Created Player", pos+1, "at position", pos, \
                  "with init_threshold:", self.players[pos].init_threshold, \
                  "and token_threshold:", self.players[pos].token_threshold, \
                  "and eff_val_threshold:", self.players[pos].eff_val_threshold, \
                  "and pot_threshold:", self.players[pos].pot_threshold)

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
                        print("  Player {0}: effective value = {1:.2f}"\
                               .format(player.pos + 1, effective_value - self.pot))
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
        if self.pot > player.pot_threshold:
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
        i = (self.whose_turn + 1) % 3
        j = 1
        while i != self.whose_turn:
            other_player = self.players[i]
            if other_player.tokens == 0 or other_player.eff_val < j + 7:
                if self.verbosity == 2:
                    print("  Player {}: too risky, not milking"\
                          .format(player.pos + 1))
                return 0
            j += 1
            i = (i + 1) % 3
#       for other_player in self.players:
#           if other_player != player:
#               if other_player.tokens < self.num_players \
#                  or other_player.eff_val < self.num_players + 4:
#                   if self.verbosity == 2:
#                       print("  too risky, not milking")
#                   return 0
        if self.verbosity == 2:
            print("  Player {}: milking".format(player.pos + 1))
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
        if len(self.deck.cards) > self.num_players:
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
                print("  Player {}: No tokens left".format(player.pos + 1))
            self.player_takes_card()
        elif player.tokens < player.token_threshold \
                  and self.pot > player.pot_threshold \
                  and len(self.deck.cards) > 9 \
                  and self.card_up != self.deck.max_card:
            if self.verbosity == 2:
                print("  Player {} takes it for the pot. (tokens = {}, pot = {})"\
                      .format(player.pos + 1, player.tokens, self.pot))
            self.player_takes_card()
        elif len(player.cards) == 0:
            # No cards in hand yet.
            if player.eff_val <= player.init_threshold:
                if self.verbosity == 2:
                    print("  Player {}: Card within initial threshold value"\
                          .format(player.pos + 1))
                self.player_takes_card()
            else:
                self.player_passes()
        else:
            if player.eff_val < 1.0:
                # Note: < 1 instead of < 0 because it costs 1 point to pass
                # (by playing a token)
                if self.verbosity == 2:
                    print("  Player {}: effective value < 1"\
                          .format(player.pos + 1))
                if self.milking_potential():
                    self.player_passes()
                else:
                    self.player_takes_card()
            elif len(self.deck.cards) > 0 \
                and player.eff_val <= player.eff_val_threshold \
                and self.card_up - 1 not in self.other_player_cards():
                # The player may choose to take a card with a positive
                # effective value (i.e. one which increases the player's score)
                # in order to obtain the pot and the card for constructing
                # potential future runs.
                # Note: Saving tokens for future use doesn't matter in the final
                # round -- only the effective value matters at the end of the 
                # game.
                if self.verbosity == 2:
                    print("  Player {}: effective value below threshold"\
                          .format(player.pos + 1))
                self.player_takes_card()
            elif self.vindictive_potential():
                self.player_takes_card()
            else:
                self.player_passes()

    def player_passes(self):
        """
        The current player plays a token from her token reserve,
        then it's the next player's turn.
        """
        player = self.players[self.whose_turn]
        player.play_token()
        if self.verbosity > 0:
            print("Player", player.pos + 1, sorted(player.cards),\
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
            print("Player", player.pos + 1, sorted(player.cards), \
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
        if self.verbosity > 0:
            print('{0:6}  {1:5}  {2:6}  {3}'\
                  .format('Player', 'Score', 'Tokens', 'Cards'))
        for player in self.players:
            player.get_score()
            scores.append(player.score)
            if self.verbosity > 0:
                print('{0:6d}  {1:5d}  {2:6d}  {3}'.format(player.pos + 1, \
                       player.score, player.tokens, sorted(player.cards)))
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
            feature.append(player.token_history)
            feature.append(player.eff_val_history)
            feature.append(player.cards)
            features.append(feature)
        return features

