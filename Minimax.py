from typing import Any

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


def minimax(game, depth, isMaximizingPlayer):
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


def minimax_alpha_beta(game: object, depth: int, alpha: float, beta: float, isMaximizingPlayer: bool) -> int:
    if depth == 0:
        return -evaluate_board(game.board())
    newGameMoves = list(game.legal_moves)
    if isMaximizingPlayer:
        maxEvaluation = -float('inf')
        for move in newGameMoves:
            game.push(move)
            maxEvaluation = max(maxEvaluation, minimax_alpha_beta(game, depth - 1, alpha, beta, False))
            game.pop()
            alpha = max(alpha, maxEvaluation)
            if beta <= alpha:
                break
        return maxEvaluation
    else:
        minEvaluation = float('inf')
        for move in newGameMoves:
            game.push(move)
            minEvaluation = min(minEvaluation, minimax_alpha_beta(game, depth - 1, alpha, beta, True))
            game.pop()
            beta = min(beta, minEvaluation)
            if beta <= alpha:
                break
        return minEvaluation


def Elo_Calculation(rating1, rating2, result):
    if rating2 > 2400:
        k = 10
    elif rating2 >= 2000 and rating2 <= 2400:
        k = 15
    elif rating2 >= 1600 and rating2 <= 2000:
        k = 20
    else:
        k = 25
    Qa = pow(10, rating1 / 400)
    Qb = pow(10, rating2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = 1 - Ea
    if result is True:
        return rating1 + k * (1 - Ea)
    else:
        return rating2 + k * (0 - Eb)
