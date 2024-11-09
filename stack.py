from card import Faces, Colors, Card
from random import shuffle as _shuffle
from controls import timed_message

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
        '''creates new shuffled deck of cards: 4 skips, 8 wilds, 2 sets of numbers 1-12 for each color'''
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
        if self.size() != 0:
            card_lines = [str(card).split('\n') for card in self.cards]
            for line in range(len(card_lines[0])): 
                for card_line in card_lines:
                    hand_builder += card_line[line] + " " # matches the same line for all cards
                hand_builder += '\n'
        return hand_builder.rstrip() + '\n'
    
    def find(self, card_repr: str):
        '''Returns the index of the card in a stack via a card's card_repr. Returns -1 if not found'''
        for index in range(self.size()):
            if card_repr == self.cards[index]._repr:
                return index
        return -1

    def drop(self):
        '''Prompts player to 'safely' drop a card
        '''
        while True:
            card_repr = input("Which card would you like to drop?: ")
            index = self.find(card_repr)
            if index != -1:
                return self.pop(index)
            print("Card not found. (ex. g3 is Green 4; w is Wild)")

    def face_sort(self):
        '''Sorts cards by face'''
        self.cards.sort(key = lambda card: card.val) # may modify

    def color_sort(self):
        '''Sorts cards by color'''
        self.cards = sorted(self.cards, key = lambda card: card.color.value) # may modify

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

    def desc(self):
        '''Returns a human readable description of the Phase contraints
        >>> p1 = Phase("set3")
        >>> p1.desc()
        'A Set of 3'
        >>> p1 = Phase("set3c")
        >>> p1.desc()
        'A Set of 3 Colors'
        '''
        return f"A {self.phase_str[:3].title()} of {self.phase_str[3]} {'Colors' if len(self.phase_str) == 5 else ''}".rstrip()

    def __str__(self):
        hand_builder = ""
        if self.size() + self.unchecked.size() != 0:
            card_lines = [str(card).split('\n') for card in self.cards + self.unchecked.cards]
            for line in range(len(card_lines[0])): 
                for card_line in card_lines:
                    hand_builder += card_line[line] + " " # matches the same line for all cards
                hand_builder = hand_builder.rstrip() + '\n'
        return hand_builder.rstrip() + '\n'

if __name__ == "__main__":
    from doctest import testmod
    testmod()
