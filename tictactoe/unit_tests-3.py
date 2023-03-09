from inspect import getmembers, isfunction, signature
from contextlib import contextmanager
from importlib import import_module
import os
import sys
from io import StringIO
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
# UTILITY FUNCTIONS                      #
##########################################

# Context manager for suppressing stdout. Does not suppress stderr.
# From stackoverflow.com/a/25061573 and bit.ly/3lIR067
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# Context manager for redirecting stdin.
@contextmanager
def redirect_stdin(string):
    old_stdin = sys.stdin
    sys.stdin = StringIO(string)
    try:
        yield
    finally:
        sys.stdin = old_stdin

# Returns 0 on failure, 1 on success
def test_args(f, n_expected):
    n_args = len(signature(f).parameters)
    if n_args == n_expected:
        p_pass(f'Correct number of arguments ({n_expected})')
        return 1
    else:
        p_fail(f'Incorrect number of arguments (expected {n_expected}, actually'
            + f' has {n_args})')
        return 0

def p_aux_args(f, args, stdin=None):
    if stdin: p_aux(f'with keyboard input: {repr(stdin)}')
    for a, n in zip(args, signature(f).parameters):
        p_aux(f'{n}: {repr(a)}')
    

# Returns (True, ret) when function returns without an exception
# Returns (False, None) when function fails
def safe_call(f, args, suppress_stdout=True, stdin=None):
    # Suppress stdout and/or get stdin from string
    if suppress_stdout:
        devnull = open(os.devnull, 'w')
        old_stdout = sys.stdout
        sys.stdout = devnull
    if stdin != None:
        old_stdin = sys.stdin
        sys.stdin = StringIO(stdin)

    # Call function
    try:
        ret = f(*args)

        # Reset stdout/stdin
        if suppress_stdout:
            sys.stdout = old_stdout
        if stdin != None:
            sys.stdin = old_stdin

        return True, ret

    except (Exception, SystemExit) as e:
        # Reset stdout/stdin
        if suppress_stdout:
            sys.stdout = old_stdout
        if stdin != None:
            sys.stdin = old_stdin

        if isinstance(e, SystemExit):
            p_fail('quit() or exit() was called and function did not return')
            p_aux_args(f, args, stdin=stdin)
        else:
            p_fail('Function produced an error and did not return')
            p_aux_args(f, args, stdin=stdin)
            print(Colors.RED)
            traceback.print_exc()  # print most recent exception
            print(Colors.END)

        return False, None

# Returns 0 on failure, 1 on success
def test(f, args, exp, stdin=None):
    success, ret = safe_call(f, args, stdin=stdin)
    if not success: return 0
    if ret != exp:
        p_fail(f"Returned {Colors.BLUE}{repr(ret)}{Colors.END} ({type(ret)})"
            + f" instead of {Colors.BLUE}{repr(exp)}{Colors.END} ({type(exp)})")
        retval = 0
    else:
        p_pass(f"Correctly returned {repr(exp)}")
        retval = 1
    p_aux_args(f, args, stdin=stdin)
    return retval



##########################################
# UNIT TEST FUNCTIONS                    #
##########################################

def test_play_game(ttt, tier):
    # Check number of args
    f = ttt.play_game
    total = 1
    passed = 0

    passed += test_args(f, 2)

    return (total, passed)


def test_print_board(ttt, tier):
    f = ttt.print_board
    total = 1
    passed = 0

    passed += test_args(f, 1)
    
    return (total, passed)


def test_get_winner(ttt, tier):
    f = ttt.get_winner
    total = 0
    passed = 0
    
    passed += test_args(f, 1)
    total += 1

    # No winner: all tiers
    b = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    passed += test(f, (b,), None)
    b = [['O', 'X', '-'], ['-', 'X', '-'], ['-', '-', '-']]
    passed += test(f, (b,), None)
    b = [['X', 'O', 'X'], ['-', 'O', '-'], ['-', 'X', '-']]
    passed += test(f, (b,), None)
    b = [['X', 'O', 'X'], ['X', 'X', 'O'], ['O', 'X', 'O']]
    passed += test(f, (b,), None)
    b = [['O', 'X', 'O'], ['O', 'X', 'X'], ['X', 'O', 'X']]
    passed += test(f, (b,), None)
    b = [['X', 'O', 'X'], ['X', 'O', 'O'], ['O', 'X', 'X']]
    passed += test(f, (b,), None)
    b = [['X', 'O', 'X'], ['X', 'O', 'X'], ['O', 'X', 'O']]
    passed += test(f, (b,), None)

    # Winner on rows: all tiers
    b = [['O', 'O', 'O'], ['-', '-', 'X'], ['X', 'X', '-']]
    passed += test(f, (b,), 'O')

    total += 8

    # Winner on cols/diag: moderate+
    if tier >= MODERATE:
        b = [['O', 'X', '-'], ['O', '-', 'X'], ['O', '-', 'X']]
        passed += test(f, (b,), 'O')
        b = [['O', '-', 'X'], ['X', 'O', 'O'], ['X', 'X', 'O']]
        passed += test(f, (b,), 'O')
        total += 2

    return (total, passed)


