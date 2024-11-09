# Andrew Patton
# Phase Ten
# 2024-11-1 Began refactoring - Created new class structure
# 2024-11-2 Further refactoring - Expanded on stack subclass methods as well as stack class)
# 2024-11-3 Worked on Phase class methods and Hand sorting
# 2024-11-4 Implemented Phases and Phase completion, better printing, and skipping
# 2024-11-5 Implemented Phase addition - Production
# 2024-11-8 Phase class rework (Stack, verification, merge, etc.) misc. tweaks

# after returning cards, screen doesnt refresh, show player hand, then ask to 'complete phase?'
# only returning cards from failed phase, not all cards


from stack import Pickup, Phase, Hand
from controls import intin, clear, timed_message
from itertools import cycle

def print_phase_group(phase_group: list[Phase]):
    '''Prints a phase group'''
    master_str = ""
    phase_strings = [str(phase).split('\n') for phase in phase_group]
    for line in range(len(phase_strings[0])):
        for phase in phase_strings:
            master_str += phase[line] + "    "
        master_str = master_str.rstrip() + '\n'
    print(master_str)

def phase_objectives(phases: list[Phase]):
    '''Returns a comma-space seperated string of phase descriptions'''
    master_str = ""
    for phase in phases:
        master_str += phase.desc() + " + "
    return master_str[:-3]

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
          ["set5", "set3"]]

class Player:
    '''Player has a Hand and Phases'''
    count = 1
    def __init__(self):
        self.hand = Hand()
        self.phase_num = 0
        self.phases: list[Phase] = []
        self.next_phase()
        self.out = False
        self.points = 0
        self.name = Player.count
        Player.count += 1

    def show_area(self, phase: Phase, condition: int = -1):
        clear()
        print(phase.desc() if condition == -1 else f"Phase {self.phase_num} - Condition {condition + 1}: {phase.desc()}")
        print(phase)
        print(self.hand)

    def has_cards(self) -> bool:
        '''Returns True if a player has any cards, returns False otherwise'''
        return not self.hand.is_empty()
    
    def next_phase(self):
        '''Increments a player's phase, and instantiates Phase based on player's phase'''
        num_phases = len(PHASES) - 1
        if self.phase_num != -1:
            if self.phase_num == num_phases:
                self.phase_num = -1 # marks player as done
            else:
                self.phase_num += 1
                self.phases = [Phase(phase_str) for phase_str in PHASES[self.phase_num]]
    
    def complete_phase(self) -> bool:
        '''Player attempts to complete phase. Returns True if player completed phase, otherwise returns False'''
        while intin("Complete Phase? yes(1), no(2): ", (1, 2)) == 1:
            for condition in range(len(self.phases)):
                phase = self.phases[condition]
                while True:
                    self.show_area(phase, condition)
                    choice = input("Which card would you like to drop? (type F to finish) ")
                    if choice.upper() == "F":
                        break
                    card_index = self.hand.find(choice)
                    if card_index == -1:
                        timed_message("Card not found. (ex. g3 is Green 4; w is Wild)", 1)
                    else:
                        phase.push(self.hand.pop(card_index))
            if all([phase.is_phase() for phase in self.phases]): # phases are complete
                for phase in self.phases:
                    phase.merge()
                self.out = True
                break
            else: # phases are not complete
                timed_message("Phases Incomplete. Returning cards...")
                for phase in self.phases:
                    for _ in range(phase.unchecked.size()):
                        self.hand.push(phase.pop())
                clear()
                print(self.hand)
        return self.out

class Game:
    '''Game has Players, Phases, a Pickup, and a Discard'''
    def __init__(self, num_players = None):
        if not num_players:
            num_players = intin("How many players (2-4): ", (2, 4))
        self.players = [Player() for _ in range(num_players)]
        self.deck = Pickup()
        self.discard = self.deck.discard
        self.player_phases: list[list[Phase]] = []
        self.game_running = True
        self.turn = None
    
    def deal(self):
        '''Resets deck and discard and deals 10 cards to each player'''
        self.deck.shuffle()
        for _ in range(10):
            for player in self.players:
                player.hand.push(self.deck.pop())
        self.discard.cards = []
        self.discard.push(self.deck.pop())

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

    def show_table(self, curr_player: Player):
        '''shows the current players hand, pickup, discard, and complete phases'''
        clear()
        print(f"Player {curr_player.name}'s Turn - Phase {curr_player.phase_num}: {phase_objectives(curr_player.phases) if not curr_player.out else 'Completed!'}")
        for phase in self.player_phases:
            print_phase_group(phase)
        print(self.deck)
        print(curr_player.hand)
                               
    def add_to_phase(self, player: Player):
        '''Player gets chance to add more cards to other player's phases'''
        for phase_group in self.player_phases:
            for phase in phase_group:
                player.show_area(phase)
                while intin("Add to this Phase? yes(1), no(2): ", (1, 2)) == 1:
                    while True: # while player still adding cards
                        clear()
                        print(phase)
                        print(player.hand)
                        choice = input("Which card would you like to drop? (type F to finish) ")
                        if choice.upper() == "F":
                            break
                        card_index = player.hand.find(choice)
                        if card_index == -1:
                            timed_message("Card not found. (ex. g3 is Green 4; w is Wild)")
                        else:
                            phase.push(player.hand.pop(card_index))
                    if phase.is_phase():
                        phase.merge()
                        timed_message("Phase addition: Success.")
                    else:
                        timed_message("Phase addition: Failure. Returning cards...")
                        for _ in range(phase.unchecked.size()):
                            player.hand.push(phase.pop())
                    player.show_area(phase)

    def player_turn(self, player: Player) -> bool:
        '''Sets and walks through players turn. Returns True if player is out of cards, otherwise, returns False'''
        choice = 3
        while choice == 3: # player pickup a card
            self.show_table(player)
            choice = intin("Draw from Discard(1), from Pickup(2), or Sort(3): ", (1, 3))
            if choice == 1:
                if self.discard.top().val == 15: # checks for skip
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
                self.player_phases += [player.phases] # adds to game's phases to print

        self.show_table(player)
        if player.out: # players who are out are now able to add to other game phases
            if intin("Add to an existing Phase? Yes(1), No(2): ", (1, 2)) == 1:
                self.add_to_phase(player)
        
        if not player.has_cards():
            return True
        
        self.show_table(player)
        card = player.hand.drop()
        if card.val == 15:
            next(self.turn)
            timed_message("Next player will be skipped...")
        self.discard.push(card) # Player puts down a card

        if not player.has_cards():
            return True
        
        self.show_table(player)
        input('press any key to end your turn...')
        clear()
        return False

    def mainloop(self):
        '''starts and maintains the state of the game'''
        clear()
        self.turn = cycle(self.players)
        while all([player.phase_num != -1 for player in self.players]): # begins next round if any player is not done with all phases
            self.deal()
            self.turn = cycle([player for player in self.players if player.phase_num != -1])
            while not self.player_turn(next(self.turn)): # will loop through player turns until a player is out of cards
                input('enter any key to continue...\n')
            timed_message("Round over!")
            self.end_round()
            self.round_results()
            input('enter any key to continue...\n')
        self.game_results()
    
    def end_round(self):
        '''Resets and increments all the necessary fields to prepare for the next round'''
        for player in self.players: # round ends
            for _ in range(player.hand.size()):
                player.points += player.hand.pop().val # clears hand and adds points
            if player.out:
                player.next_phase()
            player.out = False
        self.player_phases = []

if __name__ == "__main__":
    g = Game(2)
    g.mainloop()