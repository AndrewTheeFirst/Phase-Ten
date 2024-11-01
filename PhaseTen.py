from functools import partial
from random import shuffle
from enum import Enum

def removeElements(elements: list, elementsToRemove: list):
    for elem in elementsToRemove:
        elements.remove(elem)
    return elements

class PlayerTypes(Enum):
    PLAYER = 1
    PICKUP = 2
    PHASE = 3

class Colors(Enum):
    RED = 0
    BLUE = 1
    YELLOW = 2
    GREEN = 3
    NONE = 4
    UNKNOWN = 5
    ANY = 6

class Faces(Enum):
    BLANK = -1
    BACK = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    ELEVEN = 11
    TWELVE = 12
    SKIP = 15
    WILD = 25

class Phases(Enum):
    FlexSet: 1
    FlexRun: 2

SPECIAL_COLORS = {Colors.ANY, Colors.NONE, Colors.UNKNOWN}
SPECIAL_FACES = {Faces.SKIP, Faces.WILD, Faces.BACK, Faces.BLANK}

CARD_RENDERS = {Faces.ONE: '\n+---------+\n|    +    |\n|    |    |\n|    |    |\n|    |    |\n|    +    |\n+---------+',
               Faces.TWO: '\n+---------+\n|  ----+  |\n|      |  |\n|  +---+  |\n|  |      |\n|  +----  |\n+---------+',
               Faces.THREE: '\n+---------+\n|  ----+  |\n|      |  |\n|  ----+  |\n|      |  |\n|  ----+  |\n+---------+',
               Faces.FOUR: '\n+---------+\n|  +   +  |\n|  |   |  |\n|  +---+  |\n|      |  |\n|      +  |\n+---------+',
               Faces.FIVE: '\n+---------+\n|  +----  |\n|  |      |\n|  +---+  |\n|      |  |\n|  ----+  |\n+---------+',
               Faces.SIX: '\n+---------+\n|  +----  |\n|  |      |\n|  +---+  |\n|  |   |  |\n|  +---+  |\n+---------+',
               Faces.SEVEN: '\n+---------+\n|  +---+  |\n|  |   |  |\n|      +  |\n|      |  |\n|      +  |\n+---------+',
               Faces.EIGHT: '\n+---------+\n|  +---+  |\n|  |   |  |\n|  +---+  |\n|  |   |  |\n|  +---+  |\n+---------+',
               Faces.NINE: '\n+---------+\n|  +---+  |\n|  |   |  |\n|  +---+  |\n|      |  |\n|      +  |\n+---------+',
               Faces.TEN: '\n+---------+\n| + +---+ |\n| | |   | |\n| | |   | |\n| | |   | |\n| + +---+ |\n+---------+',
               Faces.ELEVEN: '\n+---------+\n|  +   +  |\n|  |   |  |\n|  |   |  |\n|  |   |  |\n|  +   +  |\n+---------+',
               Faces.TWELVE: '\n+---------+\n| + ----+ |\n| |     | |\n| | ----+ |\n| | |     |\n| + +---- |\n+---------+',
               Faces.SKIP: '\n+---------+\n|         |\n|         |\n| S K I P |\n|         |\n|         |\n+---------+',
               Faces.WILD: '\n+---------+\n|         |\n|         |\n| W I L D |\n|         |\n|         |\n+---------+',
               Faces.BACK: '\n+---------+\n|  P      |\n|   H     |\n|    A    |\n|     S   |\n|      E  |\n+---------+',
               Faces.BLANK: '\n+---------+\n|         |\n|         |\n|         |\n|         |\n|         |\n+---------+'}

class PhaseCard:

    def __init__(self, color: Colors, face: Faces):
        self.color = color
        self.face = face

    def _returnFaceValue(card: 'PhaseCard'):
        return card.face.value
    
    def _colorSort(hand: list['PhaseCard'], primaryCard: 'PhaseCard'):
        '''solely used as a sorting key'''
        if primaryCard == None:
            return 0
        count = 1
        for card in hand:
            if (primaryCard.color == card.color) and (primaryCard != card):
                count += 1
        return count + (1 - (primaryCard.color.value / 10)) #helps order sort
    
    def __eq__(self, other: object):
        return True if repr(self) == repr(other) else False

    def __str__(self):
            return f'{CARD_RENDERS[self.face]}\n{self.color.name.center(11)}\n'
    
    def __repr__(self):
        return f'({self.color}, {self.face})'
    
    def copy(self):
        return PhaseCard(self.color, self.face)
    
