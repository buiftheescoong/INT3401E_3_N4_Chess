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

mobility_weights = {
    chess.PAWN: 0.5,
    chess.KNIGHT: 4.5,
    chess.BISHOP: 3.0,
    chess.ROOK: 2.5,
    chess.QUEEN: 1.5,
    chess.KING: 0.1
}

# Weights for evaluation components
W_MOBILITY = 5
W_KING_SAFETY = 10
W_PAWN_STRUCTURE = 15
W_BISHOP_PAIR = 40
W_CENTER_CONTROL = 20
W_PAWN_SHELTER = 12
W_ROOK_OPEN = 15
W_OUTPOST = 8
W_TROPISM = 5
W_SPACE = 3
W_THREAT = 10

# GAME PHASE
def game_phase(board: chess.Board):
    phase_weights = {chess.QUEEN: 4, chess.ROOK: 2, chess.BISHOP: 1, chess.KNIGHT: 1}
    max_counts = {chess.QUEEN: 1, chess.ROOK: 2, chess.BISHOP: 2, chess.KNIGHT: 2}
    max_phase = sum(phase_weights[p] * max_counts[p] * 2 for p in phase_weights)
    phase = 0
    for piece, w in phase_weights.items():
        phase += len(board.pieces(piece, chess.WHITE)) * w
        phase += len(board.pieces(piece, chess.BLACK)) * w
    return min(1.0, phase / max_phase)

# PST
def eval_pst(board: chess.Board):
    mg = game_phase(board)
    eg = 1 - mg
    score = 0
    for sq, piece in board.piece_map().items():
        arrays = wpiece_values if piece.color else bpiece_values
        pst_mg, pst_eg = arrays[piece.piece_type]
        idx = sq if piece.color else chess.square_mirror(sq)
        score += (pst_mg[idx] * mg + pst_eg[idx] * eg) * (1 if piece.color else -1)
    return score / (5255 + 435)

# MOBILITY
def eval_mobility(board: chess.Board):
    w_score = 0.0
    b_score = 0.0
    for move in board.legal_moves:
        ptype = board.piece_type_at(move.from_square)
        w = mobility_weights.get(ptype, 0)
        if board.color_at(move.from_square) == chess.WHITE:
            w_score += w
        else:
            b_score += w
    return w_score - b_score


# KING SAFETY: attacked neighbors + pawn shelter
def eval_king_safety(board: chess.Board):
    def attacked_neighbors(color):
        k = board.king(color)
        return sum(1 for sq in chess.SquareSet(chess.square_ring(k)) if sq in board.attackers(not color, sq))
    def pawn_shelter(color):
        kf = chess.square_file(board.king(color))
        files = [kf-1, kf, kf+1]
        return sum(len(board.pieces(chess.PAWN, color).intersection(chess.SquareSet([sq for f in files
                   for sq in board.pieces(chess.PAWN, color) if chess.square_file(sq)==f]))) for color in [color])
    return -(attacked_neighbors(chess.WHITE) - attacked_neighbors(chess.BLACK)) + \
           W_PAWN_SHELTER * (pawn_shelter(chess.WHITE) - pawn_shelter(chess.BLACK))

# PAWN STRUCTURE
def eval_pawn_structure(board: chess.Board):
    def score_pawns(color):
        s=0; files={f:[sq for sq in board.pieces(chess.PAWN,color) if chess.square_file(sq)==f] for f in range(8)}
        for f,p in files.items():
            if len(p)>1: s-=1
            if not (files.get(f-1) or files.get(f+1)): s-=1
            for sq in p:
                if not any((chess.square_file(op)==f) and ((color==chess.WHITE and op>sq) or (color==chess.BLACK and op<sq))
                           for op in board.pieces(chess.PAWN,not color)): s+=1
        return s
    return W_PAWN_STRUCTURE*(score_pawns(chess.WHITE) - score_pawns(chess.BLACK))

# BISHOP PAIR
def eval_bishop_pair(board: chess.Board):
    return W_BISHOP_PAIR*((len(board.pieces(chess.BISHOP,chess.WHITE))>1) - (len(board.pieces(chess.BISHOP,chess.BLACK))>1))

# CENTER CONTROL
CENTER=[chess.D4,chess.E4,chess.D5,chess.E5]
def eval_center_control(board: chess.Board):
    return sum(len(board.attackers(chess.WHITE,sq))-len(board.attackers(chess.BLACK,sq)) for sq in CENTER)

# ROOK ON OPEN/SEMI-OPEN
def eval_rook_open(board: chess.Board):
    s=0
    for color in [chess.WHITE, chess.BLACK]:
        for r in board.pieces(chess.ROOK,color):
            f=chess.square_file(r)
            if not any(chess.square_file(p)==f for p in board.pieces(chess.PAWN,True)): s += (1 if color==chess.WHITE else -1)
    return W_ROOK_OPEN*s

# OUTPOSTS
OUTPOST_SQ=[chess.D5,chess.E5,chess.D4,chess.E4]
def eval_outposts(board: chess.Board):
    s=0
    for color in [chess.WHITE, chess.BLACK]:
        for sq in board.pieces(chess.KNIGHT,color)|board.pieces(chess.BISHOP,color):
            if sq in OUTPOST_SQ and not any(chess.square_file(p)==chess.square_file(sq) for p in board.pieces(chess.PAWN,not color)):
                s+= (1 if color==chess.WHITE else -1)
    return W_OUTPOST*s

# TROPISM (king attack potential)
def eval_tropism(board: chess.Board):
    ks={chess.WHITE:board.king(chess.WHITE), chess.BLACK:board.king(chess.BLACK)}
    s=0
    for color in [chess.WHITE, chess.BLACK]:
        for p in board.piece_map().items():
            if board.color_at(p[0])==color and p[1] in [chess.QUEEN,chess.ROOK,chess.BISHOP,chess.KNIGHT]:
                dist=chess.square_distance(p[0],ks[not color])
                s+= (W_TROPISM/dist if color==chess.WHITE else -W_TROPISM/dist)
    return s

# SPACE (control total squares)
def eval_space(board: chess.Board):
    s=0
    for color in [chess.WHITE, chess.BLACK]:
        controlled=set().union(*(board.attacks(piece) for piece in board.pieces_map() if board.color_at(piece)==color))
        s+= (len(controlled) if color==chess.WHITE else -len(controlled))
    return W_SPACE*s

# THREATS & HANGING PIECES
def eval_threats(board: chess.Board):
    s=0
    for sq,piece in board.piece_map().items():
        if not board.is_attacked_by(not piece.color,sq): s+=0
        elif board.is_attacked_by(not piece.color,sq) and not board.is_attacked_by(piece.color,sq):
            s+= ( -W_THREAT if piece.color==chess.WHITE else W_THREAT)
    return s

# FINAL EVALUATE
def evaluate(board: chess.Board):
    if board.is_checkmate(): return MATE_SCORE*( -1 if board.turn else 1)
    if board.is_stalemate() or board.is_insufficient_material() or board.is_fivefold_repetition(): return 0
    total=0
    total+=eval_pst(board)
    # total+=W_MOBILITY*eval_mobility(board)
    # total+=W_KING_SAFETY*eval_king_safety(board)
    # total+=eval_pawn_structure(board)
    # total+=eval_bishop_pair(board)
    # total+=W_CENTER_CONTROL*eval_center_control(board)
    # total+=eval_rook_open(board)
    # total+=eval_outposts(board)
    # total+=eval_tropism(board)
    # total+=eval_space(board)
    # total+=eval_threats(board)
    return total
