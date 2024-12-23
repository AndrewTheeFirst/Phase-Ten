from card import Faces, Colors, Card
from random import shuffle as _shuffle

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
        if self.is_empty():
            return None
        else:
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

    def clear(self):
        '''removes all cards from the stack'''
        self.cards = []    

    def __str__(self) -> str:
        '''string representation of a stack (subclasses may override this method)'''
        return Card.str_cards(self.cards)

class Pickup(Stack):
    '''Pickup is a Stack and has a Discard'''

    class Discard(Stack):
        '''Discard is a Stack'''

        def recycle(self):
            '''keeps only the top card, returns the rest to be reused'''
            rest = self.cards[:-1]
            top = self.pop()
            self.cards = [top]
            _shuffle(rest)
            return rest

    def __init__(self):
        super().__init__()
        self.discard = self.Discard()    

    def shuffle(self):
        '''creates new shuffled deck of cards: 4 skips, 8 wilds, 2 sets of numbers 1-12 for each color'''
        self.cards = [Card(face, color) for face in Faces for color in Colors \
                      if face.value in range(1, 13) and color.value in range(1,5) for _ in range(2)]
        for _ in range(2):
            for _ in range(2):
                self.push(Card(Faces.WILD, Colors.ANY))
            self.push(Card(Faces.SKIP, Colors.NONE))
        _shuffle(self.cards)
    
    def __str__(self):
        '''will print the top of discard and the back of the pickup'''
        pickup_back = BLANK if self.is_empty() else BACK
        discard_front = BLANK if self.discard.is_empty() else self.discard.top()
        return f"{Card.str_cards([discard_front, pickup_back]).rstrip()}\n{'Discard':^11} {'Deck Pl':^11}"

class Hand(Stack):
    '''Represents a player-owned stack of cards'''
    
    def find(self, card_repr: str) -> int:
        '''Returns the index of the card in a stack via a card's card_repr. Returns -1 if not found'''
        for index in range(self.size()):
            if card_repr == self.cards[index]._repr:
                return index
        return -1

    def face_sort(self):
        '''Sorts cards by face'''
        self.cards.sort(key = lambda card: card.val) # may modify

    def color_sort(self):
        '''Sorts cards by color'''
        self.cards.sort(key = lambda card: card.color.value) # may modify

    def sum(self) -> int:
        return sum([card.val for card in self.cards])

