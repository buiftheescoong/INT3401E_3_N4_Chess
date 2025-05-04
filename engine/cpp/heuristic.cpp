#include <array>
#include <array>
#include <map>
#include "../../chess/chess.h"
#include <iostream>


using namespace std;
const int MATE_SCORE = 999999;


const std::array<int, 64> BPAWN_MG = {
    100, 100, 100, 100, 100, 100, 100, 100,
    176, 214, 147, 194, 189, 214, 132, 77,
    82, 88, 106, 113, 150, 146, 110, 73,
    67, 93, 83, 95, 97, 92, 99, 63,
    55, 74, 80, 89, 94, 86, 90, 55,
    55, 70, 68, 69, 76, 81, 101, 66,
    52, 84, 66, 60, 69, 99, 117, 60,
    100, 100, 100, 100, 100, 100, 100, 100
};


const std::array<int, 64> BKNIGHT_MG = {
    116, 228, 271, 270, 338, 213, 278, 191,
    225, 247, 353, 331, 321, 360, 300, 281,
    258, 354, 343, 362, 389, 428, 375, 347,
    300, 332, 325, 360, 349, 379, 339, 333,
    298, 322, 325, 321, 337, 332, 332, 303,
    287, 297, 316, 319, 327, 320, 327, 294,
    276, 259, 300, 304, 308, 322, 296, 292,
    208, 290, 257, 274, 296, 284, 293, 284
};

const std::array<int, 64> BBISHOP_MG = {
    292, 338, 254, 283, 299, 294, 337, 323,
    316, 342, 319, 319, 360, 385, 343, 295,
    342, 377, 373, 374, 368, 392, 385, 363,
    332, 338, 356, 384, 370, 380, 337, 341,
    327, 354, 353, 366, 373, 346, 345, 341,
    335, 350, 351, 347, 352, 361, 350, 344,
    333, 354, 354, 339, 344, 353, 367, 333,
    309, 341, 342, 325, 334, 332, 302, 313
};

const std::array<int, 64> BROOK_MG = {
    493, 511, 487, 515, 514, 483, 485, 495,
    493, 498, 529, 534, 546, 544, 483, 508,
    465, 490, 499, 497, 483, 519, 531, 480,
    448, 464, 476, 495, 484, 506, 467, 455,
    442, 451, 468, 470, 476, 472, 498, 454,
    441, 461, 468, 465, 478, 481, 478, 452,
    443, 472, 467, 476, 483, 500, 487, 423,
    459, 463, 470, 479, 480, 480, 446, 458
};


const std::array<int, 64> BQUEEN_MG = {
    865, 902, 922, 911, 964, 948, 933, 928,
    886, 865, 903, 921, 888, 951, 923, 940,
    902, 901, 907, 919, 936, 978, 965, 966,
    881, 885, 897, 894, 898, 929, 906, 915,
    907, 884, 899, 896, 904, 906, 912, 911,
    895, 916, 900, 902, 904, 912, 924, 917,
    874, 899, 918, 908, 915, 924, 911, 906,
    906, 899, 906, 918, 898, 890, 878, 858
};


const std::array<int, 64> BKING_MG = {
    -11, 70, 55, 31, -37, -16, 22, 22,
    37, 24, 25, 36, 16, 8, -12, -31,
    33, 26, 42, 11, 11, 40, 35, -2,
    0, -9, 1, -21, -20, -22, -15, -60,
    -25, 16, -27, -67, -81, -58, -40, -62,
    7, -2, -37, -77, -79, -60, -23, -26,
    12, 15, -13, -72, -56, -28, 15, 17,
    -6, 44, 29, -58, 8, -25, 34, 28
};

const std::array<int, 64> WPAWN_MG = {
    100, 100, 100, 100, 100, 100, 100, 100,
    52, 84, 66, 60, 69, 99, 117, 60,
    55, 70, 68, 69, 76, 81, 101, 66,
    55, 74, 80, 89, 94, 86, 90, 55,
    67, 93, 83, 95, 97, 92, 99, 63,
    82, 88, 106, 113, 150, 146, 110, 73,
    176, 214, 147, 194, 189, 214, 132, 77,
    100, 100, 100, 100, 100, 100, 100, 100
};

