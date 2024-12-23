# Andrew Patton
# Phase Ten
# 2024-11-1 Began refactoring - Created new class structure
# 2024-11-2 Further refactoring - Expanded on stack subclass methods as well as stack class)
# 2024-11-3 Worked on Phase class methods and Hand sorting
# 2024-11-4 Implemented Phases and Phase completion, better printing, and skipping
# 2024-11-5 Implemented Phase addition - Production
# 2024-11-8 Phase class rework (Stack, verification, merge, etc.) misc. tweaks
# 2024-12-21 Complete refactor - more consistent printing, improved eventloop
# 2024-12-23 Bug fix, Moved controls.py into main.py

from stack import Pickup, Phase, Hand
from os import system, name as os_name
from time import sleep

def clear():
    '''clears the console / terminal'''
    if os_name == "nt":
        system("cls")
    else:
        print("\x1b[2J\x1b[H", end="")

def timed_message(prompt: str, seconds: float = 1.0):
    '''displays specified prompt for a number of seconds'''
    print(prompt)
    sleep(seconds)

PHASES = [["set3", "set3"],
          ["set3", "run4"],
          ["set4", "run4"],
          ["run7"],
          ["run8"],
          ["run9"],
          ["set4", "set4"],
          ["set7c"],
          ["set5", "set2"],
          ["set5", "set3"]]

class Player:
    '''Player has a Hand and Phases'''
    count = 0

    def __init__(self):
        self.phase = 0
        self.cards = Hand()
        self.out = False
        self.points = 0
        self.turn_over = True
        self.name = Player.count + 1
        Player.count += 1

    def show_space(self, phase: Phase):
        space = phase.desc() + '\n' + str(phase) + '\n' + str(self.cards)
        clear()
        print(space)

    def has_cards(self):
        '''Returns True if a player has any cards, returns False otherwise'''
        return self.cards.size() != 0

    def consolidate(self):
        self.cards.clear()
        if self.out:
            self.phase += 1
            self.out = False
        self.points += self.cards.sum()

    def sort(self):
        '''Player will choose how to sort their hand'''
        clear()
        print(self.cards)
        choices = {'1': lambda: self.cards.face_sort(), 
                   '2': lambda: self.cards.color_sort()}
        user_input = input("Press 1 to sort by Face | Press 2 to sort by Color")
        choices.get(user_input, lambda: timed_message("Invalid Argument"))()

    def do_phase(self, phase: Phase):
        while True:
            self.show_space(phase)
            user_input = input("Which cards would you like to drop? (Enter Q when done) ")
            if user_input.upper() == 'Q':
                break
            elif (index := self.cards.find(user_input)) != -1:
                phase.push(self.cards.pop(index))
            else:
                timed_message("Card not found. (ex. g3 is Green 4; w is Wild)")
        return phase.is_phase()

    def get_objective(self):
        return f"Phase {self.phase + 1}: " + " + ".join([Phase.descript(phs_str) for phs_str in PHASES[self.phase]])

