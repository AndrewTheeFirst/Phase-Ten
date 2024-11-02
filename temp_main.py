from temp import *
from os import system

#Deals cards to players and puts them in a list

numPlayers = int(input('How many players (2-6): '))
print()

myGame = PhaseTen(numPlayers)

playerList = [Player(hand) for hand in myGame.deal()] 

#access player objects via playerList

while True:
    for player in playerList:
        player.Turn(myGame)
        input('press any key to end your turn...')
        system('cls')                             #wipes screen so players have privacy 
        input('enter any key to continue...\n') 


while True:
        player.Turn(myGame)
        input('press any key to end your turn...')
        system('cls')                             #wipes screen so players have privacy 
        input('enter any key to continue...\n') 


