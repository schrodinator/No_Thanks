# No Thanks

"No Thanks" is a 3-5 player card game designed by Thorsten Gimmler. The winner is the player with the lowest final score. The game is played with cards numbered 3 through 35, of which 9 are chosen at random and discarded, leaving 24 cards. 

Each player begins the game with 0 cards and 11 tokens. At the beginning of a turn, a card is drawn from the shuffled deck. A player may either take the card or pass by placing one of her tokens into the token pot. If a player is out of tokens, she must take the card. When a player takes a card, another is immediately drawn and the same player may choose to take the new card or pass by playing a token. The next player gets a chance to take/pass on the card only after the previous player has passed. When the card is taken, the player takes all tokens in the token pot along with it. The game ends when the last card from the deck is taken.

A player's final score is calculated by adding the points of the cards in her hand and subtracting the number of tokens in her possession. A card's number gives its point value, except in the case where a player has collected a run of consecutively-numbered cards. The point value of an entire run is equal to the value of the lowest-numbered card in that run. For example, a player with the hand

[3, 4, 5, 10, 11, 15]

has a score of 3 + 10 + 15 = 28, from which the number of the player's tokens is then subtracted.

The nothx.py Python script simulates a game of "No Thanks" to investigate optimal strategy. Players are constructed by specifiying the following paramters:

| Parameter | Description |
| --------- | ----------- |
| pos		    | Position in play order, indexed from 0. |
| card_threshold    | Maximum value of card the player is willing to take at the beginning of the game, when the player has 0 cards in hand. For a game using the standard deck, possible values are 3-35. |
| token_threshold   | Minimum number of tokens the player desires to reserve for future rounds. At the beginning of the game, when the player has 0 cards in hand, the player will take a card exceeding card_threshold in order to retain a number of tokens equal to the token_threshold for use in future rounds. Allowed values are 0-10. |
| eff_val_threshold | The effective value threshold, where effective value = value of card - value of pot. A player may be willing to take a card that increases her score by a small amount in order to obtain the pot and a card with which to build future runs. The effective value threshold is not used during the final round, when obtaining tokens and cards for future rounds ceases to matter. Advised values (used for computer-generated players) are 0-4. |
