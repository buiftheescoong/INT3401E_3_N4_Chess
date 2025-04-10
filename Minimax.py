import chess

def evaluate_board(board):
    # giá trị mỗi quân cờ
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }
    # giá trị của các quân trong từng vị trí
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    return score

def minimax (game, depth, isMaximizingPlayer):
    if depth == 0:
        return -evaluate_board(game.board())
    newGameMoves = list(game.legal_moves)
    if isMaximizingPlayer:
        maxEvaluation = -float('inf')
        for move in newGameMoves:
            game.push(move)
            maxEvaluation += minimax(game, depth - 1, not isMaximizingPlayer)
            game.pop()
        return maxEvaluation
    else:
        minEvaluation = float('inf')
        for move in newGameMoves:
            game.push(move)
            minEvaluation += minimax(game, depth - 1, not isMaximizingPlayer)
            game.pop()
        return minEvaluation
