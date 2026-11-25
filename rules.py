letters = ["a", "b", "c", "d", "e"]

def bpawn_getLegalMoves(destination):
    letter = destination[0]
    number = int(destination[1])

    position = letters.index(letter)
    possible_moves = []

    # Forward
    if number - 1 >= 1:
        possible_moves.append(letter + str(number - 1))

        # Diagonal left
        if position > 0:
            left = letters[position - 1]
            possible_moves.append(left + str(number - 1))

        # Diagonal right
        if position < len(letters) - 1:
            right = letters[position + 1]
            possible_moves.append(right + str(number - 1))

    return possible_moves

def wpawn_getLegalMoves(destination):
    letter = destination[0]
    number = int(destination[1])

    position = letters.index(letter)
    possible_moves = []

    # Forward
    if number + 1 <= 5:
        possible_moves.append(letter + str(number + 1))

        # Diagonal left
        if position > 0:
            left = letters[position - 1]
            possible_moves.append(left + str(number + 1))

        # Diagonal right
        if position < len(letters) - 1:
            right = letters[position + 1]
            possible_moves.append(right + str(number + 1))

    return possible_moves

def king_getLegalMoves(destination):
    letter = destination[0]
    number = int(destination[1])

    position = letters.index(letter)
    possible_moves = []

    for file_change in [-1, 0, 1]:
        for rank_change in [-1, 0, 1]:

            if file_change == 0 and rank_change == 0:
                continue

            new_position = position + file_change
            new_number = number + rank_change

            if 0 <= new_position < len(letters) and 1 <= new_number <= 5:
                possible_moves.append(
                    letters[new_position] + str(new_number)
                )

    return possible_moves

#minimax start

import copy
def king_distance(square1, square2):

    file1 = letters.index(square1[0])
    file2 = letters.index(square2[0])

    rank1 = int(square1[1])
    rank2 = int(square2[1])

    return max(
        abs(file1 - file2),
        abs(rank1 - rank2)
    )
def get_board_value(board):

    score = 0

    white_king = None
    black_king = None

    for square, piece in board.items():

        if piece == "wpawn":
            score += 10

        elif piece == "bpawn":
            score -= 10

        elif piece == "wking":
            white_king = square

        elif piece == "bking":
            black_king = square

    if white_king is not None:

        black_pawns = [
            square for square, piece in board.items()
            if piece == "bpawn"
        ]

        if black_pawns:
            closest = min(
                king_distance(white_king, pawn)
                for pawn in black_pawns
            )

            score += (4 - closest) * 5

    # King moves towards white pawns
    if black_king is not None:

        white_pawns = [
            square for square, piece in board.items()
            if piece == "wpawn"
        ]

        if white_pawns:
            closest = min(
                king_distance(black_king, pawn)
                for pawn in white_pawns
            )

            score -= (4 - closest) * 5

    return score

def make_move(board, start, end):

    new_board = copy.deepcopy(board)

    piece = new_board.pop(start)
    new_board.pop(end, None)

    new_board[end] = piece

    return new_board

def is_king_in_check(board, color):

    king = color + "king"
    enemy_pawn = "bpawn" if color == "w" else "wpawn"
    enemy_king = "bking" if color == "w" else "wking"

    king_square = None
    enemy_king_square = None

    for square, piece in board.items():

        if piece == king:
            king_square = square

        elif piece == enemy_king:
            enemy_king_square = square

    if king_square is None:
        return True

    file_position = letters.index(king_square[0])
    rank = int(king_square[1])

    #enemy pawn attack squares
    enemy_rank = rank + 1 if color == "w" else rank - 1

    if 1 <= enemy_rank <= 5:

        for file_change in [-1, 1]:

            enemy_file = file_position + file_change

            if 0 <= enemy_file < len(letters):

                enemy_square = letters[enemy_file] + str(enemy_rank)

                if board.get(enemy_square) == enemy_pawn:
                    return True

    #Enemy king distance
    if enemy_king_square is not None:

        enemy_file = letters.index(enemy_king_square[0])
        enemy_rank = int(enemy_king_square[1])

        if (abs(file_position - enemy_file) <= 1 and
            abs(rank - enemy_rank) <= 1):
            return True

    return False

def get_goal_pawn_square(board, color):

    pawn = color + "pawn"
    target_rank = "5" if color == "w" else "1"

    for square, piece in board.items():
        if piece == pawn and square[1] == target_rank:
            return square

    return None


def update_pending_winner(board, mover, pending_winner):

    # Response move
    if pending_winner is not None and mover != pending_winner:

        pawn_square = get_goal_pawn_square(board, pending_winner)

        if pawn_square is not None:
            return None, pending_winner

        # Play continues
        pending_winner = None

    # Check if reached final rank.
    if pending_winner is None:

        if get_goal_pawn_square(board, mover) is not None:
            pending_winner = mover

    return pending_winner, None

