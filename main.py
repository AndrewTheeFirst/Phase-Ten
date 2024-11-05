# Andrew Patton
# Phase Ten
# 2024-11-1 Began refactoring - Created new class structure
# 2024-11-2 Further refactoring - Expanded on stack subclass methods as well as stack class)
# 2024-11-3 Worked on Phase class methods and Hand sorting
# 2024-11-4 Implemented Phases and Phase completion, better printing, and skipping
# 2024-11-5 

from stack import Pickup, Phase, Hand
from controls import intin, clear, timed_message
from itertools import cycle

PHASES = [["HI"],
          ["set3", "set3"],
          ["set3", "run4"],
          ["set4", "run4"],
          ["run7"],
          ["run8"],
          ["run9"],
          ["set4", "set4"],
          ["set7c"],
          ["set5", "set2"],
          ["set5", "set3"],
          ["BYE"]]

class Player:
    '''Player has a Hand'''
    count = 1
    def __init__(self):
        self.hand = Hand()
        self.phase = 0
        self.phases: list[Phase] = []
        self.next_phase()
        self.out = False
        self.points = 0
        self.name = Player.count
        Player.count += 1


    def has_cards(self):
        return not self.hand.is_empty()
    
    def next_phase(self):
        self.phase += 1
        if self.phase < 11:
            self.phases = [Phase(phase_str) for phase_str in PHASES[self.phase]]
    
    def complete_phase(self):
        while True:
            if intin("Complete Phase? yes(1), no(2): ", (1, 2)) == 1:
                for phase_index in range(len(self.phases)):
                    phase = self.phases[phase_index]
                    while True:
                        clear()
                        print(f"Phase {self.phase} - Condition {phase_index}: {phase.desc()}")
                        print(phase)
                        print(self.hand)
                        choice = input("Which card would you like to drop? (type F to finish) ")
                        if choice.upper() == "F":
                            break
                        card_index = self.hand.find(choice)
                        if card_index == -1:
                            timed_message("Card not found. (ex. g3 is Green 4; w is Wild)")
                        else:
                            phase.push(self.hand.pop(card_index))
                if all([phase.is_phase() for phase in self.phases]): # phases are complete
                    self.out = True
                    break
                else: # phases are not complete
                    timed_message("Phases Incomplete. Returning cards...")
                    for phase in self.phases:
                        for _ in range(phase.size()):
                            self.hand.push(phase.pop())
            else:
                break
        return self.out

class Game:
    '''Game has Players, Phases, a Pickup, and a Discard'''
    def __init__(self, num_players = None):
        if not num_players:
            num_players = intin("How many players (2-6): ", (2, 6))
        self.players = [Player() for _ in range(num_players)]
        self.deck = Pickup()
        self.discard = self.deck.discard
        self.player_phases: list[list[Phase]] = []
        self.game_running = True
        self.turn = None
    
    def deal(self):
        for _ in range(10):
            for player in self.players:
                player.hand.push(self.deck.pop())
        self.discard.push(self.deck.pop())

    def show_results(self):
        self.players.sort(key = lambda player: player.phase)
        for index in range(1, len(self.players) + 1):
            print(f"Player {self.players[index].name}: {self.players[index].points} points")
        winner = self.players[0]
        print(f"\nPlayer {winner.name} has won with {winner.points}")

    def print_phases(self):
        master_str = ""
        for phases_index in range(len(self.player_phases)):
            player_phase =  self.player_phases[phases_index]
            phase_strings = [str(player_phase[index]).split('\n') for index in range(len(player_phase))]
            for line_index in range(len(phase_strings[0])):
                for index in range(len(phase_strings)):
                    master_str += phase_strings[index][line_index] + "     "
                master_str = master_str.rstrip() + '\n'
        print(master_str)

    def show_table(self, curr_player: Player):
        '''shows the current players hand, pickup, discard, and complete phases'''
        clear()
        print(f"Player {curr_player.name}'s Turn")
        self.print_phases()
        print(self.deck)
        print(curr_player.hand)

    def player_turn(self, player: Player):
        '''sets and walks through players turn'''
        self.show_table(player)
        choice = 3
        while choice == 3: # player pickup a card
            choice = intin("Draw from Discard(1), from Pickup(2), or Sort(3): ", (1, 3))
            if choice == 1:
                if self.discard.top().value() == 15: # checks for skip
                    timed_message("Cannot draw SKIPS from discard. Drawing from Deck...")
                    player.hand.push(self.deck.pop())
                else:
                    player.hand.push(self.discard.pop())
            elif choice == 2:
                player.hand.push(self.deck.pop())
            else:
                if intin("Would you like to sort by Face(1) or Color(2): ", (1, 2)) == 1:
                    player.hand.face_sort()
                else:
                    player.hand.color_sort()
            self.show_table(player)

        if not player.out: # does not ask players who are already out to complete phase
            if player.complete_phase():
                timed_message("Phase Complete! ...")
                self.player_phases += [player.phases] # adds to game's global phases to print

        # TODO If player out, allow phase addons
        
        if not player.has_cards():
            print("Round over!")
            return True
        
        self.show_table(player)
        card = player.hand.drop()
        if card.value() == 15:
            next(self.turn)
            timed_message("Next player will be skipped...")
        self.discard.push(card) # Player puts down a card

        if not player.has_cards():
            print("Round over!")
            return True
        self.show_table(player)
        input('press any key to end your turn...')
        clear()
        return False

    def mainloop(self):
        '''starts and maintains the state of the game'''
        clear()
        self.turn = cycle(self.players)
        game_running = True
        while game_running:
            self.deal()
            while not self.player_turn(next(self.turn)):
                input('enter any key to continue...\n')
            for player in self.players: # round ends
                for _ in range(player.hand.size()):
                    player.points += player.hand.pop().value() # clears hand and adds points
                if player.out:
                    player.next_phase()
                player.out = False
                if player.phase == 11:
                    game_running = False
                    break
            self.player_phases = []
        
if __name__ == "__main__":
    g = Game(2)
    g.mainloop()
                