import os
import sys
import time
from random import random

BLACK   = "\033[1;40;40m"
WHITE   = "\033[1;97;40m"
GREEN = "\033[1;32;40m"
MAGENTA = "\033[1;95;40m"
YELLOW = "\033[1;93;40m"
BROWN = '\033[93;40m'
CYAN  = "\033[1;96;40m"
END = "\033[0;0m"

TREE = [
    "                       ",
    "                       ",
    "           x           ",
    "          xxx          ",
    "         xxxxx         ",
    "       xxxxxxxxx       ",
    "     xxxxxxxxxxxxx     ",
    "__________bbb__________",
]

BACKGROUND = [
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
    "                       ",
]

# update background array
def update(background):
    new_bg = []

    # create new snow flakes on line 0
    line = ""
    for i in range(len(background[0])):
        if random() < 0.025:
            line += "*"
        else:
            line += " "
    new_bg.append(line)

    # update snow flake position
    num_rows = len(background)
    num_cols = len(background[0])
    # skip first line
    for i in range(1, num_rows):
        line = ""
        for j in range(num_cols):
            # move snow flake down
            if background[i - 1][j] == "*":
                line += "*"
            else:
                line += " "
        new_bg.append(line)

    return new_bg

def render(background):
    # build string to return
    s = ""

    for i, line in enumerate(TREE):
        for j, c in enumerate(line):
            # render tree or lights
            if c == "x":
                # lights
                if random() < 0.1:
                    r = random()
                    color = MAGENTA
                    if r < 0.3:
                        color = CYAN
                    elif r < 0.6:
                        color = YELLOW
                    s += f"{color}x{color}{END}"
                # tree
                else:
                    s += f"{GREEN}x{GREEN}{END}"
            # render tree bark
            elif c == "b":
                s += f"{BROWN}x{BROWN}{END}"
            # render background
            else:
                # render snow
                if background[i][j] == "*":
                    s += f"{WHITE}*{WHITE}{END}"
                else:
                    s += f"{BLACK} {BLACK}{END}"

        # new line
        s += "\n"
    return s

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

background = BACKGROUND

while True:
    # update background
    background = update(background)

    ## animate ##
    # clear terminal
    clear()
    # write to terminal
    sys.stdout.write(render(background))
    sys.stdout.flush()
    # wait 0.5 seconds
    time.sleep(0.5)