class Player:
    numPlayers = 0

    def __init__(self, hand: list[PhaseCard], playerType: PlayerTypes = PlayerTypes.PLAYER, phase = 1):
        if playerType == PlayerTypes.PLAYER:
            Player.numPlayers += 1
            self.playerNum = Player.numPlayers
            self.phase = phase
            self.phaseComplete = False
        if playerType == PlayerTypes.PHASE:
            self.phase = phase
            self.header = PhaseTen.phaseHeader(phase)
        self.hand = hand
        self.playerType = playerType

    def resetPlayers():
        Player.numPlayers = 0

    def _sortHand(self):
        print(self)
        while True:
            userInput = input('Would you like to sort hand? (y/n): ')
            if userInput == 'y' or userInput == 'n':
                break
            else:
                print('Bad Input')
        if userInput == 'n':
            return
        while True:
            userInput = int(input('Sort by Face(1), or Color(2): '))
            if userInput == 1 or userInput == 2:
                break
            else:
                print('Bad Input')

        if userInput == 1:
            self.hand = sorted(self.hand, key=PhaseCard._returnFaceValue)
        elif userInput == 2:
            colorSortKey = partial(PhaseCard._colorSort, self.hand)
            self.hand = sorted(self.hand, key=colorSortKey, reverse=True)
        print(self)

    def Turn(self, game: 'PhaseTen'):
        '''goes through a player's turn picking up and discarding a card'''
        self._sortHand(); print(game)

        playerChoice = int(input('Draw from Discard(1) or from Deck(2): '))


        if playerChoice == 1:
            discardTopCard = game.discard.pop(len(game.discard) - 1)
            self.hand.append(discardTopCard)
        elif playerChoice == 2:
            deckTopCard = game.deck.pop(len(game.deck) - 1)   #player picks card from discard pile or deck
            self.hand.append(deckTopCard)
        
        print(self, game)
        if not self.phaseComplete:
            PhaseTen.phaseRequirment(self) #can player complete phase?
            print(self)
        else:
            for phase in Phase.completePhases: #can you put anycards into complete phases?
                if Phase.completePhases[phase]:
                    for decks in Phase.completePhases[phase]:
                        for deck in decks:
                            print(Player(deck, PlayerTypes.PHASE, phase))
                        print('---------------------------------------------------------------')

        #TO DO: END ROUND IF HAND EMPTY

        numCards = len(self.hand)

        playerChoice = int(input(f'Which card would you like to drop? (1{"-" + str(numCards) if numCards > 1 else ""}): '))

        #TO DO: END ROUND IF HAND EMPTY

        game.discard.append(self.hand.pop(playerChoice - 1)) 
        
        print(self, game) #drops players card into discard pile

    def __str__(self):
        '''Displays a player's hand of cards'''
        Handlines = [str(card).split('\n') for card in self.hand]
        cards, renderLength = len(Handlines), len(Handlines[0])
        if self.playerType == PlayerTypes.PLAYER:
            playerHand = f'(Player {self.playerNum})'
        elif self.playerType == PlayerTypes.PICKUP:
            playerHand = f''
        elif self.playerType == PlayerTypes.PHASE:
            playerHand = f''

        for line in range(renderLength):
            for card in range(cards):
                playerHand += f'{Handlines[card][line]} '
            playerHand += '\n'
        return playerHand

    def __repr__(self):
        return f'Player({self.hand}, {self.playerType})'
    
    def copy(self, playerType = PlayerTypes.PLAYER):
        return Player(self.hand.copy(), playerType)

