
from os import system, name as os_name
from time import sleep

def clear():
    '''clears the console / terminal'''
    if os_name == "nt":
        system("cls")
    else:
        print("\x1b[2J\x1b[H", end="")

def timed_message(prompt: str, seconds: float = 1.5):
    '''displays specified prompt for a number of seconds'''
    print(prompt)
    sleep(seconds)

def intin(prompt: str, range: tuple[int, int]) -> int:
    '''robust method of receiving integer input from user in specified range'''
    while True:
            user_input = input(prompt)
            if user_input.isdigit():
                user_input = int(user_input)
                if user_input < range[0] or user_input > range[1]:
                    print(f"Out of range {range}. Try again.")
                    continue
                return user_input
            else:
                print("Not a number. Try again: ")