def test_get_winner_rows(ttt, tier):
    f = ttt.get_winner_rows
    total = 0
    passed = 0

    passed += test_args(f, 1)
    total += 1

    b = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    passed += test(f, (b,), None)
    b = [['O', 'X', 'O'], ['O', 'X', 'X'], ['X', 'O', 'X']]
    passed += test(f, (b,), None)
    b = [['O', '-', 'X'], ['O', 'X', '-'], ['X', '-', '-']]
    passed += test(f, (b,), None)
   
    b = [['O', 'O', 'O'], ['-', '-', 'X'], ['X', 'X', '-']]
    passed += test(f, (b,), 'O')
    b = [['X', 'O', 'O'], ['X', 'X', 'X'], ['O', 'X', 'O']]
    passed += test(f, (b,), 'X')
    b = [['-', 'O', 'O'], ['-', 'X', 'O'], ['X', 'X', 'X']]
    passed += test(f, (b,), 'X')

    total += 6
    return (total, passed)


def test_get_next_move(ttt, tier):
    f = ttt.get_next_move
    total = 0
    passed = 0

    passed += test_args(f, 1)
    total += 1

    # Parsable moves
    if tier >= BASE:
        passed += test(f, ('X',), (0,0), stdin='0,0\n')
        passed += test(f, ('X',), (2,0), stdin='2,0\n')
        passed += test(f, ('X',), (1,2), stdin='1,2\n')
        total += 3

    # Nonebasic moves
    if tier >= COMPLETE:
        passed += test(f, ('X',), (0,0), stdin='0 ,0\n')
        passed += test(f, ('X',), (2,0), stdin='0 0\n 2,0')
        passed += test(f, ('X',), (1,0), stdin='0,0,0\n 1,0')
        passed += test(f, ('X',), (1,2), stdin='a,0\n  1 , 2  \n')
        total += 4

    return (total, passed)


def test_get_winner_cols(ttt, tier):
    f = ttt.get_winner_cols
    total = 0
    passed = 0

    passed += test_args(f, 1)
    total += 1
    
    b = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    passed += test(f, (b,), None)
    b = [['O', 'X', 'O'], ['O', 'X', 'X'], ['X', 'O', 'X']]
    passed += test(f, (b,), None)
    b = [['O', 'O', 'O'], ['-', '-', 'X'], ['X', 'X', '-']]
    passed += test(f, (b,), None)
    
    b = [['O', 'X', '-'], ['O', '-', 'X'], ['O', '-', 'X']]
    passed += test(f, (b,), 'O')
    b = [['O', 'O', 'X'], ['X', 'O', 'X'], ['X', 'O', '-']]
    passed += test(f, (b,), 'O')
    b = [['O', 'O', 'X'], ['O', 'X', 'X'], ['X', 'O', 'X']]
    passed += test(f, (b,), 'X')

    total += 6
    return (total, passed)


def test_get_winner_diag(ttt, tier):
    f = ttt.get_winner_diag
    total = 0
    passed = 0

    passed += test_args(f, 1)
    total += 1

    b = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    passed += test(f, (b,), None)
    b = [['O', 'X', 'O'], ['O', 'X', 'X'], ['X', 'O', 'X']]
    passed += test(f, (b,), None)
    b = [['O', 'X', '-'], ['O', '-', 'X'], ['O', '-', 'X']]
    passed += test(f, (b,), None)
    
    b = [['O', '-', 'X'], ['X', 'O', 'O'], ['X', 'X', 'O']]
    passed += test(f, (b,), 'O')
    b = [['O', '-', 'X'], ['O', 'X', '-'], ['X', '-', '-']]
    passed += test(f, (b,), 'X')

    total += 5
    return (total, passed)


def test_input_str_is_valid(ttt, tier):
    f = ttt.input_str_is_valid
    total = 0
    passed = 0

    passed += test_args(f, 1)
    total += 1
    
    passed += test(f, ('',), False)
    passed += test(f, ('a,0',), False)
    passed += test(f, ('1',), False)
    passed += test(f, ('1 0',), False)
    passed += test(f, ('2,b',), False)
    passed += test(f, ('0,0,3',), False)

    passed += test(f, ('0,0',), True)
    passed += test(f, ('2, 0',), True)
    passed += test(f, ('  1 ,   2 ',), True)

    total += 9
    return (total, passed)


def test_move_is_valid(ttt, tier):
    f = ttt.move_is_valid
    total = 0
    passed = 0

    passed += test_args(f, 2)
    total += 1
    
    b = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    passed += test(f, (b, (0,0)), True)
    passed += test(f, (b, (0,1)), True)
    passed += test(f, (b, (1,1)), True)
    passed += test(f, (b, (2,0)), True)

    b = [['O', 'X', '-'], ['-', 'X', '-'], ['-', '-', '-']]
    passed += test(f, (b, (2,0)), True)
    passed += test(f, (b, (1,1)), False)

    b = [['X', 'O', 'X'], ['X', 'O', 'X'], ['O', 'X', 'O']]
    passed += test(f, (b, (0,0)), False)
    passed += test(f, (b, (2,2)), False)

    total += 8
    return (total, passed)



