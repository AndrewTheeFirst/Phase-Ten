from PhaseTen import Player, Pickup, Phase
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
        self.phases: list[Phase] = []
        self.discard = self.deck.discard
        self.game_running = True
        self.round_over = False
    
    def deal(self):
        for _ in range(10):
            for player in self.players:
                player.hand.push(self.deck.pop())
        self.discard.push(self.deck.pop())

    def show_table(self, curr_player: Player):
        clear()
        for phase in self.phases:
            pass
        print(self.deck, end = "\n\n")
        print(curr_player.hand)

    def player_turn(self, player: Player):
        self.show_table(player)
        choice = 3
        while choice == 3:
            choice = intin("Draw from Discard(1), from Deck(2), or Sort(3): ", (1, 3))
            if choice == 1: # Player picks up a card
                player.hand.push(self.discard.pop())
            elif choice == 2:
                player.hand.push(self.deck.pop())
            else:
                if intin("Would you like to sort by Face(1) or Color(2): ", (1, 2)) == 1:
                    player.hand.face_sort()
                else:
                    player.hand.color_sort()
            self.show_table(player)

        # TODO Can player complete phase ?

        # TODO If player out, allow phase addons
        
        # TODO Check if player is has no more cards

        self.discard.push(player.hand.pop()) # Player puts down a card

        # TODO Check if player is has no more cards (here too)

        self.show_table(player)


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
                self.player_turn(next(turn))
            for player in self.players:
                player.hand.clear()
                if player.out:
                    player.phase += 1
                player.out = False
            
if __name__ == "__main__":
    g = Game(2)
    g.mainloop()
                