class PhaseTen:

    def __init__(self, numPlayers: int = 4, discard: list[PhaseCard] = [PhaseCard(Colors.NONE, Faces.BLANK)]):

        self.numPlayers = numPlayers
        self.discard = discard
        self.deck = PhaseTen._shuffleDeck()

    def _shuffleDeck():
        deck = []
        for _ in range(2):
            for face in Faces:
                if face in SPECIAL_FACES:
                    continue
                else:
                    for color in Colors:
                        if color in SPECIAL_COLORS:
                            continue
                        else:
                            deck.append(PhaseCard(color, face))
            for rep in range(4):
                if rep % 2 == 0:
                    deck.append(PhaseCard(Colors.NONE, Faces.SKIP))
                deck.append(PhaseCard(Colors.ANY, Faces.WILD))
        shuffle(deck)

        return deck

    def deal(self):
        hands = []
        for _ in range(self.numPlayers):
            hand = []
            for _ in range(10):
                hand.append(self.deck.pop(0))
            hands.append(hand)
        self.discard.append(self.deck.pop(0))
        return hands

    def phaseRequirment(player: Player = None):
        userInput = input('Complete Phase? (y/n): ')
        
        if userInput == 'y':
            match player.phase:
                case 1:
                    Phase.one(player)
                case 2:
                    Phase.two(player)
                case 3:
                    Phase.three(player)
                case 4:
                    Phase.four(player)
                case 5:
                    Phase.five(player)
                case 6:
                    Phase.six(player)
                case 7:
                    Phase.seven(player)
                case 8:
                    Phase.eight(player)
                case 9:
                    Phase.nine(player)
                case 10:
                    Phase.ten(player)
        else:
            return

    def phaseHeader(phase):
        match (phase):
            case 1:
                return 'Phase 1: 2 sets of 3'
            case 2:
                return 'Phase 2: 1 set of 3 + 1 run of 4'
            case 3:
                return 'Phase 3: 1 set of 4 + 1 run of 4'
            case 4:
                return 'Phase 4: 1 run of 7'
            case 5:
                return 'Phase 5: 1 run of 8'
            case 6:
                return 'Phase 6: 1 run of 9'
            case 7:
                return 'Phase 7: 2 sets of 4'
            case 8:
                return 'Phase 8: 7 cards of one color'
            case 9:
                return 'Phase 9: 1 set of 5 + 1 set of 2'
            case 10:
                return 'Phase 10: 1 set of 5 + 1 set of 3'

    def __str__(self):
        '''displays top of discard pile and top of deck'''
        topCard = len(self.discard) - 1
        return str(Player([self.discard[topCard], PhaseCard(Colors.UNKNOWN, Faces.BACK)], PlayerTypes.PICKUP))
    