##########################################
# SET UP TESTS                           #
##########################################


# Printing functions

def p_pass(msg):
    print(f'[ {Colors.GREEN}PASS{Colors.END} ]  {msg}')

def p_fail(msg):
    print(f'[ {Colors.RED}FAIL{Colors.END} ]  {msg}')

def p_info(msg):
    print(f'[ {Colors.DARK_GRAY}INFO{Colors.END} ]  {msg}')

def p_aux(msg):
    print(' ' * 14 + msg)

def p_hdr(msg):
    print(f'\n{Colors.BOLD}{msg}{Colors.END}')


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

def run_tests(tictactoe, fnames_to_test, tier):
    jmp_table = {
        'play_game': test_play_game,
        'print_board': test_print_board,
        'get_winner': test_get_winner,
        'get_winner_rows': test_get_winner_rows,
        'get_next_move': test_get_next_move,
        'get_winner_cols': test_get_winner_cols,
        'get_winner_diag': test_get_winner_diag,
        'input_str_is_valid': test_input_str_is_valid,
        'move_is_valid': test_move_is_valid
    }

    # Run tests
    stats = []
    for name in fnames_to_test:
        test_fcn = jmp_table[name]
        p_hdr(f'Testing function "{name}"')
        stats.append((name, test_fcn(tictactoe, tier)))
    return stats


def init_tests():
    tier = pick_tier()
    print(f'{Colors.YELLOW}Starting test of tictactoe{Colors.END}')
    tier_strs = ('base', 'moderate', 'complete')
    print(f'Testing tier: {Colors.LIGHT_BLUE}{tier_strs[tier]}{Colors.END}')

    # Check whether module exists (import cannot be performed in function)
    print(f'\n{Colors.BOLD}Checking script{Colors.END}')
    try:
        tictactoe = import_module('tictactoe')
        p_pass('Script has correct name')
    except ModuleNotFoundError:
        p_fail('Could not find script "tictactoe.py"')
        p_aux(f'- Make sure you\'ve used VSCode\'s "Open Folder" command (in')
        p_aux(f'  the "File" menu) to open the folder where this script is located')
        p_aux(f'- Make sure your script has the correct name ("tictactoe.py")')
        p_aux(f'- Make sure your script is in the same folder as this script')
        print('Exiting...')
        exit()

    p_info(f'Attempting to load functions for {tier_strs[tier]} tier')
    registered_fnames = (
        ('play_game', 'print_board', 'get_winner', 'get_winner_rows'),
        ('play_game', 'print_board', 'get_winner', 'get_winner_rows',
        'get_next_move', 'get_winner_cols', 'get_winner_diag'),
        ('play_game', 'print_board', 'get_winner', 'get_winner_rows',
        'get_next_move', 'get_winner_cols', 'get_winner_diag',
        'input_str_is_valid', 'move_is_valid')
    )

    # getmembers returns list of (function name, function object)
    all_available_fnames = [val[0] for val in getmembers(tictactoe, isfunction)]
    fnames_to_test = []
    fnames_not_found = []
    max_name_length = max([len(s) for s in registered_fnames[tier]])  # for nice formatting

    for name in registered_fnames[tier]:
        if name in all_available_fnames:
            fnames_to_test.append(name)
            p_aux(f'{name:{max_name_length}s}  {Colors.GREEN}found{Colors.END}')
        else:
            fnames_not_found.append(name)
            p_aux(f'{name:{max_name_length}s}  {Colors.RED}not found{Colors.END}')

    # Launch tests
    stats = run_tests(tictactoe, fnames_to_test, tier)

    # name, two spaces, XX of XX passed, one space box padding
    print('\n\n')
    box_contents_width = max_name_length + 2 + 15 + 2

    # Summary box
    print(f'{Colors.DARK_GRAY}+-{Colors.END}{Colors.BOLD}SUMMARY{Colors.END}'
        + f'{Colors.DARK_GRAY}' + '-'*(box_contents_width - 8) + f'+{Colors.END}')
    for name, results in stats:
        print(f'{Colors.DARK_GRAY}|{Colors.END}'
            + f' {name:{max_name_length}s}  '
            + f'{Colors.YELLOW}{results[1]:2d}{Colors.END} of '
            + f'{Colors.YELLOW}{results[0]:2d}{Colors.END} passed '
            + f'{Colors.DARK_GRAY}|{Colors.END}')
    for name in fnames_not_found:
        print(f'{Colors.DARK_GRAY}|{Colors.END}'
            + f' {name:{max_name_length}s}{Colors.YELLOW}'
            + f'{"not tested":>{box_contents_width - max_name_length - 2}s}'
            + f'{Colors.END} '
            + f'{Colors.DARK_GRAY}|{Colors.END}')
    print(f'{Colors.DARK_GRAY}+' + '-' * box_contents_width + f'+{Colors.END}')


if __name__ == '__main__':
    init_tests()
    print(f'\n\n{Colors.PURPLE}All tests complete.{Colors.END}')
