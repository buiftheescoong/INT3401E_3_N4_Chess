import chess
import numpy as np

MATE_SCORE = 999999

BPAWN_MG = np.array([100, 100, 100, 100, 100, 100, 100, 100,
                     176, 214, 147, 194, 189, 214, 132, 77,
                     82, 88, 106, 113, 150, 146, 110, 73,
                     67, 93, 83, 95, 97, 92, 99, 63,
                     55, 74, 80, 89, 94, 86, 90, 55,
                     55, 70, 68, 69, 76, 81, 101, 66,
                     52, 84, 66, 60, 69, 99, 117, 60,
                     100, 100, 100, 100, 100, 100, 100, 100])

BKNIGHT_MG = np.array([116, 228, 271, 270, 338, 213, 278, 191,
                       225, 247, 353, 331, 321, 360, 300, 281,
                       258, 354, 343, 362, 389, 428, 375, 347,
                       300, 332, 325, 360, 349, 379, 339, 333,
                       298, 322, 325, 321, 337, 332, 332, 303,
                       287, 297, 316, 319, 327, 320, 327, 294,
                       276, 259, 300, 304, 308, 322, 296, 292,
                       208, 290, 257, 274, 296, 284, 293, 284])

BBISHOP_MG = np.array([292, 338, 254, 283, 299, 294, 337, 323,
                       316, 342, 319, 319, 360, 385, 343, 295,
                       342, 377, 373, 374, 368, 392, 385, 363,
                       332, 338, 356, 384, 370, 380, 337, 341,
                       327, 354, 353, 366, 373, 346, 345, 341,
                       335, 350, 351, 347, 352, 361, 350, 344,
                       333, 354, 354, 339, 344, 353, 367, 333,
                       309, 341, 342, 325, 334, 332, 302, 313])

BROOK_MG = np.array([493, 511, 487, 515, 514, 483, 485, 495,
                     493, 498, 529, 534, 546, 544, 483, 508,
                     465, 490, 499, 497, 483, 519, 531, 480,
                     448, 464, 476, 495, 484, 506, 467, 455,
                     442, 451, 468, 470, 476, 472, 498, 454,
                     441, 461, 468, 465, 478, 481, 478, 452,
                     443, 472, 467, 476, 483, 500, 487, 423,
                     459, 463, 470, 479, 480, 480, 446, 458])

BQUEEN_MG = np.array([865, 902, 922, 911, 964, 948, 933, 928,
                      886, 865, 903, 921, 888, 951, 923, 940,
                      902, 901, 907, 919, 936, 978, 965, 966,
                      881, 885, 897, 894, 898, 929, 906, 915,
                      907, 884, 899, 896, 904, 906, 912, 911,
                      895, 916, 900, 902, 904, 912, 924, 917,
                      874, 899, 918, 908, 915, 924, 911, 906,
                      906, 899, 906, 918, 898, 890, 878, 858])

BKING_MG = np.array([-11, 70, 55, 31, -37, -16, 22, 22,
                     37, 24, 25, 36, 16, 8, -12, -31,
                     33, 26, 42, 11, 11, 40, 35, -2,
                     0, -9, 1, -21, -20, -22, -15, -60,
                     -25, 16, -27, -67, -81, -58, -40, -62,
                     7, -2, -37, -77, -79, -60, -23, -26,
                     12, 15, -13, -72, -56, -28, 15, 17,
                     -6, 44, 29, -58, 8, -25, 34, 28])

WPAWN_MG = np.array([100, 100, 100, 100, 100, 100, 100, 100,
                     52, 84, 66, 60, 69, 99, 117, 60,
                     55, 70, 68, 69, 76, 81, 101, 66,
                     55, 74, 80, 89, 94, 86, 90, 55,
                     67, 93, 83, 95, 97, 92, 99, 63,
                     82, 88, 106, 113, 150, 146, 110, 73,
                     176, 214, 147, 194, 189, 214, 132, 77,
                     100, 100, 100, 100, 100, 100, 100, 100])