class Game:
    '''Game has Players, Phases, a Pickup, and a Discard'''

    def __init__(self, num_players = ""):
        if not num_players:
            while not num_players.isnumeric() or not ('1' <= num_players <= '4'):
                clear()
                num_players = input("How many players (1-4): ")
        self.new_game(int(num_players))

    def new_game(self, num_players):
        self.players = [Player() for _ in range(num_players)]
        self.pickup = Pickup()
        self.round_phases: list[list[Phase]] = []
        self.turn_num = 0
        self.main_loop()

    def inc_turn(self):
        self.turn_num = (self.turn_num + 1) % len(self.players)

    def deal(self):
        self.pickup.shuffle()
        for _ in range(10):
            for player in self.players:
                player.cards.push(self.pickup.pop())
        self.pickup.discard.clear()
        self.pickup.discard.push(self.pickup.pop())

    def show_table(self, player: Player):
        on_table = [f"Player {player.name}'s Turn - {player.get_objective()}"]
        phases_strs = "\n".join([Phase.str_phases(phase_group) for phase_group in self.round_phases])
        if phases_strs != "":
            on_table.append(phases_strs)
        on_table += [str(self.pickup), str(player.cards)]
        table = '\n'.join(on_table)
        clear()
        print(table)

    def card_from_discard(self, player: Player):
        if self.pickup.discard.is_empty():
            timed_message("Discard is empty. Drawing from Deck...")
            self.card_from_pickup(player)
        else:
            player.cards.push(self.pickup.discard.pop())

    def card_from_pickup(self, player: Player):
        if self.pickup.is_empty():
            timed_message("Pickup is empty. Reshuffling cards from Discard...")
            self.pickup.cards = self.pickup.discard.recycle()
        player.cards.push(self.pickup.pop())

    def draw(self, player: Player):
        '''player draws a card from a pile'''
        while True:
            self.show_table(player)
            choice = input("Draw from Discard (1) or Deck (2): ")
            if choice == "1":
                self.card_from_discard(player)
            elif choice == "2":
                self.card_from_pickup(player)
            else:
                timed_message("Invalid Argument")
                continue
            break

    def drop(self, player: Player):
        '''player drops a card into a pile'''
        while True:
            self.show_table(player)
            card_repr = input("Which card would you like to drop?: ")
            if (index := player.cards.find(card_repr)) != -1:
                card = player.cards.pop(index)
                if card.val == 15:
                    self.inc_turn()
                    timed_message("The next player will be skipped.")
                self.pickup.discard.push(card)
                player.turn_over = True
                break
            else:
                timed_message("Card not found. (ex. g3 is Green 4; w is Wild)")

    def complete_phase(self, player: Player):
        '''Will determine player phases and let them drop into there, if completed those phases will be returned'''
        if player.out:
            timed_message("You have already completed your phase! Try extending another phase.")
            return
        phases = [Phase(phs_str) for phs_str in PHASES[player.phase]]
        incomplete = False
        for phase in phases:
            if not player.do_phase(phase):
                incomplete = True
                break
        if not incomplete: 
            timed_message("Phase Success.")
            player.out = True
            for phase in phases:
                phase.merge()
            self.round_phases.append(phases)
        else:
            timed_message("Phase Failure.")
            for phase in phases:
                phase.return_cards(player.cards)

    def extend_phase(self, player: Player):
        '''Will loop through any phase to extend'''
        if not player.out:
            timed_message("You must first complete your phase to extend another phase.")
            return
        for phase in [phase for phase_group in self.round_phases for phase in phase_group]:
            if player.do_phase(phase):
                print("Phase Success.")
                phase.merge()
            else:
                print("Phase Failure.")
                phase.return_cards(player.cards)

    def game_over(self) -> bool:
        '''Displays round results. Returns True if game is over, returns False otherwise'''
        for player in self.players:
            player.name
        return any([player.phase == len(PHASES) for player in self.players])

    def do_turn(self, player: Player) -> bool:
        '''Walks through player's turn. Returns False if the player has no cards left, otherwise returns True'''
        self.draw(player)
        choices = {'1': lambda: player.sort(),
                   '2': lambda: self.complete_phase(player),
                   '3': lambda: self.extend_phase(player),
                   '4': lambda: self.drop(player)}
        player.turn_over = False
        while not player.turn_over and player.has_cards():
            self.show_table(player)
            user_input = input("Press 1 to Sort | Press 2 to Complete Phase | Press 3 to Extend Phase | Press 4 to Drop a Card")
            choices.get(user_input, lambda: timed_message("Invalid Argument"))()
        self.show_table(player)
        timed_message("Switching Turn" if player.turn_over else "Round Over")
        return player.has_cards()

    def main_loop(self):
        '''starts and maintains the state of the game'''
        while not self.game_over(): # while no player has beaten 10 phases
            self.deal()
            while self.do_turn(self.players[self.turn_num]): # while player still has cards
                self.inc_turn()
            for player in self.players:
                player.consolidate()
            self.round_results()
            input("Press Enter to continue...")
        self.game_results()
        input("Press Enter to continue...")

    def round_results(self):
        '''Prints points of all players and declares a winner'''
        clear()
        for index in range(0, len(self.players)):
            print(f"Player {self.players[index].name}: {self.players[index].points} points")

    def game_results(self):
        '''Prints points of all players and declares a winner'''
        self.round_results()
        self.players.sort(key = lambda player: player.points)
        winner = self.players[0]
        print(f"\nPlayer {winner.name} has won with {winner.points}")
        
if __name__ == "__main__":
    g = Game()