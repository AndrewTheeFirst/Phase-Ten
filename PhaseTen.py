# Andrew Patton
# Phase Ten
# Started Refactoring 2024-11-1
# Further Refactoring 2024-11-2

from constants import Faces, Colors, CARD_RENDERS, PRINT_COLOR, CARD_TOP_BOT, CLEAR
from random import shuffle as _shuffle

class Card:
    '''Represents phaseten phasecards'''
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
    '''Represents a generic stack of cards (superclass)'''
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
        return self.size() == 0
    
    def size(self):
        return len(self.cards)

    def __str__(self):
        '''subclasses will override this method '''
        pass          

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

class Hand(Stack):
    '''Represents a player-owned stack of cards'''
    def __str__(self):
        hand_builder = ""
        num_cards = self.size()
        card_lines = [str(self.cards[index]).split('\n') for index in range(num_cards)]
        card_height = len(card_lines[0])
        for line in range(card_height):
            for card_index in range(num_cards):
                hand_builder += card_lines[card_index][line] + "  "
            hand_builder += '\n'
        return hand_builder
    
    def pop(self):
        while True:
            card_repr = input("Which card would you like to drop?: ")
            for index in range(self.size()):
                current_repr = self.cards[index]._repr
                if card_repr == current_repr:
                    return self.cards.pop(index)
            print("Card not found. (ex. g3 is Green 4; w is Wild)")

    def face_sort(self):
        self.cards = sorted(self.cards, key = lambda card: card.value()) # may modify

    def color_sort(self):
        self.cards = sorted(self.cards, key = lambda card: card.color.value) # may modify

class Phase(Hand):
    def __init__(self):
        super().__init__()
        self.num_cards = 0
        self.num_wilds = 0
        self.has_skip = False    

    def push(self, card: Card):
        super().push(card)
        if card.face == Faces.WILD:
            self.num_wilds += 1
        elif card.face == Faces.SKIP:
            self.has_skip = True
        self.num_cards += 1
    
    def isSet(self, size: int, set_type: str):
        '''Returns true if cards creates a set of specified size and set_type (ie. 'face' or 'color')'''
        if self.num_cards < size:
            return False
        elif set_type == "face": # Goes through all cards except wilds and checks 
            return all([(self.cards[card1_index].face == self.cards[card2_index].face)\
                            for card1_index in range(self.num_cards - 1 - self.num_wilds)\
                            for card2_index in range(card1_index, self.num_cards - self.num_wilds)])\
                            and not self.has_skip
        elif set_type == "color":
            return all([(self.cards[card1_index].color == self.cards[card2_index].color)\
                            for card1_index in range(self.num_cards - 1 - self.num_wilds)\
                            for card2_index in range(card1_index, self.num_cards - self.num_wilds)])\
                            and not self.has_skip
    
    def isRun(self, size: int):
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
    
class Player:
    # Player Has a Phase and a Hand
    def __init__(self):
        self.hand = Hand()
        self.phase = Phase()
        self.out = False
        self.points = 0

if __name__ == "__main__":
    p1 = Phase()
    p1.push(Card(Faces.ONE, Colors.YELLOW))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.FIVE, Colors.RED))
    p1.push(Card(Faces.WILD, Colors.ANY))
    p1.push(Card(Faces.SEVEN, Colors.ANY))
    print(p1.isRun(5))