WKNIGHT_MG = np.array([208, 290, 257, 274, 296, 284, 293, 284,
                       276, 259, 300, 304, 308, 322, 296, 292,
                       287, 297, 316, 319, 327, 320, 327, 294,
                       300, 332, 325, 360, 349, 379, 339, 333,
                       298, 322, 325, 321, 337, 332, 332, 303,
                       258, 354, 343, 362, 389, 428, 375, 347,
                       225, 247, 353, 331, 321, 360, 300, 281,
                       116, 228, 271, 270, 338, 213, 278, 191])

WBISHOP_MG = np.array([309, 341, 342, 325, 334, 332, 302, 313,
                       333, 354, 354, 339, 344, 353, 367, 333,
                       335, 350, 351, 347, 352, 361, 350, 344,
                       332, 338, 356, 384, 370, 380, 337, 341,
                       327, 354, 353, 366, 373, 346, 345, 341,
                       342, 377, 373, 374, 368, 392, 385, 363,
                       316, 342, 319, 319, 360, 385, 343, 295,
                       292, 338, 254, 283, 299, 294, 337, 323])

WROOK_MG = np.array([459, 463, 470, 479, 480, 480, 446, 458,
                     443, 472, 467, 476, 483, 500, 487, 423,
                     441, 461, 468, 465, 478, 481, 478, 452,
                     448, 464, 476, 495, 484, 506, 467, 455,
                     442, 451, 468, 470, 476, 472, 498, 454,
                     465, 490, 499, 497, 483, 519, 531, 480,
                     493, 498, 529, 534, 546, 544, 483, 508,
                     493, 511, 487, 515, 514, 483, 485, 495])

WQUEEN_MG = np.array([906, 899, 906, 918, 898, 890, 878, 858,
                      874, 899, 918, 908, 915, 924, 911, 906,
                      895, 916, 900, 902, 904, 912, 924, 917,
                      881, 885, 897, 894, 898, 929, 906, 915,
                      907, 884, 899, 896, 904, 906, 912, 911,
                      902, 901, 907, 919, 936, 978, 965, 966,
                      886, 865, 903, 921, 888, 951, 923, 940,
                      865, 902, 922, 911, 964, 948, 933, 928])

WKING_MG = np.array([-6, 44, 29, -58, 8, -25, 34, 28,
                     12, 15, -13, -72, -56, -28, 15, 17,
                     7, -2, -37, -77, -79, -60, -23, -26,
                     0, -9, 1, -21, -20, -22, -15, -60,
                     -25, 16, -27, -67, -81, -58, -40, -62,
                     33, 26, 42, 11, 11, 40, 35, -2,
                     37, 24, 25, 36, 16, 8, -12, -31,
                     -11, 70, 55, 31, -37, -16, 22, 22])

####################### ENDGAME #########################

BROOK_EG = np.array([
    506, 500, 508, 502, 504, 507, 505, 503,
    505, 506, 502, 502, 491, 497, 506, 501,
    504, 503, 499, 500, 500, 495, 496, 496,
    503, 502, 510, 500, 502, 504, 500, 505,
    505, 509, 509, 506, 504, 503, 496, 495,
    500, 503, 500, 505, 498, 498, 499, 489,
    496, 495, 502, 505, 498, 498, 491, 499,
    492, 497, 498, 496, 493, 493, 497, 480
])

BPAWN_EG = np.array([
    100, 100, 100, 100, 100, 100, 100, 100,
    277, 270, 252, 229, 240, 233, 264, 285,
    190, 197, 182, 168, 155, 150, 180, 181,
    128, 117, 108, 102, 93, 100, 110, 110,
    107, 101, 89, 85, 86, 83, 92, 91,
    96, 96, 85, 92, 88, 83, 85, 82,
    107, 99, 97, 97, 100, 89, 89, 84,
    100, 100, 100, 100, 100, 100, 100, 100
])

