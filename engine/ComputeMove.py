import random
from typing import List
import chess
import timeit
import time
import numpy as np
from .heuristic import evaluate
from .uci_interface import UCIEngineInterface

MATE_SCORE     = 1000000000
MATE_THRESHOLD =  999000000

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
    [0, 0, 0, 0, 0, 0, 0]   # victim K,     attacker None, P, N, B, R, Q, K
])
MVV_LVA_OFFSET = 100  # offset for MVV-LVA values to ensure all are positive

def move_ordering(board: chess.Board, move: chess.Move):
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
def get_best_move(board: chess.Board, time_limit=1000, search_depth=4):
    """
    Get the best move for the current position using the C++ UCI engine.
    
    Args:
        board: A chess.Board object representing the current position
        time_limit: Time in milliseconds to spend thinking (default: 1000)
        search_depth: Search depth limit (default: 4)
        
    Returns:
        A tuple of (move, type) where move is a chess.Move object and type is 
        either "opening", "UCI", or "heuristic"
    """
    print("\n\nThinking...")
    start = time.time()

    # First try using opening book if available
    try:
        import chess.polyglot
        with chess.polyglot.open_reader("data/final-book.bin") as reader:
            root = list(reader.find_all(board))
            if len(root) != 0:
                op_move = root[0]
                best_move = op_move.move
                return best_move, "opening"
    except Exception as e:
        print(f"Opening book error: {str(e)}")

    # If opening book fails, use the UCI engine
    try:
        with UCIEngineInterface(depth=search_depth, movetime=time_limit) as engine:
            move, info = engine.get_best_move(board)
            if move:
                print(f"UCI engine move: {move}")
                print(f"UCI info: {info}")
                end = time.time()
                print("\nRuntime:", round(end - start, 2), "s")
                return move, "UCI"
    except Exception as e:
        print(f"UCI engine error: {str(e)}")
        
    # If UCI engine fails, fall back to the original heuristic algorithm
    print("Falling back to heuristic algorithm")
    max_depth = 4
    depth = 1
    best_move = None
    while time.time() - start < time_limit/1000 and depth < max_depth:
        best_move = next_move(depth, board)
        print(f'Using heuristic for depth {depth}')
        end = time.time()
        if end - start >= time_limit/1000:
            break
        depth += 1

    end = time.time()
    print("\nRuntime:", round(end - start, 2), "s")
    return best_move, "heuristic"

def next_move(depth: int, board: chess.Board) -> chess.Move:
    return minimax_root(depth, board)

def get_ordered_moves(board: chess.Board) -> List[chess.Move]:

    def orderer(move):
        return move_ordering(board, move)

    in_order = sorted(
        board.legal_moves, key=orderer, reverse=(board.turn == chess.WHITE)
    )
    return list(in_order)


def minimax_root(depth: int, board: chess.Board) -> chess.Move:

    maximize = board.turn == chess.WHITE
    best_move = -float("inf")
    if not maximize:
        best_move = float("inf")

    moves = get_ordered_moves(board)
    best_move_found = moves[0]

    for move in moves:
        board.push(move)
        if board.can_claim_draw():
            value = 0.0
        else:
            value = minimax(depth - 1, board, -float("inf"), float("inf"), not maximize)
        board.pop()
        if maximize and value >= best_move:
            best_move = value
            best_move_found = move
        elif not maximize and value <= best_move:
            best_move = value
            best_move_found = move

    return best_move_found


def minimax(
    depth: int,
    board: chess.Board,
    alpha: float,
    beta: float,
    is_maximising_player: bool,
) -> float:

    if board.is_checkmate():
        return -MATE_SCORE if is_maximising_player else MATE_SCORE

    elif board.is_game_over():
        return 0

    if depth == 0:
        return evaluate(board)

    if is_maximising_player:
        best_move = -float("inf")
        moves = get_ordered_moves(board)
        for move in moves:
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, not is_maximising_player)

            if curr_move > MATE_THRESHOLD:
                curr_move -= 1
            elif curr_move < -MATE_THRESHOLD:
                curr_move += 1
            best_move = max(
                best_move,
                curr_move,
            )
            board.pop()
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = float("inf")
        moves = get_ordered_moves(board)
        for move in moves:
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, not is_maximising_player)
            if curr_move > MATE_THRESHOLD:
                curr_move -= 1
            elif curr_move < -MATE_THRESHOLD:
                curr_move += 1
            best_move = min(
                best_move,
                curr_move,
            )
            board.pop()
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move

