from helpers import *
from variables import SHOOTING_WORDS
from random import random, choice
from game_finish import *
from main import GameEnvironment


def _shoot(env: GameEnvironment):
    word = choice(SHOOTING_WORDS)
    start = time.time()
    while True:
        resp = input(f"To fire type {word}:")
        if resp == word:
            end = time.time()
            break
        print("Nope. Try again")
    return end - start - env.shot - 1


def hunt(env: GameEnvironment):
    if env.ammo < 40:
        print("Tough luck. You don't have enough ammo to hunt.")
        env.out_of_ammo = True
        return
    env.mileage -= 45
    score = _shoot(env)
    target = random() * 100
    if target < 13 * score:
        steady_print("You missed completely…and your dinner got away.\n")
    elif score <= 1.0:
        steady_print("Right between the eyes…you got a big one!\nFull bellies tonight!\n")
        env.ammo = int(env.ammo - 10 - (4 * random()))
        env.food = int(env.food + 26 + (3 * random()))
    else:
        steady_print("Nice shot…right on target…good eatin' tonight!\n")
        env.food = int(env.food + 24 - (2 * score))
        env.ammo = int(env.ammo - 10 - (3 * score))


def fort_hunt_or_push(env: GameEnvironment):
    def _get_odd_response():
        resp = int_input(f"Would you like to (1) hunt or (2) continue on?")
        if resp not in (1, 2):
            print("Enter a 1 or 2 please.")
            resp = _get_odd_response()
        return resp

    def _get_even_response():
        resp = int_input(f"Want to (1) stop at next fort{'' if env.out_of_ammo else ', (2) hunt, '} or (3) push on?")
        if resp not in (1, 2, 3):
            print(f"Enter a 1{'' if env.out_of_ammo else ', 2'}, 2 or 3 please.")
            resp = _get_even_response()
        return resp

    def _fort():
        if env.wallet <= 0:
            steady_print(
                "You sing with the folks there and get a good night's sleep, but you have no money to buy anything.\n")
            return
        steady_print(f"What would you like to spend on each of the following; (${env.wallet} remaining)")
        food = int_input("Food:")
        ammo = int_input("Ammunition:")
        clothing = int_input("Clothing:")
        medicine = int_input("Medicine:")
        total = sum([food, ammo, clothing, medicine])
        steady_print(f"The storekeeper tallies up your bill. It comes to ${total}.")
        if total > env.wallet:
            steady_print("Uh, oh. That's more than you have. Better start over.")
            return _fort()
        else:
            env.wallet -= total
            env.food += food * .67
            env.ammo += 33 * ammo
            env.clothes += clothing * .67
            env.repairs += medicine * .67
        return

    if env.segment % 2:
        response = _get_odd_response()
        if response == 2:
            return
        hunt(env)
    else:
        response = _get_even_response()
        if response == 3:
            return
        if response == 2:
            hunt(env)
        else:
            _fort()


def eat(env: GameEnvironment):
    if env.food < 5:
        you_lose_food(env)
    resp = int_input("Do you want to eat (1) poorly (2) moderately or (3) well? ")
    while resp not in (1, 2, 3):
        steady_print("Enter a 1, 2, or 3, please.")
        resp = int_input("Do you want to eat (1) poorly (2) moderately or (3) well? ")
    amount_eaten = 4 + (2.5 * resp)
    env.food -= amount_eaten
    if env.food < 0 and resp != 1:
        steady_print("You don't have enough to eat that well.\n")
        env.food += amount_eaten
        eat(env)
    else:
        env.eating = resp
    return