BKNIGHT_EG = np.array([
    229, 236, 269, 250, 257, 249, 219, 188,
    252, 274, 263, 281, 273, 258, 260, 229,
    253, 264, 290, 289, 278, 275, 263, 243,
    267, 280, 299, 301, 299, 293, 285, 264,
    263, 273, 293, 301, 296, 293, 284, 261,
    258, 276, 278, 290, 287, 274, 260, 255,
    241, 259, 270, 277, 276, 262, 260, 237,
    253, 233, 258, 264, 261, 260, 234, 215
])

BBISHOP_EG = np.array([
    288, 278, 287, 292, 293, 290, 287, 277,
    289, 294, 301, 288, 296, 289, 294, 281,
    292, 289, 296, 292, 296, 300, 296, 293,
    293, 302, 305, 305, 306, 302, 296, 297,
    289, 293, 304, 308, 298, 301, 291, 288,
    285, 294, 304, 303, 306, 294, 290, 280,
    285, 284, 291, 299, 300, 290, 284, 271,
    277, 292, 286, 295, 294, 288, 290, 285
])

BQUEEN_EG = np.array([
    918, 937, 943, 945, 934, 926, 924, 942,
    907, 945, 946, 951, 982, 933, 928, 912,
    896, 921, 926, 967, 963, 937, 924, 915,
    926, 944, 939, 962, 983, 957, 981, 950,
    893, 949, 942, 970, 952, 956, 953, 936,
    911, 892, 933, 928, 934, 942, 934, 924,
    907, 898, 883, 903, 903, 893, 886, 888,
    886, 887, 890, 872, 916, 890, 906, 879
])

BKING_EG = np.array([
    -74, -43, -23, -25, -11, 10, 1, -12,
    -18, 6, 4, 9, 7, 26, 14, 8,
    -3, 6, 10, 6, 8, 24, 27, 3,
    -16, 8, 13, 20, 14, 19, 10, -3,
    -25, -14, 13, 20, 24, 15, 1, -15,
    -27, -10, 9, 20, 23, 14, 2, -12,
    -32, -17, 4, 14, 15, 5, -10, -22,
    -55, -40, -23, -6, -20, -8, -28, -47
])

WROOK_EG = np.array([
    492, 497, 498, 496, 493, 493, 497, 480,
    496, 495, 502, 505, 498, 498, 491, 499,
    500, 503, 500, 505, 498, 498, 499, 489,
    503, 502, 510, 500, 502, 504, 500, 505,
    505, 509, 509, 506, 504, 503, 496, 495,
    504, 503, 499, 500, 500, 495, 496, 496,
    505, 506, 502, 502, 491, 497, 506, 501,
    506, 500, 508, 502, 504, 507, 505, 503
])

WPAWN_EG = np.array([
    100, 100, 100, 100, 100, 100, 100, 100,
    107, 99, 97, 97, 100, 89, 89, 84,
    96, 96, 85, 92, 88, 83, 85, 82,
    128, 117, 108, 102, 93, 100, 110, 110,
    107, 101, 89, 85, 86, 83, 92, 91,
    190, 197, 182, 168, 155, 150, 180, 181,
    277, 270, 252, 229, 240, 233, 264, 285,
    100, 100, 100, 100, 100, 100, 100, 100
])

WKNIGHT_EG = np.array([
    253, 233, 258, 264, 261, 260, 234, 215,
    241, 259, 270, 277, 276, 262, 260, 237,
    258, 276, 278, 290, 287, 274, 260, 255,
    267, 280, 299, 301, 299, 293, 285, 264,
    263, 273, 293, 301, 296, 293, 284, 261,
    253, 264, 290, 289, 278, 275, 263, 243,
    252, 274, 263, 281, 273, 258, 260, 229,
    229, 236, 269, 250, 257, 249, 219, 188
])

