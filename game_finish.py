from helpers import *
import time
from main import GameEnvironment
from playsound import playsound
import main


##############################
#  All the ways you die
##############################
def you_lose_food(env):
    steady_print(f"You run out of food and starve to death.\n")
    you_lose(env)


def you_lose_sick(env, medical=False):
    env.wallet = 0
    if medical:
        steady_print("You have run out of all medical supplies.\n")
    else:
        steady_print(f"You need a doctor badly, but can't afford one.\n")
    steady_print(f"The wilderness is unforgiving and you die of {'Covid-19' if env.sick else 'your injuries'}.\n")
    you_lose_sick2(env)


def you_lose_sick2(env):
    steady_print(f"Your family tries to push on, but finds the going too rough without you.\n")
    you_lose(env)


def you_lose_time(env):
    steady_print("Your oxen are worn out and can't go another step. You try pushing\n"
                 "ahead on foot, but it is snowing heavily and everyone is exhausted.\n")
    time.sleep(3)
    steady_print("You stumble and can't get up....\n")
    you_lose(env)


def you_lose(env):
    time.sleep(2)
    steady_print("Some travelers find the bodies of you and your\n"
                 "family the following spring. They give you a decent\n"
                 "burial and notify your next of kin.\n")
    travelled = env.days_travelled()
    steady_print(f"At the time of your unfortunate demise, you had been on the trail\n"
                 f"for {travelled['months']} months and {travelled['days']} days and had covered "
                 f"{env.mileage + 70} miles.\n"
                 f"You have few supplies remaining :\n")
    env.print_inventory()
    play_again()


########################
# The only way you win
#########################
def you_win(env: GameEnvironment):
    # Set ML? 3200
    playsound('sounds/victory.wav')
    env.end_miles = (2040 - env.prior_mileage) / (env.mileage - env.prior_mileage)
    env.food += (1 - env.mileage) * (8 + 5 * env.eating)
    travelled = env.days_travelled()
    steady_print(f"You finally arrived at Oregon City after 2040 long miles.\n"
                 f"You're exhausted and haggard, but you made it! A real pioneer!\n"
                 f"You've been on the trail for {travelled['months']} months and {travelled['days']} days\n"
                 f"You have few supplies remaining :\n")
    env.print_inventory()
    steady_print("President James A. Polk sends you his heartiest\n"
                 "congratulations and wishes you a prosperous life in your new home.\n")
    play_again()


def play_again():
    response = input("Would you like to play again? [y/n] ")
    if response[0].upper() == "Y":
        "Okay, good luck!"
        main.play_game()
    elif response[0].upper() == "N":
        print("Okay. So long for now.")
        exit(0)
    print("Don't understand. Please enter Y for yes or N for No")
    return play_again()