def minimax(board, depth, maximizing, pending_winner=None):

    if depth == 0:
        #pawn at final rank, awaiting capture
        if pending_winner == "w":
            return 9000

        elif pending_winner == "b":
            return -9000

        return get_board_value(board)

    best_score = float("-inf") if maximizing else float("inf")

    player = "w" if maximizing else "b"

    found_move = False

    for square, piece in board.items():

        if piece[0] != player:
            continue

        if piece == "wpawn":
            moves = wpawn_getLegalMoves(square)

        elif piece == "bpawn":
            moves = bpawn_getLegalMoves(square)

        else:
            moves = king_getLegalMoves(square)

        for move in moves:

            if not is_valid_move(board, square, move, piece):
                continue

            new_board = make_move(board, square, move)

            if is_king_in_check(new_board, player):
                continue

            found_move = True

            new_pending, winner = update_pending_winner(
                new_board, player, pending_winner
            )

            if winner is not None:

                score = 10000 if winner == "w" else -10000

            else:

                score = minimax(
                    new_board,
                    depth - 1,
                    not maximizing,
                    new_pending
                )

            if maximizing:
                best_score = max(best_score, score)

            else:
                best_score = min(best_score, score)

    if not found_move:

        if pending_winner is not None:
            return 10000 if pending_winner == "w" else -10000

        return get_board_value(board)

    return best_score



def find_best_move(board, depth=3):

    best_score = float("-inf")
    best_move = None

    pending_winner = None

    if get_goal_pawn_square(board, "w") is not None:
        pending_winner = "w"

    elif get_goal_pawn_square(board, "b") is not None:
        pending_winner = "b"

    for square, piece in board.items():

        if piece[0] != "w":
            continue

        if piece == "wpawn":
            moves = wpawn_getLegalMoves(square)

        else:
            moves = king_getLegalMoves(square)

        for move in moves:

            if not is_valid_move(board, square, move, piece):
                continue

            new_board = make_move(board, square, move)

            if is_king_in_check(new_board, "w"):
                continue

            new_pending, winner = update_pending_winner(
                new_board, "w", pending_winner
            )

            if winner is not None:

                score = 10000 if winner == "w" else -10000

            else:

                score = minimax(
                    new_board,
                    depth - 1,
                    False,
                    new_pending
                )

            if score > best_score:
                best_score = score
                best_move = (square, move)

    return best_move


def is_valid_move(board, start, end, piece):

    if board.get(start) != piece:
        return False

    target = board.get(end)

    # Kings cannot be captured
    if target in ("wking", "bking"):
        return False

    # Cannot capture own piece
    if target is not None and target[0] == piece[0]:
        return False

    # If king in check, only king can move
    if is_king_in_check(board, piece[0]) and piece[1:] != "king":
        return False

    # Pawn movement rules
    if piece in ("wpawn", "bpawn"):

        direction = 1 if piece == "wpawn" else -1

        file_difference = letters.index(end[0]) - letters.index(start[0])
        rank_difference = int(end[1]) - int(start[1])

        # Forward
        if file_difference == 0:
            if rank_difference != direction or target is not None:
                return False

        # Diagonal capture
        elif abs(file_difference) == 1:
            if rank_difference != direction or target is None:
                return False

        else:
            return False
        
    new_board = make_move(board, start, end)

    # Cannot leave own king in check
    if is_king_in_check(new_board, piece[0]):
        return False

    return True

def get_valid_moves(board, start):
    piece = board.get(start)

    if piece is None:
        return []

    if piece == "wpawn":
        moves = wpawn_getLegalMoves(start)
    elif piece == "bpawn":
        moves = bpawn_getLegalMoves(start)
    else:
        moves = king_getLegalMoves(start)

    return [
        move for move in moves
        if is_valid_move(board, start, move, piece)
    ]


#checking win
def check_winner(board):
    #Are there pawns left? 
    pawns_remaining = sum(1 for piece in board.values()
        if piece in ("wpawn", "bpawn")
    )

    if pawns_remaining == 0:
        return "Draw"

    # White pawn reaches end
    for square, piece in board.items():

        if piece == "wpawn" and square[1] == "5":

            for enemy_square, enemy_piece in board.items():

                if enemy_piece == "bpawn":
                    moves = bpawn_getLegalMoves(enemy_square)

                elif enemy_piece == "bking":
                    moves = king_getLegalMoves(enemy_square)

                else:
                    continue

                if square in moves:
                    return None

            return "White"

    # Black pawn reaches end
    for square, piece in board.items():

        if piece == "bpawn" and square[1] == "1":

            for enemy_square, enemy_piece in board.items():

                if enemy_piece == "wpawn":
                    moves = wpawn_getLegalMoves(enemy_square)

                elif enemy_piece == "wking":
                    moves = king_getLegalMoves(enemy_square)

                else:
                    continue

                if square in moves:
                    return None

            return "Black"

    return None