WBISHOP_EG = np.array([
    277, 292, 286, 295, 294, 288, 290, 285,
    285, 284, 291, 299, 300, 290, 284, 271,
    285, 294, 304, 303, 306, 294, 290, 280,
    293, 302, 305, 305, 306, 302, 296, 297,
    289, 293, 304, 308, 298, 301, 291, 288,
    292, 289, 296, 292, 296, 300, 296, 293,
    289, 294, 301, 288, 296, 289, 294, 281,
    288, 278, 287, 292, 293, 290, 287, 277
])

WQUEEN_EG = np.array([
    886, 887, 890, 872, 916, 890, 906, 879,
    907, 898, 883, 903, 903, 893, 886, 888,
    911, 892, 933, 928, 934, 942, 934, 924,
    926, 944, 939, 962, 983, 957, 981, 950,
    893, 949, 942, 970, 952, 956, 953, 936,
    896, 921, 926, 967, 963, 937, 924, 915,
    907, 945, 946, 951, 982, 933, 928, 912,
    918, 937, 943, 945, 934, 926, 924, 942
])

WKING_EG = np.array([
    -55, -40, -23, -6, -20, -8, -28, -47,
    -32, -17, 4, 14, 15, 5, -10, -22,
    -27, -10, 9, 20, 23, 14, 2, -12,
    -16, 8, 13, 20, 14, 19, 10, -3,
    -25, -14, 13, 20, 24, 15, 1, -15,
    -3, 6, 10, 6, 8, 24, 27, 3,
    -18, 6, 4, 9, 7, 26, 14, 8,
    -74, -43, -23, -25, -11, 10, 1, -12
])

wpiece_values = {
    chess.PAWN: [WPAWN_MG, WPAWN_EG],
    chess.KNIGHT: [WKNIGHT_MG, WKNIGHT_EG],
    chess.BISHOP: [WBISHOP_MG, WBISHOP_EG],
    chess.ROOK: [WROOK_MG, WROOK_EG],
    chess.QUEEN: [WQUEEN_MG, WQUEEN_EG],
    chess.KING: [WKING_MG, WKING_EG]
}
bpiece_values = {
    chess.PAWN: [BPAWN_MG, BPAWN_EG],
    chess.KNIGHT: [BKNIGHT_MG, BKNIGHT_EG],
    chess.BISHOP: [BBISHOP_MG, BBISHOP_EG],
    chess.ROOK: [BROOK_MG, BROOK_EG],
    chess.QUEEN: [BQUEEN_MG, BQUEEN_EG],
    chess.KING: [BKING_MG, BKING_EG]
}
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

# Weights for new evaluation components
W_MOBILITY = 5
W_KING_SAFETY = 10
W_PAWN_STRUCTURE = 15
W_BISHOP_PAIR = 40
W_CENTER_CONTROL = 20

# Determine midgame vs endgame phase (0 = EG, 1 = MG)
def game_phase(board: chess.Board):
    """
    Determine phase of game: returns 1.0 for full midgame and 0.0 for full endgame.
    Based on weighted counts of queens, rooks, bishops, knights.
    """
    # Weight per piece type
    phase_weights = {chess.QUEEN: 4, chess.ROOK: 2, chess.BISHOP: 1, chess.KNIGHT: 1}
    # Maximum counts per side for each piece
    max_counts = {chess.QUEEN: 1, chess.ROOK: 2, chess.BISHOP: 2, chess.KNIGHT: 2}
    # Compute max possible phase (both sides)
    max_phase = sum(w * max_counts[p] * 2 for p, w in phase_weights.items())
    # Sum current weighted piece counts
    phase = 0
    for piece, w in phase_weights.items():
        phase += len(board.pieces(piece, chess.WHITE)) * w
        phase += len(board.pieces(piece, chess.BLACK)) * w
    # Normalize to [0,1]
    return min(1.0, phase / max_phase)

