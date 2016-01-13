#!/usr/bin/python
import sys
import random
from random import randint

class Deck(object):

    def __init__(self, num = 33, offset = 3, dis = 9):
        # Arguments:
        # num = number of cards in initial setup
        # offset = lowest numbered card
        # dis = number of cards to discard in setup
        #
        # Defaults are official game values:
        # cards are numbered from 3 to 35,
        # i.e. 33 cards with an offset of 3,
        # 9 of which are discarded (giving a final deck of 24 cards)
        if num < 1 or offset < 0:
            sys.exit("Cannot initialize Deck with less than 1 card!")
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

    def num(self):
        return len(self.cards)

    def shuffle(self):
        shuffled = []
        num = self.num()
        for i in range(num):
            j = random.choice(self.cards)
            self.cards.remove(j)
            shuffled.append(j)
        self.cards = shuffled

    def discard(self, begone = 1):
        if begone < 0 or begone > self.num():
            sys.exit("Cannot discard", begone, "cards!")
        for i in range(begone):
            self.cards.pop(0)

    def draw(self):
        if self.num() > 0:
            card = self.cards.pop(0)
            return card
        else:
            return -1


class Player(object):

    def __init__(self, pos, card_threshold = 9, token_threshold = 0):
        # Arguments:
        # pos = position in play order (starting from 0)
        # card_threshold = max value of card to take when player has 0 cards 
        #         (player will attempt to pass if card_threshold is exceeded)
        # token_threshold = min number of tokens the player wants to reserve
        #         for future rounds. When Player has 0 cards in hand,
        #         Player will take a card exceeding card_threshold in
        #         order to retain a number of tokens equal to the token_threshold.
        self.pos = pos
        self.tokens = 11
        self.cards = []
        self.score = 0
        self.eff_val = 0
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
            return self.score


