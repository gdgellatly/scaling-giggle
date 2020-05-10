from variables import *
from events import *
from game_finish import *
import os


class GameEnvironment(object):
    def __init__(self):
        self.dates = DATES  # DA$
        self.distances = DISTANCE_MARKERS  # (MP , PL)
        self.wallet = 350  # T
        self.oxen = 0  # A
        self.food = 0  # F
        self.ammo = 0  # B
        self.clothes = 0  # C
        self.repairs = 0  # R
        self.shot = 0  # DR

        self.mileage = 0  # M
        self.south_pass_mileage = False  # MP
        self.prior_mileage = 0  # MA
        self.end_miles = 0

        self.segment = 0  # J
        self.sick = False
        self.hurt = False
        self.out_of_ammo = False
        self.south_pass = False
        self.south_pass_clear = False
        self.eating = 1
        self.blue_mountain_clear = False

    def _buy_oxen(self):
        price = int_input(f"How much do you want to pay for a team of oxen? (${self.wallet} remaining)")
        if price < 100:
            print("No one in town has a team that cheap.")
            return self._buy_oxen()
        elif price > 150:
            print(f"You choose an honest dealer who tells you that ${price} is too much \n"
                  f"for a team of oxen. He charges you $150 and gives you ${price - 150} change.")
            price = 150
        return price

    def _buy_food(self):
        price = int_input(f"How much do you want to spend on food? (${self.wallet} remaining)")
        if price >= 13 and (self.oxen + price) < 300:
            return price
        elif price < 13:
            print("That won't even get you to the Kansas river - better spend a bit more")
        else:
            print("Hold on porky. You are going to want some clothes and ammo too")
        return self._buy_food()

    def _buy_ammo(self):
        bullets = int_input(f"How much do you want to spend on ammunition? (${self.wallet} remaining)")
        if bullets >= 2 and (self.wallet - bullets) > 30:
            return bullets
        elif bullets < 2:
            print("Better take a bit just for protection.")
        else:
            print("That won't leave any money for clothes.")
        return self._buy_ammo()

    def _buy_clothes(self):
        price = int_input(f"How much do you want to spend on clothes? (${self.wallet} remaining)")
        if price >= 24 and (self.wallet - price) > 5:
            return price
        elif price < 24:
            print("Your family is going to be mighty cold in the mountains. Better spend a bit more.")
        else:
            print("That leaves nothing for medicine.")
        return self._buy_clothes()

    def _buy_repairs(self):
        price = int_input(f"How much for medicine, bandages, repair parts, etc.? (${self.wallet} remaining)")
        if price >= 5 and (self.wallet - price) >= 0:
            return price
        elif price < 5:
            print("That's not at all wise.")
        else:
            print("You don't have that much money.")
        return self._buy_repairs()

    def make_initial_purchases(self):
        for item in ['oxen', 'food', 'ammo', 'clothes', 'repairs']:
            setattr(self, item, getattr(self, f'_buy_{item}')())
            self.wallet -= getattr(self, item)
            if item == 'ammo':
                self.ammo *= 50
        steady_print(f"You have ${self.wallet} left\n")

    def set_marksmanship(self):
        self.shot = int_input("How do you rank yourself? ") + 1
        if 1 > self.shot > 7:
            self.set_marksmanship()

    def print_inventory(self):
        inventory = [f"Cash:\t${max(self.wallet, 0):.2f}"]
        for item in ['oxen', 'food', 'clothes', 'ammo', 'repairs']:
            inventory.append(f"{item.title()}:\t{'$' if item != 'ammo' else ''}{max(getattr(self, item), 0):.2f}")
        print(fmtcols(inventory, 2))

    def days_travelled(self):
        days = 14 * self.segment + self.end_miles
        return {
            'months': int(days // 30.5),
            'days': int(days % 30.5)
        }


def play_game():
    print(f"{OPENING_MESSAGE}")
    print("")
    env = GameEnvironment()
    input("Press Enter when you're ready to go")
    print(INITIAL_SCENARIO)
    env.make_initial_purchases()
    quick_print(
        "Please rank your shooting (typing) ability from 1-5 as follows :\n"
        "(1) Ace marksman\n(2) Good shot\n(3) Fair to middlin'\n"
        "(4) Need more practice\n(5) Shaky knees\n")
    env.set_marksmanship()
    steady_print(" Your trip is about to begin…")
    while env.mileage < 2040:
        time.sleep(3)
        print('\n' * 50)
        if env.segment > 19:
            you_lose(env)
            break
        location = 'nowhere'
        for i, location in DISTANCE_MARKERS:
            if i >= env.mileage:
                break
        env.mileage = int(env.mileage)
        env.prior_mileage = env.mileage
        quick_print(f"Monday, {env.dates[env.segment]}.\n"
                    f"You have covered {env.mileage} miles and are "
                    f"{location}\n")  # distance
        if env.food < 6:
            print("You're low on food. Better buy some or go hunting soon.\n")
        if env.sick or env.hurt:
            env.wallet -= 10
            if env.wallet < 0:
                you_lose_sick(env)
            steady_print(f"Doctor charged $10 for his services to treat your {'illness' if env.sick else 'injuries'}\n")
            env.sick = False
            env.hurt = False
        env.segment += 1
        env.mileage += int(round(200 + ((env.oxen - 110) / 2.5) + (10 * random()), 0))
        quick_print(f"Here's what you now have (no. of bullets, $ worth of other items) :\n")
        env.print_inventory()
        fort_hunt_or_push(env)  # GOSUB 1000
        eat(env)  # Gosub 1310
        attack(env)  # Gosub 1390
        hazards(env)  # Gosub 1800
        mountains(env)  # Gosub 2640
        env.repairs = round(env.repairs, 2)
        env.ammo = int(env.ammo + 0.5)
        input("Press Enter to Continue")
    you_win(env)


if __name__ == '__main__':
    play_game()
