import sys
import time


# both of these functions allows slower printing of strings character by character with user-defined speed
def steady_print(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(.05)
    return ""


def quick_print(text):
    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.01)
    return ""


def int_input(message):
    try:
        return int(input(message + " "))
    except ValueError:
        print(f"The entry must be a number")
        return int_input(message)


def fmtcols(mylist, cols):
    lines = ("\t|\t".join(mylist[i:i+cols]) for i in range(0, len(mylist),cols))
    return '\n'.join(lines)