const std::array<int, 64> WKNIGHT_MG = {
    208, 290, 257, 274, 296, 284, 293, 284,
    276, 259, 300, 304, 308, 322, 296, 292,
    287, 297, 316, 319, 327, 320, 327, 294,
    300, 332, 325, 360, 349, 379, 339, 333,
    298, 322, 325, 321, 337, 332, 332, 303,
    258, 354, 343, 362, 389, 428, 375, 347,
    225, 247, 353, 331, 321, 360, 300, 281,
    116, 228, 271, 270, 338, 213, 278, 191
};

const std::array<int, 64> WBISHOP_MG = {
    309, 341, 342, 325, 334, 332, 302, 313,
    333, 354, 354, 339, 344, 353, 367, 333,
    335, 350, 351, 347, 352, 361, 350, 344,
    332, 338, 356, 384, 370, 380, 337, 341,
    327, 354, 353, 366, 373, 346, 345, 341,
    342, 377, 373, 374, 368, 392, 385, 363,
    316, 342, 319, 319, 360, 385, 343, 295,
    292, 338, 254, 283, 299, 294, 337, 323
};


const std::array<int, 64> WROOK_MG = {
    459, 463, 470, 479, 480, 480, 446, 458,
    443, 472, 467, 476, 483, 500, 487, 423,
    441, 461, 468, 465, 478, 481, 478, 452,
    448, 464, 476, 495, 484, 506, 467, 455,
    442, 451, 468, 470, 476, 472, 498, 454,
    465, 490, 499, 497, 483, 519, 531, 480,
    493, 498, 529, 534, 546, 544, 483, 508,
    493, 511, 487, 515, 514, 483, 485, 495
};

const std::array<int, 64> WQUEEN_MG = {
    906, 899, 906, 918, 898, 890, 878, 858,
    874, 899, 918, 908, 915, 924, 911, 906,
    895, 916, 900, 902, 904, 912, 924, 917,
    881, 885, 897, 894, 898, 929, 906, 915,
    907, 884, 899, 896, 904, 906, 912, 911,
    902, 901, 907, 919, 936, 978, 965, 966,
    886, 865, 903, 921, 888, 951, 923, 940,
    865, 902, 922, 911, 964, 948, 933, 928
};

const std::array<int, 64> WKING_MG = {
    -6, 44, 29, -58, 8, -25, 34, 28,
    12, 15, -13, -72, -56, -28, 15, 17,
    7, -2, -37, -77, -79, -60, -23, -26,
    0, -9, 1, -21, -20, -22, -15, -60,
    -25, 16, -27, -67, -81, -58, -40, -62,
    33, 26, 42, 11, 11, 40, 35, -2,
    37, 24, 25, 36, 16, 8, -12, -31,
    -11, 70, 55, 31, -37, -16, 22, 22
};

// Endgame

const std::array<int, 64> BROOK_EG = {
    506, 500, 508, 502, 504, 507, 505, 503,
    505, 506, 502, 502, 491, 497, 506, 501,
    504, 503, 499, 500, 500, 495, 496, 496,
    503, 502, 510, 500, 502, 504, 500, 505,
    505, 509, 509, 506, 504, 503, 496, 495,
    500, 503, 500, 505, 498, 498, 499, 489,
    496, 495, 502, 505, 498, 498, 491, 499,
    492, 497, 498, 496, 493, 493, 497, 480
};

const std::array<int, 64>  BPAWN_EG = {
    100, 100, 100, 100, 100, 100, 100, 100,
    277, 270, 252, 229, 240, 233, 264, 285,
    190, 197, 182, 168, 155, 150, 180, 181,
    128, 117, 108, 102, 93, 100, 110, 110,
    107, 101, 89, 85, 86, 83, 92, 91,
    96, 96, 85, 92, 88, 83, 85, 82,
    107, 99, 97, 97, 100, 89, 89, 84,
    100, 100, 100, 100, 100, 100, 100, 100
};

