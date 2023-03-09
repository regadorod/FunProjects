from importlib import import_module
import traceback
import re

##########################################
# CLASS FOR COOL, FANCY COLORS. YAY!     #
##########################################
# SGR color constants
# rene-d 2018
# https://bit.ly/3XKJ69G

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"
    # cancel SGR codes if we don't write to a terminal
    if not __import__("sys").stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        # set Windows console in VT mode
        if __import__("platform").system() == "Windows":
            kernel32 = __import__("ctypes").windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32



##########################################
# STRING WITH TESTS                      #
##########################################
tests_str = '''
# One game per line
# Lines beginning with '#' are ignored
# Blank lines are ignored
#
# Format:
# winner,num_valid_moves,method=MOVES
#     MOVES: moveA_row,moveA_col;moveB_row,moveB_col;...
#
# Note on num_valid_moves: if num_valid_moves differs from
#       length of MOVES, invalid moves are being tested
#
# Note on method: two characters
#     - Indicates how game was won
#     - First char is direction (d=diagonal, r=row, c=column)
#     - Second char indicates which one
#           row 0 is topmost row, row 2 is bottommost row
#           column 0 is leftmost column, column 2 is rightmost column
#           diagonal 0 is top-left to bottom-right
#           diagonal 1 is top-right to bottom-left

# TIES
T,9,-=1,1;0,0;0,1;2,1;2,0;0,2;1,2;1,0;2,2
T,9,-=0,0;1,1;0,2;0,1;2,1;1,2;1,0;2,0;2,2
T,9,-=1,2;2,0;1,0;1,1;0,2;2,2;0,0;0,1;2,1
T,9,-=1,0;1,2;1,1;2,0;0,0;2,2;0,2;0,1;2,1

# WIN AFTER 3
O,6,c0=0,1;2,0;1,2;0,0;2,2;1,0
X,5,d1=1,1;0,0;0,2;1,0;2,0
O,6,r0=1,2;0,2;2,0;0,0;2,1;0,1

# WIN AFTER 4
X,7,r2=1,1;0,1;2,1;0,2;2,2;1,2;2,0
O,8,d0=1,0;1,1;2,0;0,0;0,2;1,2;2,1;2,2
O,8,c1=0,2;1,1;1,2;0,0;1,0;2,1;2,0;0,1

# WIN AFTER 5
X,9,r1=1,1;0,1;0,0;2,2;1,0;2,0;2,1;0,2;1,2
X,9,c2=1,1;0,0;2,0;0,1;2,2;2,1;1,2;1,0;0,2

# INCOMPLETE
I,6,-=1,1;0,0;0,1;2,1;2,0;0,2
I,8,-=1,1;0,1;0,0;2,2;1,0;2,0;2,1;0,2

# INVALID MOVES
X,5,d1=1,1;3,2;0,9;1,5;0,0;0,2;1,0;2,0
T,9,-=1,2;2,0;1,0;1,1;0,2;2,2;0,0;0,1;3,2;2,1
'''



##########################################
# TESTING FUNCTIONS                      #
##########################################

BASE = 0
MODERATE = 1
COMPLETE = 2
def pick_tier():
    valid = False
    regexp = re.compile(r'^\s*[1-3]\s*$')
    print('GRADING TIERS:')
    print('1. Base Functionality')
    print('2. Moderate Functionality')
    print('3. Complete Functionality')
    while not valid:
        tier = input('Select the tier to test (1/2/3): ')
        if regexp.match(tier):
            tier = int(tier) - 1  # to match tiers defined below
            valid = True
        else:
            print(f'  Invalid entry: {tier}')
    return tier

def print_results(results):
    print(f'{Colors.BOLD}EXPECTED RESULTS:{Colors.END}')
    if results[0] == 'T':
        print(f'{Colors.YELLOW}\tWinner: N/A (tie){Colors.END}')
    elif results[0] == 'I':
        print(f'{Colors.YELLOW}\tGame incomplete at {results[1]} moves{Colors.END}')
    else:
        print(f'{Colors.YELLOW}\tWinner: {results[0]}{Colors.END}')
        print(f'{Colors.YELLOW}\tMethod: {results[2]}{Colors.END}')

def parse_tests():
    tests = []
    cur_label = None
    for line in tests_str.split('\n'):
        # Skip blank or comments
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        # Split results from moves
        s = line.split('=')
        assert len(s) == 2
        results, moves = s
        results = results.split(',')
        results = (results[0], int(results[1]), results[2])

        moves = moves.split(';')
        moves = [m.split(',') for m in moves]  # split move strings into lists
        moves = [(int(r),int(c)) for r,c in moves]  # convert to int-tuples
        tests.append((results,moves))
    return tests

def filter_tests(tests, tier):
    tests_to_run = []
    for results, moves in tests:
        valid_moves = results[1]
        direction = results[2][0]

        if tier == BASE:
            if direction == 'c' or direction == 'd':
                continue

        if tier < COMPLETE:
            if valid_moves != len(moves):
                continue

        tests_to_run.append((results,moves))
    return(tests_to_run)


def run_tests():
    tier = pick_tier()
    tests = parse_tests()
    tests = filter_tests(tests, tier)

    # Check whether module exists
    try:
        tictactoe = import_module('tictactoe')
        play_game = tictactoe.play_game
    except ModuleNotFoundError:
        print(f'{Colors.RED}Could not find script "tictactoe.py"{Colors.END}')
        exit()

    i = 0
    for results, moves in tests:
        print(Colors.BLUE + '~'*40 + Colors.END)
        print(f'{Colors.BLUE}STARTING GAME TEST: {Colors.END}'
            + f'{Colors.YELLOW}{i+1}{Colors.END}'
            + f'{Colors.BLUE}/{len(tests)}{Colors.END}') 
        print(f'{Colors.BLUE}Moves: {moves}{Colors.END}')
        print()
        try:
            play_game(moves, 'X')
        except (Exception, SystemExit) as e:
            if isinstance(e, SystemExit):
                print(f'{Colors.RED}Your script exited using quit() or exit(){Colors.END}')
                print(f'{Colors.YELLOW}Any calls to these functions must be removed{Colors.END}')
                print('Terminating end-to-end tests')
                exit()
            else:
                print(f'{Colors.YELLOW}Your code produced an error: {Colors.END}')
                print(Colors.RED)
                traceback.print_exc()  # print most recent exception
                print(Colors.END)
        print()
        print(f'{Colors.BLUE}END OF GAME TEST: {Colors.END}'
            + f'{Colors.YELLOW}{i+1}{Colors.END}'
            + f'{Colors.BLUE}/{len(tests)}{Colors.END}') 
        print(Colors.BLUE + '~'*40 + Colors.END)
        print()

        print_results(results)
        input('\n\nPress ENTER to continue (Ctrl-C to exit)...')
        i += 1


if __name__ == '__main__':
    run_tests()
    print(f'\n\n{Colors.PURPLE}All tests complete.{Colors.END}')