class Table(object):

    def __init__(self, players=[], num_ai_players = 3, num_cards=33, offset=3, dis=9, verbose=1):
        # Arguments:
        # players = list of user-created players
        # num_ai_players = number of computer-generated players desired
        # num_cards = number of cards in the setup deck (prior to discarding)
        # offset = the lowest card value
        # dis = number of cards to discard
        # verbose = verbosity level. Options:
        #          0  friendly to computer parsing but not human reading
        #          1  default human readable
        #          2  detailed human readable
        self.players = []
        self.num_players = len(players) + num_ai_players
        self.verbosity = verbose
        self.whose_turn = 0
        self.pot = 0
        self.deck = Deck(num_cards, offset, dis)
        if self.num_players > 5:
            sys.exit("Too many players! Max = 5")
        else:
            given_pos = []
            if len(players) > 0:
                self.players = players
                for player in players:
                    given_pos.append(player.pos)
                # check given player positions for sanity
                if max(given_pos) >= self.num_players or min(given_pos) < 0:
                    sys.exit("Player position out of bounds")
                for i in range(4):
                    ct = given_pos.count(i)
                    if ct > 1:
                        sys.exit("Duplicate player positions")
                    if ct > 0 and i >= self.num_players:
                        sys.exit("Player position out of bounds")
            for pos in range(self.num_players):
                if pos not in given_pos:
                    # add randomized AI player at this position
                    self.add_player(pos)
                    print "Created Player", pos+1, "at position", pos,\
                        "with card_threshold:", self.players[pos].card_threshold, \
                        "and token_threshold:",self.players[pos].token_threshold
            self.players.sort(key=lambda x: x.pos)
        if self.verbosity > 0:
            print "\nInitial deck:", self.deck.cards
        self.card_up = self.deck.draw()
        if self.verbosity > 0:
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
        card_threshold = randint(self.deck.min_card, self.deck.max_card - 1)
        # Do not allow a token_threshold of 11: player will take all the cards.
        token_threshold = randint(0, 10)
        self.players.append(Player(pos, card_threshold, token_threshold))

    def other_player_cards(self):
        player = self.players[self.whose_turn]
        other_player_cards = []
        for other_player in self.players:
            if other_player != player:
                other_player_cards.append(other_player.cards)
        return other_player_cards

    def get_effective_value(self):
        for player in self.players:
            if self.card_up + 1 in player.cards:
                if self.card_up - 1 in player.cards:
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
            elif self.card_up + 2 in player.cards:
                # card_up is 1 card away from being connected in a run.
                if self.card_up + 1 in self.other_player_cards():
                    # The bridging card has already been taken:
                    # no chance of completing the run.
                    effective_value = self.card_up
                else:
                    # effective value depends on probability of completing the run.
                    prob = float(self.deck.num()) / float(self.deck.tot_orig_cards)
                    # Calculate expectation value.
                    effective_value = -2.0*prob + self.card_up*(1.0 - prob)
                    if self.verbosity == 2:
                        print "  eff_val =", effective_value - self.pot, "to player", player.pos+1
            else:
                effective_value = self.card_up
            # Card value is offset by the number of tokens in the pot.
            effective_value -= self.pot
            player.eff_val = effective_value

    def milking_potential(self):
        # If a card is desirable to one player but highly undesirable to all of the others,
        # the player may deliberately pass with the intention of "milking" the other
        # players for tokens.
        player = self.players[self.whose_turn]
        if self.card_up == self.deck.max_card:
            # At best, this card will improve the player's score by 0 points
            # (that is, if the player has max_card-1 and possibly max_card-2...max_card-n). 
            # Always better to force someone else to take the highest card in the game, 
            # until tokens become a consideration.
            pot_thresh = randint(8,15)
            if self.deck.num == 0 or self.pot < pot_thresh:
                return 1
        for other_player in self.players:
            if other_player != player:
                if len(other_player.cards) == 0:
                    return 0
        thresh = 3
        for other_player in self.players:
            if other_player != player:
                if other_player.tokens == 0 or other_player.eff_val < thresh:
                    # Too much risk that another player will take the card
                    if self.verbosity == 2:
                        print "  too risky, not milking"
                    return 0
        if self.verbosity == 2:
            print "  milking"
        return 1

    def vindictive_potential(self):
        # A player who is losing may, out of vindictiveness, take a card desired by 
        # a player who's milking -- even though the card hurts their score.
        player = self.players[self.whose_turn]
        score = player.get_score()
        thresh = randint(20,40)
        val = 0
        if self.deck.num() > len(self.players):
            # Don't be vindictive until late in the game
            return 0
        for other_player in self.players:
            if other_player != player:
                if other_player.get_score() + thresh > score:
                    # Player is not losing, or is not trailing by enough points, 
                    # to risk taking the card
                    return 0
                if other_player.eff_val < val:
                    val = other_player.eff_val
        if val < 0:
            if self.verbosity == 2:
                print "  player takes card out of spite"
            return 1

    def player_logic(self):
        player = self.players[self.whose_turn]
        if player.tokens == 0:
            if self.verbosity == 2:
                print "  no tokens left"
            self.player_takes_card()
        elif len(player.cards) == 0:
            # No cards in hand yet.
            if self.card_up <= player.card_threshold:
                if self.verbosity == 2:
                    print "  no cards in hand, card within threshold: take"
                self.player_takes_card()
            elif player.tokens < player.token_threshold:
                if self.verbosity == 2:
                    print "  no cards in hand, tokens less than threshold: take"
                self.player_takes_card()
            else:
                if self.verbosity == 2:
                    print "  no cards in hand, card above threshold, plenty of tokens: pass"
                self.player_passes()
        else:
            if player.eff_val < 1.0:
                if self.milking_potential():
                    self.player_passes()
                else:
                    self.player_takes_card()
            elif self.deck.num() > 0 and player.eff_val <= randint(1,4) and self.pot >= max(player.token_threshold, 3):
                # With some probability, Player takes a card with a small positive effective value
                # (i.e. increases player score) in order to obtain the pot. The tokens
                # in the pot may be used to pass on future even-higher-effective-valued cards.
                # Note: self.deck.num() > 0 because saving tokens for future use doesn't matter 
                # in the final round -- only the effective value matters in the final round.
                if self.verbosity == 2:
                    print "  take it for the tokens"
                self.player_takes_card()
            elif self.vindictive_potential():
                self.player_takes_card()
            else:
                if self.verbosity == 2:
                    "  pass"
                self.player_passes()

    def player_passes(self):
        player = self.players[self.whose_turn]
        player.play_token()
        if self.verbosity > 0:
            print "Player", self.whose_turn + 1, player.cards, "plays token, has", player.tokens, "remaining"
        self.pot += 1
        self.whose_turn = (self.whose_turn + 1) % self.num_players
        self.play()

    def player_takes_card(self):
        player = self.players[self.whose_turn]
        if self.verbosity > 0:
            print "Player", self.whose_turn + 1, player.cards, "takes card:", self.card_up
        player.take_card(self.card_up)
        player.tokens += self.pot
        self.pot = 0
        if self.deck.num() > 0:
            self.card_up = self.deck.draw()
            if self.verbosity > 0:
                print "Card up:", self.card_up
            self.play()
        else:
            if self.verbosity > 0:
                print "Game Over\n"
            self.score()

    def play(self):
        self.get_effective_value()
        self.player_logic()

    def score(self):
        for i,player in enumerate(self.players):
            player.get_score()
            if self.verbosity > 0:
                print "Player", i+1, " score:", player.score, " tokens:", player.tokens, " cards:", player.cards
        if self.verbosity == 0:
            # computer-parseable
            print " still need to decide which stats to collect... "


def main():
    mytable = Table(num_ai_players = 3, verbose = 1)
    mytable.play()


if __name__ == "__main__":
    main()
