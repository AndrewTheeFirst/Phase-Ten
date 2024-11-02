from PhaseTen import Player, Pickup
from itertools import cycle
from os import system, name as os_name

def clear():
    if os_name == "nt":
        system("cls")
    else:
        print("\x1b[2J\x1b[H", end="")

def intin(prompt: str, range: tuple[int, int]) -> int:
    while True:
        try:
            user_input = int(input(prompt))
            if user_input < range[0] or user_input > range[1]:
                print(f"Out of range {range}. Try again.")
                continue
            return user_input
        except ValueError:
            print("Not a number. Try again: ")

class Game:
    # Game will have Players
    def __init__(self, num_players = None):
        if not num_players:
            num_players = intin("How many players (2-6): ", (2, 6))
        self.players = [Player() for _ in range(num_players)]
        self.deck = Pickup()
        self.discard = self.deck.discard
        self.game_running = True
        self.round_over = False
    
    def show(self, player: Player):
        clear()
        print(player.hand)
        print(self.deck)
        print()

    def deal(self):
        for _ in range(10):
            for player in self.players:
                player.hand.push(self.deck.pop())
        self.discard.push(self.deck.pop())

    def set_turn(self, player: Player):

        self.show(player)
        choice = intin("Draw from Discard(1) or from Deck(2): ", (1, 2))
        
        if choice == 1: # Player picks up a card
            player.hand.push(self.discard.pop())
        else:
            player.hand.push(self.deck.pop())
        self.show(player)

        # TODO Can player complete phase ?

        # TODO If player out, allow phase addons
        
        # TODO Check if player is has no more cards

        self.discard.push(player.hand.pop()) # Player puts down a card

        # TODO Check if player is has no more cards (here too)

        self.show(player)


        input('press any key to end your turn...')
        clear()

    def mainloop(self):
        clear()
        turn = cycle(self.players)
        while self.game_running:
            self.round_over = False
            self.deal()
            while not self.round_over:
                input('enter any key to continue...\n')
                self.set_turn(next(turn))

            for player in self.players:
                player.hand.clear()
                # TODO Increment phase of all out players
                player.out = False
            
if __name__ == "__main__":
    g = Game(2)
    g.mainloop()
                