def attack(env: GameEnvironment):
    try:
        if random() * 10 > ((env.mileage // (100 - 4) ^ 2 + 72) / ((env.mileage // 100 - 4) ^ 2 + 12) - 1):
            return
    except ZeroDivisionError:
        return

    def _friendly_1():
        env.mileage += 15
        env.oxen -= 5

    def _friendly_2():
        env.mileage -= 5
        env.ammo -= 100

    def _friendly_3():
        return

    def _friendly_4():
        env.mileage -= 20

    def _hostile_1():
        env.mileage += 20
        env.repairs -= 7
        env.ammo -= 150
        env.oxen -= 20

    def _shooting_results(score):
        if score <= 1:
            steady_print("Nice shooting — you drove them off.\n")
        elif score <= 4:
            steady_print("Kind of slow with your Colt .45.\n")
        else:
            steady_print("Pretty slow on the draw, partner. You got a nasty flesh wound.\n"
                         "You'll have to see the doc soon as you can.\n")
            env.hurt = True

    def _hostile_2():
        score = _shoot(env)
        env.ammo = env.ammo - (score * 40) - 80
        _shooting_results(score)

    def _hostile_3():
        if random() > 0.8:
            steady_print("They did not attack. Whew!\n")
            return 1
        else:
            env.ammo -= 150
            env.repairs -= 7

    def _hostile_4():
        score = _shoot(env)
        env.ammo = env.ammo - (score * 30) - 80
        env.mileage -= 25
        _shooting_results(score)

    friendly_funcs = {1: _friendly_1, 2: _friendly_2, 3: _friendly_3, 4: _friendly_4}
    hostile_funcs = {1: _hostile_1, 2: _hostile_2, 3: _hostile_3, 4: _hostile_4}

    friendly = random() > .2
    steady_print(f"Riders ahead! They{' do not ' if friendly else ' '}look hostile.\n")
    steady_print("You can (1) run, (2) attack, (3) ignore them, or (4) circle wagons.")
    resp = 0
    while resp not in (1, 2, 3, 4):
        resp = int_input("What do you want to do? ")
    if random() < .2:
        friendly = not friendly
    if friendly:
        friendly_funcs[resp]()
        steady_print("Riders were friendly, but check for possible losses.\n")
    else:
        result = hostile_funcs[resp]()
        if result:
            return
        steady_print("Riders were hostile. Better check for losses!\n")
        if env.ammo < 0:
            time.sleep(3)
            steady_print(
                "Oh my gosh!\n"
                "They're coming back and you're out of ammo! Your dreams turn to\n"
                "dust as you and your family are massacred on the prairie.\n"
            )
            you_lose(env)


def wagon_breakdown(env: GameEnvironment):
    env.mileage = env.mileage - 15 - (5 * random())
    env.repairs -= 4
    steady_print("Your wagon breaks down. It costs you time and supplies to fix it.\n")


def ox_gore(env: GameEnvironment):
    env.mileage -= 25
    env.oxen -= 10
    steady_print("An ox gores your leg. That slows you down for the rest of the trip.\n")


def broken_arm(env: GameEnvironment):
    env.mileage = env.mileage - 5 - (4 * random())
    env.repairs = env.repairs - 1 - (2 * random())
    steady_print("Bad luck…your daughter breaks her arm. You must stop and\n"
                 "make a splint and sling with some of your medical supplies.\n")


def ox_wanders(env: GameEnvironment):
    env.mileage -= 17
    steady_print("An ox wanders off and you have to spend time looking for it.\n")


def lost_son(env: GameEnvironment):
    env.mileage -= 10
    steady_print("Your son gets lost and you spend half a day searching for him.\n")


def no_water(env: GameEnvironment):
    env.mileage = env.mileage - 2 - (10 * random())
    steady_print("Nothing but contaminated and stagnant water near the trail.\n"
                 "You lose time looking for a clean spring or creek.\n")


def bad_weather(env: GameEnvironment):
    if env.mileage > 950:  # It snows
        enough_clothing = env.clothes < 11 + (2 * random())
        # noinspection SpellCheckingInspection
        steady_print(f"Cold weather…Brrrrrrr!…You{' do not ' if not enough_clothing else ' '}"
                     f"have enough clothing to keep warm.\n")
        if not enough_clothing:
            illness(env)
    else:  # It rains
        steady_print("Heavy rains. Traveling is slow in the mud and you break your spare\n"
                     "ox yoke using it to pry your wagon out of the mud. Worse yet, some\n"
                     "of your ammo is damaged by the water.\n")
        env.mileage = env.mileage - 5 - (10 * random())
        env.repairs -= 7
        env.ammo -= 400
        env.food -= 5


def bandits_attack(env: GameEnvironment):
    steady_print("Bandits attacking!\n")
    time.sleep(1)
    score = _shoot(env)
    env.ammo = env.ammo - 20 * score
    if env.ammo < 0:
        env.wallet = env.wallet / 3
        steady_print("You try to drive them off but you run out of bullets.\n"
                     "They grab as much cash as they can find.\n")
    if score > 1:
        steady_print("You get shot in the leg — \n")
        time.sleep(4)
        steady_print("and they grab one of your oxen.\n"
                     "Better have a doc look at your leg…and soon!\n")
        env.hurt = True
        env.oxen -= 10
        env.repairs -= 2
    else:
        steady_print("That was the quickest draw outside of Dodge City.\n"
                     "You got at least one and drove 'em off.\n")


def wagon_fire(env: GameEnvironment):
    env.mileage -= 15
    env.food -= 20
    env.ammo -= 400
    env.repairs = env.repairs - 2 - 6 * random()
    steady_print("You have a fire in your wagon. Food and supplies are damaged.\n")


def heavy_fog(env: GameEnvironment):
    env.mileage = env.mileage - 10 - 5 * random()
    steady_print("You lose your way in heavy fog. Time lost regaining the trail.\n")


def rattlesnake(env: GameEnvironment):
    steady_print("You come upon a rattlesnake and before you are able to get your gun\nout, it bites you.\n")
    env.ammo -= 10
    env.repairs -= 2
    if env.repairs < 0:
        steady_print("You have no medical supplies left, and you die of poison.\n")
        you_lose_sick2(env)
    else:
        steady_print("Fortunately, you acted quickly, sucked out the poison, and\n"
                     "treated the wound. It is painful, but you'll survive.\n")


def swamped(env: GameEnvironment):
    env.mileage = env.mileage - 20 - (20 * random())
    env.food -= 15
    env.clothes -= 10
    steady_print("Your wagon gets swamped fording a river; you lose food and clothes.\n")


def wild_animals(env: GameEnvironment):
    steady_print("You're sound asleep and you hear a noise…get up to investigate.\n")
    time.sleep(3)
    steady_print("It's wild animals! They attack you!\n")
    score = _shoot(env)
    if env.ammo < 40:
        steady_print("You're almost out of ammo; can't reach more.\n"
                     "The wolves come at you biting and clawing.\n")
        env.hurt = True
        you_lose_sick(env)
    if score <= 2:
        steady_print("Nice shooting, pardner…They didn't get much.\n")
    else:
        steady_print("Kind of slow on the draw. The wolves got at your food and clothes.\n")
        env.ammo -= 20 * score
        env.clothes -= 2 * score
        env.food -= 4 * score


def hailstorm(env: GameEnvironment):
    env.mileage = env.mileage - 5 - 10 * random()
    env.ammo -= 150
    env.repairs = env.repairs - 2 - 2 * random()
    steady_print("You're caught in a fierce hailstorm; ammo and supplies are damaged.\n")


def jack_diet(env: GameEnvironment):
    if env.eating == 1:
        ill = True
    elif env.eating == 2:
        ill = random() > 0.25
    else:
        ill = random() > 0.5
    if ill:
        illness(env)


def indian_givers(env: GameEnvironment):
    steady_print("Helpful Indians show you where to find more food.\n")
    env.food += 7


def hazards(env: GameEnvironment):
    probabilities = [6, 11, 13, 15, 17, 22, 32, 35, 37, 42, 44, 54, 64, 69, 95]  # EP
    events = [wagon_breakdown, ox_gore, broken_arm, ox_wanders,
              lost_son, no_water, bad_weather, bandits_attack,
              wagon_fire, heavy_fog, rattlesnake, swamped,
              wild_animals, hailstorm, jack_diet, indian_givers]
    probability = int(random() * 100)
    number = 15
    for idx, prob_idx in enumerate(probabilities):
        if probability < prob_idx:
            number = idx
            break
    try:
        events[number](env)
    except IndexError:
        pass


def illness(env: GameEnvironment):
    if 100 * random() < 10 + 35 * (env.eating - 1):
        steady_print("Mild illness. Your own medicine will cure it.\n")
        env.mileage -= 5
        env.repairs -= 1
    elif 100 * random() < 100 - (40 // 4 ^ (env.eating-1)):
        steady_print("The whole family is sick. Your medicine will probably work okay.\n")
        env.mileage -= 5
        env.repairs -= 2.5
    else:
        steady_print("Serious illness in the family. You'll have to stop and see a doctor\n"
                     "soon. For now, your medicine will work.\n")
        env.repairs -= 5
        env.sick = True
    if env.repairs < 0:
        steady_print(" …if only you had enough.")
        you_lose_sick(env, medical=True)


def blizzard(env: GameEnvironment):
    steady_print("Blizzard in the mountain pass. Going is slow; supplies are lost.\n")
    env.mileage = env.mileage - 30 - (40 * random())
    env.food -= 12
    env.ammo -= 200
    env.repairs -= 5
    if env.clothes < 18 + (2 * random()):
        illness(env)


def south_pass(env: GameEnvironment):
    if not env.south_pass_clear:
        env.south_pass_clear = True
        if random() < 0.8:
            blizzard(env)
        steady_print("You made it safely through the South Pass....no snow!\n")
    env.south_pass_mileage = 1
    if env.mileage < 1700 or env.blue_mountain_clear:
        return
    env.blue_mountain_clear = True
    if random() < 0.7:
        blizzard(env)


def mountains(env: GameEnvironment):
    if env.mileage <= 975:
        return
    try:
        if 10 * random() > 9 - (((int(env.mileage) // 100 - 15) ^ 2 + 72) / ((int(env.mileage) // 100 - 15) ^ 2 + 12)):
            south_pass(env)
    except ZeroDivisionError:
        pass
    steady_print("You're in rugged mountain country.\n")
    if random() < 0.1:
        steady_print("You get lost and lose valuable time trying to find the trail.\n")
        env.mileage -= 60
        south_pass(env)
