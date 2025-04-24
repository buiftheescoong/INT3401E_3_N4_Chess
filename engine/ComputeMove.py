import random

import chess
import timeit
import time
import numpy as np

# KILLER MOVE & HISTORY HEURISTIC
killer_move = np.zeros((20, 2), dtype=chess.Move)  # killer_move[0/1][ply]
history_move = np.zeros((7, 2, 64), dtype=int)

# MVV-LVA TABLE
MVV_LVA = np.array([
    [0, 0, 0, 0, 0, 0, 0],  # victim None,  attacker None, P, N, B, R, Q, K
    [0, 15, 14, 13, 12, 11, 10],  # victim P,     attacker None, P, N, B, R, Q, K
    [0, 25, 24, 23, 22, 21, 20],  # victim N,     attacker None, P, N, B, R, Q, K
    [0, 35, 34, 33, 32, 31, 30],  # victim B,     attacker None, P, N, B, R, Q, K
    [0, 45, 44, 43, 42, 41, 40],  # victim R,     attacker None, P, N, B, R, Q, K
    [0, 55, 54, 53, 52, 51, 50],  # victim Q,     attacker None, P, N, B, R, Q, K
    [0, 0, 0, 0, 0, 0, 0],  # victim K,     attacker None, P, N, B, R, Q, K
])
MVV_LVA_OFFSET = 1000000


def move_ordering(board: chess.Board, move: chess.Move, depth):
    move_score = 0
    to_square = move.to_square
    from_square = move.from_square

    # 1. Promotion: nếu là nước phong cấp
    if move.promotion is not None:
        # Trả về điểm cực cao hoặc cực thấp tùy vào lượt đi
        return float("inf") if board.turn == chess.WHITE else -float("inf")

    # 2. Capture move
    if board.is_capture(move):
        move_score += MVV_LVA_OFFSET
        if board.is_en_passant(move):
            victim = 1  # tốt bị ăn en passant
        else:
            victim = board.piece_at(to_square).piece_type
        attacker = board.piece_at(from_square).piece_type
        move_score += MVV_LVA[victim][attacker]

    return move_score

# GET BEST MOVE
def get_best_move(board: chess.Board):
    print("\n\nThinking...")
    start = timeit.default_timer()

    best_move = None
    try:
        import chess.polyglot
        with chess.polyglot.open_reader("data/final-book.bin") as reader:
            root = list(reader.find_all(board))
            if len(root) != 0:
                op_move = root[0]
                best_move = op_move.move
                time.sleep(1)
                return best_move, "opening"
    except:
        pass

    # If no opening move, choose random legal move
    legal_moves = list(board.legal_moves)
    if legal_moves:
        best_move = random.choice(legal_moves)

    end = timeit.default_timer()
    print("\nruntime: ", round(end - start, 2), "s")
    return best_move, "random"
