#!/usr/bin/python3
import sys
from table import Table

def main():
    mytable = Table(num_ai_players=3, verbose=2)
    mytable.play()
    mytable.score()


if __name__ == "__main__":
    main()