# Material evaluation
def eval_material(board: chess.Board):
    score = 0
    for piece_type, value in piece_values.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score

# PST evaluation
def eval_pst(board: chess.Board):
    mg = game_phase(board)
    eg = 1 - mg
    score = 0
    for sq, piece in board.piece_map().items():
        arrays = wpiece_values if piece.color else bpiece_values
        pst_mg, pst_eg = arrays[piece.piece_type]
        idx = sq if piece.color else chess.square_mirror(sq)
        score += (pst_mg[idx] * mg + pst_eg[idx] * eg) * (1 if piece.color else -1)
    # Normalize by combined scalar
    return score / (5255 + 435)

# Mobility: count legal moves difference
def eval_mobility(board: chess.Board):
    white_moves = sum(1 for m in board.legal_moves if board.color_at(m.from_square) == chess.WHITE)
    black_moves = sum(1 for m in board.legal_moves if board.color_at(m.from_square) == chess.BLACK)
    return white_moves - black_moves

# King safety: count attacked squares around king
def eval_king_safety(board: chess.Board):
    def unsafe_neighbors(color):
        king_sq = board.king(color)
        attacks = set(board.attacks(king_sq))
        neighbors = chess.SquareSet(chess.square_ring(king_sq))
        return sum(1 for sq in neighbors if sq in attacks)
    return -(unsafe_neighbors(chess.WHITE) - unsafe_neighbors(chess.BLACK))

# Pawn structure: isolated, doubled, passed
def eval_pawn_structure(board: chess.Board):
    def score_pawns(color):
        s = 0
        files = {f: [sq for sq in board.pieces(chess.PAWN, color) if chess.square_file(sq)==f] for f in range(8)}
        for f, pawns in files.items():
            if len(pawns) > 1: s -= W_PAWN_STRUCTURE  # doubled
            if not any((f-1>=0 and files[f-1]) or (f+1<8 and files[f+1])): s -= W_PAWN_STRUCTURE  # isolated
        # passed pawns
        for sq in board.pieces(chess.PAWN, color):
            f = chess.square_file(sq)
            forward = (chess.WHITE if color else chess.BLACK)
            if not any(chess.square_file(op_sq)==f and board.color_at(op_sq)==(not color)
                       and ((forward==chess.WHITE and op_sq > sq) or (forward==chess.BLACK and op_sq < sq))
                       for op_sq in board.pieces(chess.PAWN, not color)):
                s += W_PAWN_STRUCTURE
        return s
    return score_pawns(chess.WHITE) - score_pawns(chess.BLACK)

# Bishop pair bonus
def eval_bishop_pair(board: chess.Board):
    return (len(board.pieces(chess.BISHOP, chess.WHITE))>=2) * W_BISHOP_PAIR - (len(board.pieces(chess.BISHOP, chess.BLACK))>=2) * W_BISHOP_PAIR

# Center control: pawns and pieces controlling d4,e4,d5,e5
CENTER_SQUARES = [chess.D4, chess.E4, chess.D5, chess.E5]
def eval_center_control(board: chess.Board):
    score = 0
    for sq in CENTER_SQUARES:
        attackers = board.attackers(chess.WHITE, sq)
        defenders = board.attackers(chess.BLACK, sq)
        score += len(attackers) - len(defenders)
    return score

# Final evaluation combining all components
def evaluate(board: chess.Board):
    if board.is_checkmate():
        return MATE_SCORE * (-1 if board.turn else 1)
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    total = 0
    total += eval_material(board)
    total += eval_pst(board)
    total += W_MOBILITY * eval_mobility(board)
    total += W_KING_SAFETY * eval_king_safety(board)
    total += eval_pawn_structure(board)
    total += eval_bishop_pair(board)
    total += W_CENTER_CONTROL * eval_center_control(board)
    return total
