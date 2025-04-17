import random

import chess
import timeit
import time
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