const std::array<int, 64> BKNIGHT_EG = {
    229, 236, 269, 250, 257, 249, 219, 188,
    252, 274, 263, 281, 273, 258, 260, 229,
    253, 264, 290, 289, 278, 275, 263, 243,
    267, 280, 299, 301, 299, 293, 285, 264,
    263, 273, 293, 301, 296, 293, 284, 261,
    258, 276, 278, 290, 287, 274, 260, 255,
    241, 259, 270, 277, 276, 262, 260, 237,
    253, 233, 258, 264, 261, 260, 234, 215
};

const std::array<int, 64> BBISHOP_EG = {
    288, 278, 287, 292, 293, 290, 287, 277,
    289, 294, 301, 288, 296, 289, 294, 281,
    292, 289, 296, 292, 296, 300, 296, 293,
    293, 302, 305, 305, 306, 302, 296, 297,
    289, 293, 304, 308, 298, 301, 291, 288,
    285, 294, 304, 303, 306, 294, 290, 280,
    285, 284, 291, 299, 300, 290, 284, 271,
    277, 292, 286, 295, 294, 288, 290, 285
};

const std::array<int, 64> BQUEEN_EG = {
    918, 937, 943, 945, 934, 926, 924, 942,
    907, 945, 946, 951, 982, 933, 928, 912,
    896, 921, 926, 967, 963, 937, 924, 915,
    926, 944, 939, 962, 983, 957, 981, 950,
    893, 949, 942, 970, 952, 956, 953, 936,
    911, 892, 933, 928, 934, 942, 934, 924,
    907, 898, 883, 903, 903, 893, 886, 888,
    886, 887, 890, 872, 916, 890, 906, 879
};

const std::array<int, 64> BKING_EG = {
    -74, -43, -23, -25, -11, 10, 1, -12,
    -18, 6, 4, 9, 7, 26, 14, 8,
    -3, 6, 10, 6, 8, 24, 27, 3,
    -16, 8, 13, 20, 14, 19, 10, -3,
    -25, -14, 13, 20, 24, 15, 1, -15,
    -27, -10, 9, 20, 23, 14, 2, -12,
    -32, -17, 4, 14, 15, 5, -10, -22,
    -55, -40, -23, -6, -20, -8, -28, -47
};

const std::array<int, 64> WROOK_EG = {
    492, 497, 498, 496, 493, 493, 497, 480,
    496, 495, 502, 505, 498, 498, 491, 499,
    500, 503, 500, 505, 498, 498, 499, 489,
    503, 502, 510, 500, 502, 504, 500, 505,
    505, 509, 509, 506, 504, 503, 496, 495,
    504, 503, 499, 500, 500, 495, 496, 496,
    505, 506, 502, 502, 491, 497, 506, 501,
    506, 500, 508, 502, 504, 507, 505, 503
};

const std::array<int, 64> WPAWN_EG = {
    100, 100, 100, 100, 100, 100, 100, 100,
    107, 99, 97, 97, 100, 89, 89, 84,
    96, 96, 85, 92, 88, 83, 85, 82,
    128, 117, 108, 102, 93, 100, 110, 110,
    107, 101, 89, 85, 86, 83, 92, 91,
    190, 197, 182, 168, 155, 150, 180, 181,
    277, 270, 252, 229, 240, 233, 264, 285,
    100, 100, 100, 100, 100, 100, 100, 100
};

const std::array<int, 64> WKNIGHT_EG = {
    253, 233, 258, 264, 261, 260, 234, 215,
    241, 259, 270, 277, 276, 262, 260, 237,
    258, 276, 278, 290, 287, 274, 260, 255,
    267, 280, 299, 301, 299, 293, 285, 264,
    263, 273, 293, 301, 296, 293, 284, 261,
    253, 264, 290, 289, 278, 275, 263, 243,
    252, 274, 263, 281, 273, 258, 260, 229,
    229, 236, 269, 250, 257, 249, 219, 188
};

const std::array<int, 64>  WBISHOP_EG = {
    277, 292, 286, 295, 294, 288, 290, 285,
    285, 284, 291, 299, 300, 290, 284, 271,
    285, 294, 304, 303, 306, 294, 290, 280,
    293, 302, 305, 305, 306, 302, 296, 297,
    289, 293, 304, 308, 298, 301, 291, 288,
    292, 289, 296, 292, 296, 300, 296, 293,
    289, 294, 301, 288, 296, 289, 294, 281,
    288, 278, 287, 292, 293, 290, 287, 277
};

