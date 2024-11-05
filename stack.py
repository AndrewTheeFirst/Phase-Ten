from card import Faces, Colors, Card
from random import shuffle as _shuffle, seed
from controls import timed_message

# seed(8)
BLANK = Card(Faces.BLANK, Colors.NONE)
BACK = Card(Faces.BACK, Colors.NONE)

class Stack:
    '''Represents a generic stack of cards (superclass)'''
    def __init__(self):
        self.cards: list[Card] = []

    def push(self, card: Card):
        '''Adds the card to the top of the stack'''
        self.cards.append(card)
    
    def pop(self, index = -1) -> Card:
        '''Returns the top card in the stack whilst also removing it from the stack'''
        return self.cards.pop(index)
    
    def top(self) -> Card:
        '''Returns the top card in the stack'''
        return self.cards[-1]

    def is_empty(self):
        '''Returns True if the stack is empty. Returns False otherwise'''
        return self.cards == []
    
    def size(self):
        '''Returns the number of cards in the stack'''
        return len(self.cards)

    def __str__(self):
        '''subclasses will override this method '''
        return ""          

class Discard(Stack):
    '''Discard is a Stack'''

    def recycle(self):
        '''keeps only the top card, returns the rest to be reused'''
        rest = self.cards[:-1]
        top = self.pop()
        self.cards = [top]
        _shuffle(rest)
        return rest
    
    def __str__(self):
        if self.is_empty():
            return str(BLANK)
        return str(self.top())

class Pickup(Stack):
    '''Pickup is a Stack and has a Discard'''

    def __init__(self):
        super().__init__()
        self.discard = Discard()

    def shuffle(self):
        '''creates new shuffled deck of cards'''
        self.cards = [Card(face, color) for face in Faces for color in Colors \
                      if face.value in range(1, 13) and color.value in range(1,5) for _ in range(2)]
        for _ in range(2):
            for _ in range(2):
                self.push(Card(Faces.WILD, Colors.ANY))
            self.push(Card(Faces.SKIP, Colors.NONE))
        _shuffle(self.cards)
    
    def pop(self) -> Card:
        '''returns the top of the deck. If deck is empty, recycles the cards in the discard and reshuffles first'''
        if self.is_empty():
            timed_message("Out of cards. Recycling discard pile...")
            self.cards = self.discard.recycle()
        return super().pop()
    
    def __str__(self):
        '''will print the top of discard and the back of the pickup'''
        card_builder = ""
        pickup_back = BACK
        if self.is_empty():
            pickup_back = BLANK
        cards = [str(stack).split('\n') for stack in [self.discard, pickup_back]]
        for index in range(len(cards[0])):
            card_builder += cards[0][index] + "  " + cards[1][index] + '\n'
        
        return card_builder.rstrip() + '\n' + "Discard".center(11) + "  " + "Pickup".center(11) + '\n'

class Hand(Stack):
    '''Represents a player-owned stack of cards'''
    def __str__(self):
        hand_builder = ""
        num_cards = self.size()
        if num_cards != 0:
            card_lines = [str(self.cards[index]).split('\n') for index in range(num_cards)]
            card_height = len(card_lines[0])
            for line in range(card_height):
                for card_index in range(num_cards):
                    hand_builder += card_lines[card_index][line] + "  "
                hand_builder += '\n'
        return hand_builder
    
    def find(self, card_repr):
        '''Returns the index of the card in a stack via a card's card_repr. Returns -1 if not found'''
        for index in range(self.size()):
            if card_repr == self.cards[index]._repr:
                return index
        return -1

    def drop(self):
        '''Prompts player to 'safely' drop a card'''
        while True:
            card_repr = input("Which card would you like to drop?: ")
            index = self.find(card_repr)
            if index != -1:
                return self.pop(index)
            print("Card not found. (ex. g3 is Green 4; w is Wild)")

    def face_sort(self):
        '''Sorts cards by face'''
        self.cards = sorted(self.cards, key = lambda card: card.value()) # may modify

    def color_sort(self):
        '''Sorts cards by color'''
        self.cards = sorted(self.cards, key = lambda card: card.color.value) # may modify

class Phase(Hand):
    '''Represents a maintained stack according to phase conditions.

    ex phase_str: "set4", "run4", "set4c" '''
    def __init__(self, phase_str: str):
        super().__init__()
        self.phase_str = phase_str
        self.num_cards = 0
        self.num_wilds = 0
        self.has_skip = False
    
    def is_phase(self):
        size = int(self.phase_str[3]) 
        if "set" in self.phase_str:
            if self.phase_str[-1] != 'c':
                return self.is_set(size, "face")
            else:
                return self.is_set(size, "color")
        return self.is_run(size)

    def push(self, card: Card):
        '''Pushes a card onto stack while keeping track of phase state'''
        super().push(card)
        if card.face == Faces.WILD:
            self.num_wilds += 1
        elif card.face == Faces.SKIP:
            self.has_skip = True
        self.num_cards += 1

    def put(self, cards: list[Card]):
        '''Pushes a list of cards via .push()'''
        for card in cards:
            self.push(card)

    def copy(self):
        '''Returns a copy of Phase object (maintained state)'''
        temp_phase = Phase(self.phase_str)
        temp_phase.put(self.cards)
        return temp_phase

    def is_set(self, size: int, set_type: str):
        '''Returns true if cards creates a set of specified size and set_type (ie. "face" or "color") otherwise returns False'''
        self.face_sort()
        if self.num_cards < size:
            return False
        elif set_type == "face": # Goes through all cards except wilds 
            return all([(self.cards[card1_index].face == self.cards[card2_index].face)\
                            for card1_index in range(self.num_cards - 1 - self.num_wilds)\
                            for card2_index in range(card1_index, self.num_cards - 1 - self.num_wilds)])\
                            and not self.has_skip
        elif set_type == "color":
            return all([(self.cards[card1_index].color == self.cards[card2_index].color)
                            for card1_index in range(self.num_cards - 1 - self.num_wilds)\
                            for card2_index in range(card1_index, self.num_cards - 1 - self.num_wilds)])\
                            and not self.has_skip
        return False
    
    def is_run(self, size: int):
        '''Returns true if cards creates a run of specified size otherwise returns False'''
        self.face_sort()
        num_wilds = self.num_wilds
        if self.num_cards < size:
            return False
        card_values = [card.value() for card in self.cards]
        last_value, expected_value = card_values[0], card_values[0] + 1
        for card_index in range(1, self.num_cards - num_wilds): # Goes through all cards except wilds
            curr_value = card_values[card_index]
            if last_value == curr_value: # cannot have duplicates
                return False
            elif expected_value != curr_value:
                num_wilds -= curr_value - expected_value # calculates the number of cards missing from inbetween
            last_value, expected_value = curr_value, curr_value + 1
        return num_wilds >= 0 and not self.has_skip

    def reset(self):
        '''Resets all fields of the Phase instance'''
        self.num_cards = 0
        self.num_wilds = 0
        self.has_skip = False
        self.cards = []

    def desc(self):
        '''Returns a human readable description of the Phase contraints'''
        return f"A {self.phase_str[:3].title()} of {self.phase_str[3]} {'Colors' if len(self.phase_str) == 5 else ''}"

if __name__ == "__main__":
    p1 = Phase("run5")
    p1.push(Card(Faces.ONE, Colors.YELLOW))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.FIVE, Colors.GREEN))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.SIX, Colors.YELLOW))
    print(p1.is_phase())
    print(p1)