class Phase(Stack):
    '''Represents a maintained stack according to phase conditions.'''

    def __init__(self, phase_str: str):
        '''ex phase_str: "set4", "run4", "set4c"'''
        super().__init__()
        self.unchecked = Stack()
        self.phase_str = phase_str
        self.num_skips = 0
    
    def push(self, card: Card):
        '''Pushes unverified card into the unchecked pile'''
        if card.val == 15:
            self.num_skips += 1
        self.unchecked.push(card)

    def pop(self):
        top_card = self.unchecked.pop()
        if top_card.val == 15:
            self.num_skips -= 1
        return top_card
    
    def is_phase(self):
        '''Returns True if cards are of phase_str specified. Returns False otherwise.
        (if returns True .unchecked can be considered verified)
        
        >>> p1 = Phase("set3c")
        >>> p1.push(Card(Faces.ONE, Colors.RED))
        >>> p1.push(Card(Faces.WILD, Colors.ANY))
        >>> p1.push(Card(Faces.TWO, Colors.RED))
        >>> p1.is_phase()
        True

        >>> p1 = Phase("run3")
        >>> p1.push(Card(Faces.ONE, Colors.YELLOW))
        >>> p1.push(Card(Faces.FOUR, Colors.RED))
        >>> p1.push(Card(Faces.WILD, Colors.ANY))
        >>> p1.is_phase()
        False
        '''
        size = int(self.phase_str[3]) 
        if "set" in self.phase_str:
            if self.phase_str[-1] != 'c':
                verified = self.is_set(size, "face")
            else:
                verified = self.is_set(size, "color")
        else:
            verified = self.is_run(size)
        return verified
    
    def merge(self):
        '''Merges .unchecked cards (checked through is_phase()) into the the stack of verified phase cards

        >>> p1 = Phase("set3")
        >>> p1.push(Card(Faces.TWO, Colors.RED))
        >>> p1.push(Card(Faces.WILD, Colors.ANY))
        >>> p1.push(Card(Faces.TWO, Colors.BLUE))
        >>> if p1.is_phase():
        ...    p1.merge()
        >>> p1.cards
        [Card(Faces.TWO, Colors.BLUE), Card(Faces.TWO, Colors.RED), Card(Faces.WILD, Colors.ANY)]
        >>> p1.unchecked.cards
        []

        >>> p1.push(Card(Faces.ONE, Colors.YELLOW))
        >>> if p1.is_phase():
        ...     p1.merge()
        >>> p1.cards
        [Card(Faces.TWO, Colors.BLUE), Card(Faces.TWO, Colors.RED), Card(Faces.WILD, Colors.ANY)]
        >>> p1.unchecked.cards
        [Card(Faces.ONE, Colors.YELLOW)]
        '''
        for _ in range(self.unchecked.size()):
            super().push(self.unchecked.pop())
        self.cards.sort(key = lambda card: card.val)

    def is_set(self, size: int, set_type: str):
        '''Returns true if cards creates a set of specified size and set_type (ie. "face" or "color") otherwise returns False
        >>> p1 = Phase("")
        >>> p1.push(Card(Faces.ONE, Colors.YELLOW))
        >>> p1.push(Card(Faces.WILD, Colors.RED))
        >>> p1.push(Card(Faces.ONE, Colors.BLUE))
        >>> p1.is_set(3, "face")
        True
        >>> p1 = Phase("")
        >>> p1.push(Card(Faces.ONE, Colors.YELLOW))
        >>> p1.push(Card(Faces.ONE, Colors.RED))
        >>> p1.push(Card(Faces.ONE, Colors.BLUE))
        >>> p1.is_set(3, "color")
        False
        '''
        if self.size() + self.unchecked.size()  < size:
            return False
        if set_type == "face":
            return len({card.val for card in self.cards + self.unchecked.cards if card.val != 25}) == 1\
            and self.num_skips == 0
        else:
            return len({card.color_val for card in self.cards + self.unchecked.cards if card.val != 25}) == 1\
            and self.num_skips == 0
    
    def is_run(self, size: int):
        '''Returns true if cards creates a run of specified size otherwise returns False
        >>> p1 = Phase("")
        >>> p1.push(Card(Faces.THREE, Colors.YELLOW))
        >>> p1.push(Card(Faces.FOUR, Colors.RED))
        >>> p1.push(Card(Faces.WILD, Colors.BLUE))
        >>> p1.is_run(3)
        True
        >>> p1 = Phase("")
        >>> p1.push(Card(Faces.ONE, Colors.YELLOW))
        >>> p1.push(Card(Faces.FOUR, Colors.RED))
        >>> p1.push(Card(Faces.WILD, Colors.BLUE))
        >>> p1.is_run(3)
        False
        '''
        if self.size() + self.unchecked.size() < size:
            return False
        card_vals = [card.val for card in self.cards + self.unchecked.cards]
        card_vals.sort()
        num_wilds = card_vals.count(25)
        expected_val = card_vals[0] + 1
        for val_index in range(1, len(card_vals) - num_wilds): # looping over only the cards between the first value and the wilds
            curr_val = card_vals[val_index]
            if curr_val == card_vals[val_index - 1]: # cannot have duplicates
                return False
            else:
                num_wilds -= curr_val - expected_val # difference of exp and curr is the required num of wilds
                expected_val = curr_val + 1
        return num_wilds >= 0 and self.num_skips == 0

    def return_cards(self, stack: Stack):
        for _ in range(self.unchecked.size()):
            stack.push(self.pop())

    @staticmethod
    def descript(phase_str: str) -> str:
        '''Returns a human readable description of the Phase contraints
        >>> Phase.descript("set3")
        'A Set of 3'
        >>> Phase.descript("set3c")
        'A Set of 3 Colors'
        '''
        return f"A {phase_str[:3].title()} of {phase_str[3]} {'Colors' if len(phase_str) == 5 else ''}".rstrip()

    def desc(self):
        '''Returns a human readable description of the Phase contraints
        >>> p1 = Phase("set3")
        >>> p1.desc()
        'A Set of 3'
        >>> p1 = Phase("set3c")
        >>> p1.desc()
        'A Set of 3 Colors'
        '''
        return Phase.descript(self.phase_str)

    @staticmethod
    def str_phases(phases: list["Phase"]): # assumes at least one card in each phase
        if len(phases) == 0:
            return ""
        phases_lines = [str(phase).split('\n') for phase in phases]
        num_phases = len(phases_lines)
        num_lines = len(phases_lines[0])
        return '\n'.join(["    ".join([phases_lines[phase][line_num] 
                                       for phase in range(num_phases)]) 
                                       for line_num in range(num_lines)])

    def __str__(self) -> str:
        return Card.str_cards(self.cards + self.unchecked.cards)

if __name__ == "__main__":
    from doctest import testmod
    testmod()
    h = Phase("")
    h.push(Card(Faces.EIGHT, Colors.BLUE))
    h.push(Card(Faces.SEVEN, Colors.RED))
    h.push(Card(Faces.FOUR, Colors.YELLOW))

    w = Phase("")
    w.push(Card(Faces.EIGHT, Colors.BLUE))
    w.push(Card(Faces.SEVEN, Colors.RED))
    w.push(Card(Faces.FOUR, Colors.YELLOW))
    
    print(Phase.str_phases([w, h]))