const std::array<int, 64> WQUEEN_EG = {
    886, 887, 890, 872, 916, 890, 906, 879,
    907, 898, 883, 903, 903, 893, 886, 888,
    911, 892, 933, 928, 934, 942, 934, 924,
    926, 944, 939, 962, 983, 957, 981, 950,
    893, 949, 942, 970, 952, 956, 953, 936,
    896, 921, 926, 967, 963, 937, 924, 915,
    907, 945, 946, 951, 982, 933, 928, 912,
    918, 937, 943, 945, 934, 926, 924, 942
};

const std::array<int, 64> WKING_EG = {
    -55, -40, -23, -6, -20, -8, -28, -47,
    -32, -17, 4, 14, 15, 5, -10, -22,
    -27, -10, 9, 20, 23, 14, 2, -12,
    -16, 8, 13, 20, 14, 19, 10, -3,
    -25, -14, 13, 20, 24, 15, 1, -15,
    -3, 6, 10, 6, 8, 24, 27, 3,
    -18, 6, 4, 9, 7, 26, 14, 8,
    -74, -43, -23, -25, -11, 10, 1, -12
};



enum Piece {
    PAWN = 1,
    KNIGHT = 2,
    BISHOP = 3,
    ROOK = 4,
    QUEEN = 5,
    KING = 6
};

enum Color { WHITE, BLACK };

extern const std::array<int, 64> WPAWN_MG, WPAWN_EG;
extern const std::array<int, 64> WKNIGHT_MG, WKNIGHT_EG;
extern const std::array<int, 64> WBISHOP_MG, WBISHOP_EG;
extern const std::array<int, 64> WROOK_MG, WROOK_EG;
extern const std::array<int, 64> WQUEEN_MG, WQUEEN_EG;
extern const std::array<int, 64> WKING_MG, WKING_EG;

extern const std::array<int, 64> BPAWN_MG, BPAWN_EG;
extern const std::array<int, 64> BKNIGHT_MG, BKNIGHT_EG;
extern const std::array<int, 64> BBISHOP_MG, BBISHOP_EG;
extern const std::array<int, 64> BROOK_MG, BROOK_EG;
extern const std::array<int, 64> BQUEEN_MG, BQUEEN_EG;
extern const std::array<int, 64> BKING_MG, BKING_EG;

using PieceValuePair = std::pair<const std::array<int, 64>&, const std::array<int, 64>&>;

const std::map<Piece, PieceValuePair> wpiece_values = {
    {PAWN,   {WPAWN_MG, WPAWN_EG}},
    {KNIGHT, {WKNIGHT_MG, WKNIGHT_EG}},
    {BISHOP, {WBISHOP_MG, WBISHOP_EG}},
    {ROOK,   {WROOK_MG, WROOK_EG}},
    {QUEEN,  {WQUEEN_MG, WQUEEN_EG}},
    {KING,   {WKING_MG, WKING_EG}}
};

const std::map<Piece, PieceValuePair> bpiece_values = {
    {PAWN,   {BPAWN_MG, BPAWN_EG}},
    {KNIGHT, {BKNIGHT_MG, BKNIGHT_EG}},
    {BISHOP, {BBISHOP_MG, BBISHOP_EG}},
    {ROOK,   {BROOK_MG, BROOK_EG}},
    {QUEEN,  {BQUEEN_MG, BQUEEN_EG}},
    {KING,   {BKING_MG, BKING_EG}}
};

const std::map<Piece, double> mobility_weights = {
    {PAWN,   0.5},
    {KNIGHT, 4.5},
    {BISHOP, 3.0},
    {ROOK,   2.5},
    {QUEEN,  1.5},
    {KING,   0.1}
};

int W_MOBILITY        = 5;
int W_KING_SAFETY     = 10;
int W_PAWN_STRUCTURE  = 15;
int W_BISHOP_PAIR     = 40;
int W_CENTER_CONTROL  = 20;
int W_PAWN_SHELTER    = 12;
int W_ROOK_OPEN       = 15;
int W_OUTPOST         = 8;
int W_TROPISM         = 5;
int W_SPACE           = 3;
int W_THREAT          = 10;

