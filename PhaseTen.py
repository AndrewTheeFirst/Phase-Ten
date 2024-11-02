# Andrew Patton
# Phase Ten
# Started Refactoring 2024-11-1
# Further Refactoring 2024-11-2

from constants import *
from random import shuffle as _shuffle


class Card:
    def __init__(self, face: Faces, color: Colors):
        self.face = face
        self.color = color
        self._repr = color.name.lower()[0] + str(face.value) if face not in [Faces.WILD, Faces.SKIP] else face.name.lower()[0]

        
    def __str__(self):
        card = ""
        card += PRINT_COLOR[self.color] + CARD_TOP_BOT + CLEAR + '\n'
        card_render = CARD_RENDERS[self.face].split('\n')
        for card_line in card_render:
            card += PRINT_COLOR[self.color] + card_line[0] + CLEAR +\
                    card_line[1:-1] +\
                    PRINT_COLOR[self.color] + card_line[-1] + CLEAR + '\n'
        card += PRINT_COLOR[self.color] + CARD_TOP_BOT + CLEAR + '\n'
        return card

    def __repr__(self):
        return f"Card({self.face}, {self.color})"

    def value(self) -> int:
        return self.face.value

class Stack:
    '''Represents a stack of cards'''
    def __init__(self):
        self.cards: list[Card] = []

    def push(self, card: Card):
        self.cards.append(card)
    
    def pop(self) -> Card:
        return self.cards.pop()
    
    def top(self) -> Card:
        return self.cards[-1]

    def clear(self):
        self.cards = []

    def is_empty(self):
        return len(self.cards) == 0

    def __str__(self):
        '''subclasses will override this method '''
        pass

class Hand(Stack):
    def __str__(self):
        hand_builder = ""
        card_lines = [str(self.cards[index]).split('\n') for index in range(len(self.cards))]
        card_height = len(card_lines[0])
        num_cards = len(card_lines)
        for line in range(card_height):
            for card in range(num_cards):
                hand_builder += card_lines[card][line] + "  "
            hand_builder += '\n'
        return hand_builder
    
    def pop(self):
        while True:
            card_repr = input("Which card would you like to drop?: ")
            for index in range(len(self.cards)):
                current_repr =  self.cards[index]._repr
                if card_repr == current_repr:
                    return self.cards.pop(index)
            print("Card not found. (ex. g3 is Green 4; w is Wild)")
            

class Discard(Stack):
    '''Discard is a Stack'''
    BLANK = Card(Faces.BLANK, Colors.NONE)

    def recycle(self):
        '''keeps only the top card, returns the rest to be reused'''
        top = self.pop()
        rest = self.cards[:-1]
        self.cards = top
        return _shuffle(rest)
    
    def __str__(self):
        if self.is_empty():
            return str(Discard.BLANK)
        return str(self.top())

class Pickup(Stack):
    '''Pickup is a Stack and has a Discard'''
    BACK = Card(Faces.BACK, Colors.NONE)

    def __init__(self):
        super().__init__()
        self.discard = Discard()
        self.shuffle()

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
            print("Out of cards. Recycling discard pile...")
            self.cards = self.discard.recycle()
        return super().pop()
    
    def __str__(self):
        '''will print the top of discard and the back of the pickup'''
        card_builder = ""
        cards = [str(self.discard).split('\n'),
                        str(Pickup.BACK).split('\n')]
        for index in range(len(cards[0])):
                card_builder += cards[0][index] + "  " + cards[1][index] + '\n'
        return card_builder

class Player:
    # Player Has a Phase and a Hand
    def __init__(self):
        self.out = False
        self.hand = Hand()

class Phase:
    # Phase Template
    def __init__(self):
        pass

if __name__ == "__main__":
    c1 = Card(Faces.WILD, Colors.ANY)
    print(c1._repr)
