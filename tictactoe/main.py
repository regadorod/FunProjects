import re

# THIS ONE HAS THE move_is_valid function
board = [['-', '-', '-'],
         ['-', '-', '-'],
         ['-', '-', '-']]


def play_game(moves=[], starting_player='X'):
       #adds the tuple to a list called moves and starts with x
    board = [['-', '-', '-'],
         ['-', '-', '-'],
         ['-', '-', '-']]
    current_player = starting_player
    while not get_winner(board) and len(moves) < 9:   #checks for winner or max moves
        print_board(board)
        move = get_next_move(current_player)
        board[move[0]][move[1]] = current_player  #adds to board
        moves.append(move)   #appends to moves list
        current_player = 'O' if current_player == 'X' else 'X'


    print_board(board)   #checks for winner
    winner = get_winner(board)
    if winner:
        print(winner)
    else:
        print("No winner")
    return winner




def print_board(board):
    for row in board:    #just prints the board
        print('|'.join(row))




def get_next_move(player):
    valid_move = False
    while not valid_move:
        move = input(f'Next move (row,col) for {player}: ')
        if not input_str_is_valid(move):
            print("Could not parse move")
            continue
        move = move.strip('()').split(',')
        row, col = int(move[0]), int(move[1])
        if not move_is_valid(board, move):  #check the automated version and the input version, inside get_next_move and outside
            print('Invalid move')
            continue
        else:
            valid_move = True
    return (row, col)


def move_is_valid(board, move):
     valid_move =False
     row, col = int(move[0]), int(move[1])
     print(board[row][col])

     if row >= 0 and row <= 2 and col >= 0 and col <= 2 and board[row][col] == '-':
         return True
     else:
         return False

def input_str_is_valid(move_str):
    pattern = re.compile("^[(]?(\s*[0-9]\s*,\s*[0-9]\s*)[)]?$")

    if re.match(pattern,move_str):
        return True
    else:
        return False

def get_winner(board):
    for player in ['X', 'O']:         #checks if any of the winning conditions are true
        if get_winner_rows(board):
           return get_winner_rows(board)
        elif get_winner_cols(board):
            return get_winner_cols(board)
        elif get_winner_diag(board):
            return get_winner_diag(board)
    return None



def get_winner_rows(board):
    for i in range(3):
        if board[i][0] == board[i][1] and board[i][1] == board [i][2] and not board[i][0] == '-':
            if board[i][0] == 'X':
                return 'X'
            else:
                return 'O'
    return None






def get_winner_cols(board):
    for i in range(3):
        if board[0][i] == board [1][i] and board [1][i] == board [2][i] and not board[0][i] == '-':
            if board[0][i] == 'X':
                return 'X'
            else:
                return 'O'
    return None






def get_winner_diag(board):
    if board[0][0] == board[1][1] and board[1][1] == board[2][2] and not board[2][2] == '-':
        if board[0][0] == 'X':
            return 'X'
        else:
            return 'O'
    elif board[0][2] == board[1][1] and board[1][1] == board[2][0] and not board[1][1] == '-':
        if board[2][0] == 'X':
            return 'X'
        else:
            return 'O'
    return None

if __name__ == '__main__':
    play_game()