double game_phase(chess::Board board) {
    std::map<Piece, int> phase_weights = {
        {QUEEN, 4}, {ROOK, 2}, {BISHOP, 1}, {KNIGHT, 1}
    };
<<<<<<< HEAD

    std::map<Piece, int> max_counts = {
        {QUEEN, 1}, {ROOK, 2}, {BISHOP, 2}, {KNIGHT, 2}
    };

    int max_phase = 24;
    int phase = 0;
    for (const auto& entry : phase_weights) {
        Piece piece = entry.first;
        phase += board.pieces(piece, WHITE).size() * phase_weights[piece];
        phase += board.pieces(piece, BLACK).size() * phase_weights[piece];

    }

    return std::min(1.0, static_cast<double>(phase) / max_phase);
}

double eval_pst(chess::Board board) {
    double mg = game_phase(board);
    double eg = 1.0 - mg;
    double score = 0;
    for (int sq = 0; sq < 64; ++sq) {
        if (!board.piece_at(sq)) continue;
        auto opt_piece = board.piece_at(sq);
        if (!opt_piece) continue;
        chess::Piece piece = *opt_piece;
        bool is_white = piece.color;
        int idx = sq;
        const auto& pst_mg = is_white ? wpiece_values.at(static_cast<Piece>(piece.piece_type)).first: bpiece_values.at(static_cast<Piece>(piece.piece_type)).first;
        const auto& pst_eg = is_white ? wpiece_values.at(static_cast<Piece>(piece.piece_type)).second : bpiece_values.at(static_cast<Piece>(piece.piece_type)).second;
        double value = (pst_mg[idx] * mg + pst_eg[idx] * eg);
        score += is_white ? value : -value;
    }
    return score / (5255 + 435);
}

=======
    
    std::map<Piece, int> max_counts = {
        {QUEEN, 1}, {ROOK, 2}, {BISHOP, 2}, {KNIGHT, 2}
    };

    int max_phase = 24;
    int phase = 0;
    for (const auto& entry : phase_weights) {
        Piece piece = entry.first;
        phase += board.pieces(piece, WHITE).size() * phase_weights[piece];
        phase += board.pieces(piece, BLACK).size() * phase_weights[piece];
        
    }

    return std::min(1.0, static_cast<double>(phase) / max_phase);
}

double eval_pst(chess::Board board) {
    double mg = game_phase(board);  
    double eg = 1.0 - mg;
    double score = 0;
    for (int sq = 0; sq < 64; ++sq) {
        if (!board.piece_at(sq)) continue;
        auto opt_piece = board.piece_at(sq);
        if (!opt_piece) continue;
        chess::Piece piece = *opt_piece;
        bool is_white = piece.color;
        int idx = sq;
        const auto& pst_mg = is_white ? wpiece_values.at(static_cast<Piece>(piece.piece_type)).first: bpiece_values.at(static_cast<Piece>(piece.piece_type)).first;
        const auto& pst_eg = is_white ? wpiece_values.at(static_cast<Piece>(piece.piece_type)).second : bpiece_values.at(static_cast<Piece>(piece.piece_type)).second;
        double value = (pst_mg[idx] * mg + pst_eg[idx] * eg);
        score += is_white ? value : -value;
    }
    return score / (5255 + 435);
}

>>>>>>> origin/fix_convert
double evaluate(chess::Board board) {
    if (board.is_checkmate()) {
        return board.turn == WHITE ? -MATE_SCORE : MATE_SCORE;
    }

    if (board.is_stalemate() ||
        board.is_insufficient_material() ||
        board.is_fivefold_repetition()) {
        return 0;
    }

    double total = 0;
    total += eval_pst(board);
    // total += W_MOBILITY * eval_mobility(board);
    // total += W_KING_SAFETY * eval_king_safety(board);
    // total += eval_pawn_structure(board);
    // total += eval_bishop_pair(board);
    // total += W_CENTER_CONTROL * eval_center_control(board);
    // total += eval_rook_open(board);
    // total += eval_outposts(board);
    // total += eval_tropism(board);
    // total += eval_space(board);
    // total += eval_threats(board);

    return total;
}