class Phase(Player):
    completePhases: dict[int, list[PhaseCard]] = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[]}
    
    def __init__(self):
        pass

    def _isIncreasingModified(numbers: list):
        #assume a sorted list
        nextNumber = numbers[0]; numbers.pop(0)
        previousNumber = None
        numWilds = 0

        for number in numbers:
            match (number):
                case 25:
                    numWilds += 1
                    numbers.remove(25)
                case 15:
                    return False #if skip is present
        
        for number in numbers:
            if number == previousNumber:
                return False #if there are duplicates
            nextNumber += 1
            if (not number == nextNumber):
                numbersMissing = number - nextNumber
                numWilds -= numbersMissing
                nextNumber += numbersMissing
            
        return numWilds >= 0 #if wilds to spare
    
    def isRun(cards: list[PhaseCard], size = 0):
        if len(cards) < size:
            print(f'Is not a run{" of " + str(size) if size != 0 else ""}')
            return False
         
        cards = sorted(cards, key=PhaseCard._returnFaceValue)
        temp = [card.face.value for card in cards]
        isIncreasing = Phase._isIncreasingModified(temp)
        if not isIncreasing:
            print(f'Is not a run{" of " + str(size) if size != 0 else ""}')

        return isIncreasing

    def isSet(cards: list[PhaseCard], size = 0, setType: Enum = Faces):
        if len(cards) < size:
            print(f'Is not a set{" of " + {size} if size != 0 else ""}')
            return False
        if all(card.face == Faces.WILD for card in cards):
            return True
        for primaryCard in cards:
            for secondaryCard in cards:
                if (secondaryCard == primaryCard) or (primaryCard.face == Faces.WILD):
                    continue
                if setType == Faces:
                    if (primaryCard.face != secondaryCard.face) and (secondaryCard.face != Faces.WILD):
                        print(f'Is not a set{" of " + str(size) if size != 0 else ""}')
                        return False
                elif setType == Colors:
                    if (primaryCard.color != secondaryCard.color) and (secondaryCard.color != Colors.ANY):
                        print(f'\nIs not a set{" of " + str(size) if size != 0 else ""}')
                        return False
        return True
    
    def flexSet(tempPlayer: Player, setSize: int = 3, setType: Enum = Faces):
        print(tempPlayer)
        print(f'\nCreate a set of {setSize} {setType}')
        cardsChosen = Phase.getCards(tempPlayer)
        print(Player(cardsChosen, PlayerTypes.PHASE)) #checks and displays chosen cards
        if not Phase.isSet(cardsChosen, setSize, setType):
            return []
        removeElements(tempPlayer.hand, cardsChosen)
        return cardsChosen

    def flexRun(tempPlayer: Player, runSize: 7):
        print(tempPlayer)
        print(f'\nCreate a run of {runSize}')
        cardsChosen = Phase.getCards(tempPlayer)
        print(Player(cardsChosen, PlayerTypes.PHASE)) #checks and displays chosen cards
        
        if not Phase.isRun(cardsChosen, runSize):
            return []
        removeElements(tempPlayer.hand, cardsChosen)
        return cardsChosen

    def getCards(player: Player):
        numCards = len(player.hand)
        cardIndices = (input(f'Which cards would you like to drop? (1{"-" + str(numCards) if numCards > 1 else ""})\
                                \n(seperate each card number with a space) :')).split()
        cardIndices = [int(index) - 1 for index in cardIndices]
        return [player.hand[index] for index in cardIndices]

    def one(player: Player = None):
        if player == None:
            return 'SET'
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer)
        if tempPhase0:
            tempPhase1 = Phase.flexSet(tempPlayer)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases[player.phase] += [[tempPhase0, tempPhase1]]
                    return True
        return False  

    def two(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer)
        if tempPhase0:
            tempPhase1 = Phase.flexRun(tempPlayer, 4)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases += [tempPhase0, tempPhase1]

    def three(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer, 4)
        if tempPhase0:
            tempPhase1 = Phase.flexRun(tempPlayer, 4)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases += [tempPhase0, tempPhase1]

    def four(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexRun(tempPlayer)
        if tempPhase0:
                player.hand = tempPlayer.hand
                player.phaseComplete = True
                Phase.completePhases += [tempPhase0]

    def five(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexRun(tempPlayer, 8)
        if tempPhase0:
                player.hand = tempPlayer.hand
                player.phaseComplete = True
                Phase.completePhases += [tempPhase0]

    def six(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexRun(tempPlayer, 9)
        if tempPhase0:
                player.hand = tempPlayer.hand
                player.phaseComplete = True
                Phase.completePhases += [tempPhase0]

    def seven(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer, 4)
        if tempPhase0:
            tempPhase1 = Phase.flexSet(tempPlayer, 4)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases += [tempPhase0, tempPhase1]

    def eight(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer, 7, Colors)
        if tempPhase0:
                player.hand = tempPlayer.hand
                player.phaseComplete = True
                Phase.completePhases += [tempPhase0]

    def nine(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer, 5)
        if tempPhase0:
            tempPhase1 = Phase.flexSet(tempPlayer, 2)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases += [tempPhase0, tempPhase1]

    def ten(player: Player):
        tempPlayer = player.copy(PlayerTypes.PHASE)
        tempPhase0 = Phase.flexSet(tempPlayer, 5)
        if tempPhase0:
            tempPhase1 = Phase.flexSet(tempPlayer, 3)
            if tempPhase1:
                    player.hand = tempPlayer.hand
                    player.phaseComplete = True
                    Phase.completePhases += [tempPhase0, tempPhase1]
  


