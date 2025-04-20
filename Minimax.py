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
    def get_k(rating):
        if rating > 2400:
            return 10
        elif 2000 <= rating <= 2400:
            return 15
        elif 1600 <= rating < 2000:
            return 20
        return 25

    k1, k2 = get_k(rating1), get_k(rating2)
    Qa, Qb = 10 ** (rating1 / 400), 10 ** (rating2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    if result is True:
        return rating1 + k1 * (1 - Ea)
    else:
        return rating2 + k2 * (0 - Eb)
