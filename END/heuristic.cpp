#include "heuristic.h"
#include <numeric> // For std::accumulate if needed, though not directly here
#include <iostream> // For debugging (optional)
#include <array>
#include <map>
#include "chess/chess.h"
#include <iostream>
#include <cstdint>

namespace chess_eval {
    // --- Piece-Square Tables (PSTs) Data ---
    // Black Middle Game
    const std::array<int, 64> BPAWN_MG = {
        {
            100, 100, 100, 100, 100, 100, 100, 100,
            176, 214, 147, 194, 189, 214, 132, 77,
            82, 88, 106, 113, 150, 146, 110, 73,
            67, 93, 83, 95, 97, 92, 99, 63,
            55, 74, 80, 89, 94, 86, 90, 55,
            55, 70, 68, 69, 76, 81, 101, 66,
            52, 84, 66, 60, 69, 99, 117, 60,
            100, 100, 100, 100, 100, 100, 100, 100
        }
    };
    const std::array<int, 64> BKNIGHT_MG = {
        {
            116, 228, 271, 270, 338, 213, 278, 191,
            225, 247, 353, 331, 321, 360, 300, 281,
            258, 354, 343, 362, 389, 428, 375, 347,
            300, 332, 325, 360, 349, 379, 339, 333,
            298, 322, 325, 321, 337, 332, 332, 303,
            287, 297, 316, 319, 327, 320, 327, 294,
            276, 259, 300, 304, 308, 322, 296, 292,
            208, 290, 257, 274, 296, 284, 293, 284
        }
    };
    const std::array<int, 64> BBISHOP_MG = {
        {
            292, 338, 254, 283, 299, 294, 337, 323,
            316, 342, 319, 319, 360, 385, 343, 295,
            342, 377, 373, 374, 368, 392, 385, 363,
            332, 338, 356, 384, 370, 380, 337, 341,
            327, 354, 353, 366, 373, 346, 345, 341,
            335, 350, 351, 347, 352, 361, 350, 344,
            333, 354, 354, 339, 344, 353, 367, 333,
            309, 341, 342, 325, 334, 332, 302, 313
        }
    };
    const std::array<int, 64> BROOK_MG = {
        {
            493, 511, 487, 515, 514, 483, 485, 495,
            493, 498, 529, 534, 546, 544, 483, 508,
            465, 490, 499, 497, 483, 519, 531, 480,
            448, 464, 476, 495, 484, 506, 467, 455,
            442, 451, 468, 470, 476, 472, 498, 454,
            441, 461, 468, 465, 478, 481, 478, 452,
            443, 472, 467, 476, 483, 500, 487, 423,
            459, 463, 470, 479, 480, 480, 446, 458
        }
    };
    const std::array<int, 64> BQUEEN_MG = {
        {
            865, 902, 922, 911, 964, 948, 933, 928,
            886, 865, 903, 921, 888, 951, 923, 940,
            902, 901, 907, 919, 936, 978, 965, 966,
            881, 885, 897, 894, 898, 929, 906, 915,
            907, 884, 899, 896, 904, 906, 912, 911,
            895, 916, 900, 902, 904, 912, 924, 917,
            874, 899, 918, 908, 915, 924, 911, 906,
            906, 899, 906, 918, 898, 890, 878, 858
        }
    };
    const std::array<int, 64> BKING_MG = {
        {
            -11, 70, 55, 31, -37, -16, 22, 22,
            37, 24, 25, 36, 16, 8, -12, -31,
            33, 26, 42, 11, 11, 40, 35, -2,
            0, -9, 1, -21, -20, -22, -15, -60,
            -25, 16, -27, -67, -81, -58, -40, -62,
            7, -2, -37, -77, -79, -60, -23, -26,
            12, 15, -13, -72, -56, -28, 15, 17,
            -6, 44, 29, -58, 8, -25, 34, 28
        }
    };

    // Black End Game
    const std::array<int, 64> BPAWN_EG = {
        {
            100, 100, 100, 100, 100, 100, 100, 100,
            277, 270, 252, 229, 240, 233, 264, 285,
            190, 197, 182, 168, 155, 150, 180, 181,
            128, 117, 108, 102, 93, 100, 110, 110,
            107, 101, 89, 85, 86, 83, 92, 91,
            96, 96, 85, 92, 88, 83, 85, 82,
            107, 99, 97, 97, 100, 89, 89, 84,
            100, 100, 100, 100, 100, 100, 100, 100
        }
    };
    const std::array<int, 64> BKNIGHT_EG = {
        {
            229, 236, 269, 250, 257, 249, 219, 188,
            252, 274, 263, 281, 273, 258, 260, 229,
            253, 264, 290, 289, 278, 275, 263, 243,
            267, 280, 299, 301, 299, 293, 285, 264,
            263, 273, 293, 301, 296, 293, 284, 261,
            258, 276, 278, 290, 287, 274, 260, 255,
            241, 259, 270, 277, 276, 262, 260, 237,
            253, 233, 258, 264, 261, 260, 234, 215
        }
    };
    const std::array<int, 64> BBISHOP_EG = {
        {
            288, 278, 287, 292, 293, 290, 287, 277,
            289, 294, 301, 288, 296, 289, 294, 281,
            292, 289, 296, 292, 296, 300, 296, 293,
            293, 302, 305, 305, 306, 302, 296, 297,
            289, 293, 304, 308, 298, 301, 291, 288,
            285, 294, 304, 303, 306, 294, 290, 280,
            285, 284, 291, 299, 300, 290, 284, 271,
            277, 292, 286, 295, 294, 288, 290, 285
        }
    };
    const std::array<int, 64> BROOK_EG = {
        {
            506, 500, 508, 502, 504, 507, 505, 503,
            505, 506, 502, 502, 491, 497, 506, 501,
            504, 503, 499, 500, 500, 495, 496, 496,
            503, 502, 510, 500, 502, 504, 500, 505,
            505, 509, 509, 506, 504, 503, 496, 495,
            500, 503, 500, 505, 498, 498, 499, 489,
            496, 495, 502, 505, 498, 498, 491, 499,
            492, 497, 498, 496, 493, 493, 497, 480
        }
    };
    const std::array<int, 64> BQUEEN_EG = {
        {
            918, 937, 943, 945, 934, 926, 924, 942,
            907, 945, 946, 951, 982, 933, 928, 912,
            896, 921, 926, 967, 963, 937, 924, 915,
            926, 944, 939, 962, 983, 957, 981, 950,
            893, 949, 942, 970, 952, 956, 953, 936,
            911, 892, 933, 928, 934, 942, 934, 924,
            907, 898, 883, 903, 903, 893, 886, 888,
            886, 887, 890, 872, 916, 890, 906, 879
        }
    };
    const std::array<int, 64> BKING_EG = {
        {
            -74, -43, -23, -25, -11, 10, 1, -12,
            -18, 6, 4, 9, 7, 26, 14, 8,
            -3, 6, 10, 6, 8, 24, 27, 3,
            -16, 8, 13, 20, 14, 19, 10, -3,
            -25, -14, 13, 20, 24, 15, 1, -15,
            -27, -10, 9, 20, 23, 14, 2, -12,
            -32, -17, 4, 14, 15, 5, -10, -22,
            -55, -40, -23, -6, -20, -8, -28, -47
        }
    };

    // White Middle Game
    const std::array<int, 64> WPAWN_MG = {
        {
            100, 100, 100, 100, 100, 100, 100, 100,
            52, 84, 66, 60, 69, 99, 117, 60,
            55, 70, 68, 69, 76, 81, 101, 66,
            55, 74, 80, 89, 94, 86, 90, 55,
            67, 93, 83, 95, 97, 92, 99, 63,
            82, 88, 106, 113, 150, 146, 110, 73,
            176, 214, 147, 194, 189, 214, 132, 77,
            100, 100, 100, 100, 100, 100, 100, 100
        }
    };
    const std::array<int, 64> WKNIGHT_MG = {
        {
            208, 290, 257, 274, 296, 284, 293, 284,
            276, 259, 300, 304, 308, 322, 296, 292,
            287, 297, 316, 319, 327, 320, 327, 294,
            300, 332, 325, 360, 349, 379, 339, 333,
            298, 322, 325, 321, 337, 332, 332, 303,
            258, 354, 343, 362, 389, 428, 375, 347,
            225, 247, 353, 331, 321, 360, 300, 281,
            116, 228, 271, 270, 338, 213, 278, 191
        }
    };
    const std::array<int, 64> WBISHOP_MG = {
        {
            309, 341, 342, 325, 334, 332, 302, 313,
            333, 354, 354, 339, 344, 353, 367, 333,
            335, 350, 351, 347, 352, 361, 350, 344,
            332, 338, 356, 384, 370, 380, 337, 341,
            327, 354, 353, 366, 373, 346, 345, 341,
            342, 377, 373, 374, 368, 392, 385, 363,
            316, 342, 319, 319, 360, 385, 343, 295,
            292, 338, 254, 283, 299, 294, 337, 323
        }
    };
    const std::array<int, 64> WROOK_MG = {
        {
            459, 463, 470, 479, 480, 480, 446, 458,
            443, 472, 467, 476, 483, 500, 487, 423,
            441, 461, 468, 465, 478, 481, 478, 452,
            448, 464, 476, 495, 484, 506, 467, 455,
            442, 451, 468, 470, 476, 472, 498, 454,
            465, 490, 499, 497, 483, 519, 531, 480,
            493, 498, 529, 534, 546, 544, 483, 508,
            493, 511, 487, 515, 514, 483, 485, 495
        }
    };
    const std::array<int, 64> WQUEEN_MG = {
        {
            906, 899, 906, 918, 898, 890, 878, 858,
            874, 899, 918, 908, 915, 924, 911, 906,
            895, 916, 900, 902, 904, 912, 924, 917,
            881, 885, 897, 894, 898, 929, 906, 915,
            907, 884, 899, 896, 904, 906, 912, 911,
            902, 901, 907, 919, 936, 978, 965, 966,
            886, 865, 903, 921, 888, 951, 923, 940,
            865, 902, 922, 911, 964, 948, 933, 928
        }
    };
    const std::array<int, 64> WKING_MG = {
        {
            -6, 44, 29, -58, 8, -25, 34, 28,
            12, 15, -13, -72, -56, -28, 15, 17,
            7, -2, -37, -77, -79, -60, -23, -26,
            0, -9, 1, -21, -20, -22, -15, -60,
            -25, 16, -27, -67, -81, -58, -40, -62,
            33, 26, 42, 11, 11, 40, 35, -2,
            37, 24, 25, 36, 16, 8, -12, -31,
            -11, 70, 55, 31, -37, -16, 22, 22
        }
    };

    // White End Game
    const std::array<int, 64> WPAWN_EG = {
        {
            100, 100, 100, 100, 100, 100, 100, 100,
            107, 99, 97, 97, 100, 89, 89, 84,
            96, 96, 85, 92, 88, 83, 85, 82,
            128, 117, 108, 102, 93, 100, 110, 110,
            107, 101, 89, 85, 86, 83, 92, 91,
            190, 197, 182, 168, 155, 150, 180, 181,
            277, 270, 252, 229, 240, 233, 264, 285,
            100, 100, 100, 100, 100, 100, 100, 100
        }
    };
    const std::array<int, 64> WKNIGHT_EG = {
        {
            253, 233, 258, 264, 261, 260, 234, 215,
            241, 259, 270, 277, 276, 262, 260, 237,
            258, 276, 278, 290, 287, 274, 260, 255,
            267, 280, 299, 301, 299, 293, 285, 264,
            263, 273, 293, 301, 296, 293, 284, 261,
            253, 264, 290, 289, 278, 275, 263, 243,
            252, 274, 263, 281, 273, 258, 260, 229,
            229, 236, 269, 250, 257, 249, 219, 188
        }
    };
    const std::array<int, 64> WBISHOP_EG = {
        {
            277, 292, 286, 295, 294, 288, 290, 285,
            285, 284, 291, 299, 300, 290, 284, 271,
            285, 294, 304, 303, 306, 294, 290, 280,
            293, 302, 305, 305, 306, 302, 296, 297,
            289, 293, 304, 308, 298, 301, 291, 288,
            292, 289, 296, 292, 296, 300, 296, 293,
            289, 294, 301, 288, 296, 289, 294, 281,
            288, 278, 287, 292, 293, 290, 287, 277
        }
    };
    const std::array<int, 64> WROOK_EG = {
        {
            492, 497, 498, 496, 493, 493, 497, 480,
            496, 495, 502, 505, 498, 498, 491, 499,
            500, 503, 500, 505, 498, 498, 499, 489,
            503, 502, 510, 500, 502, 504, 500, 505,
            505, 509, 509, 506, 504, 503, 496, 495,
            504, 503, 499, 500, 500, 495, 496, 496,
            505, 506, 502, 502, 491, 497, 506, 501,
            506, 500, 508, 502, 504, 507, 505, 503
        }
    };
    const std::array<int, 64> WQUEEN_EG = {
        {
            886, 887, 890, 872, 916, 890, 906, 879,
            907, 898, 883, 903, 903, 893, 886, 888,
            911, 892, 933, 928, 934, 942, 934, 924,
            926, 944, 939, 962, 983, 957, 981, 950,
            893, 949, 942, 970, 952, 956, 953, 936,
            896, 921, 926, 967, 963, 937, 924, 915,
            907, 945, 946, 951, 982, 933, 928, 912,
            918, 937, 943, 945, 934, 926, 924, 942
        }
    };
    const std::array<int, 64> WKING_EG = {
        {
            -55, -40, -23, -6, -20, -8, -28, -47,
            -32, -17, 4, 14, 15, 5, -10, -22,
            -27, -10, 9, 20, 23, 14, 2, -12,
            -16, 8, 13, 20, 14, 19, 10, -3,
            -25, -14, 13, 20, 24, 15, 1, -15,
            -3, 6, 10, 6, 8, 24, 27, 3,
            -18, 6, 4, 9, 7, 26, 14, 8,
            -74, -43, -23, -25, -11, 10, 1, -12
        }
    };

    // Piece Values Lookup
    const std::unordered_map<chess::PieceType, PieceTables> W_PIECE_VALUES = {
        {chess::PAWN, {WPAWN_MG, WPAWN_EG}},
        {chess::KNIGHT, {WKNIGHT_MG, WKNIGHT_EG}},
        {chess::BISHOP, {WBISHOP_MG, WBISHOP_EG}},
        {chess::ROOK, {WROOK_MG, WROOK_EG}},
        {chess::QUEEN, {WQUEEN_MG, WQUEEN_EG}},
        {chess::KING, {WKING_MG, WKING_EG}}
    };

    const std::unordered_map<chess::PieceType, PieceTables> B_PIECE_VALUES = {
        {chess::PAWN, {BPAWN_MG, BPAWN_EG}},
        {chess::KNIGHT, {BKNIGHT_MG, BKNIGHT_EG}},
        {chess::BISHOP, {BBISHOP_MG, BBISHOP_EG}},
        {chess::ROOK, {BROOK_MG, BROOK_EG}},
        {chess::QUEEN, {BQUEEN_MG, BQUEEN_EG}},
        {chess::KING, {BKING_MG, BKING_EG}}
    };

    const std::unordered_map<chess::PieceType, int> PIECE_MATERIAL_VALUES = {
        {chess::PAWN, 1},
        {chess::KNIGHT, 3},
        {chess::BISHOP, 3},
        {chess::ROOK, 5},
        {chess::QUEEN, 9},
        {chess::KING, 0} // King material value is often not counted or handled by PSTs
    };

    const std::unordered_map<chess::PieceType, double> MOBILITY_PIECE_FACTORS = {
        {chess::PAWN, 0.0},
        {chess::KNIGHT, 4.5},
        {chess::BISHOP, 3.0},
        {chess::ROOK, 1.0},
        {chess::QUEEN, 1.0},
        {chess::KING, 0.0}
    };



    int score(chess::Board &board) {
        if (board.is_checkmate()) {
            return MATE_SCORE * (board.turn == chess::BLACK ? 1 : -1);
        }
        if (board.is_stalemate() || board.is_insufficient_material() || board.is_fivefold_repetition()) {
            return 0;
        }
        // Additional draw conditions from your C++ library
        if (board.is_seventyfive_moves() ||
            (board.can_claim_fifty_moves() && board.is_fifty_moves()) || /* Assuming you want to auto-claim for eval */
            (board.can_claim_threefold_repetition() && board.is_repetition(3)) /* Assuming auto-claim for eval */) {
            return 0;
        }


        double eval_score = calculate_score(board);
        return eval_score * (board.turn == chess::WHITE ? 1 : 1);
        // Or make sure calculate_score returns from white's PoV
    }

    int calculate_score(const chess::Board &board) {
        double mid_game_weight = 5255.0; // Using double for precision in weights
        double end_game_weight = 435.0;
        double current_score = 0.0;

        int total_material_sum = 0;
        std::unordered_map<chess::Square, chess::Piece> piece_map = board.piece_map();

        for (const auto &pair: piece_map) {
            chess::Square square = pair.first;
            chess::Piece piece = pair.second;
            if (PIECE_MATERIAL_VALUES.count(piece.piece_type)) {
                total_material_sum += PIECE_MATERIAL_VALUES.at(piece.piece_type);
            }
        }

        if (total_material_sum <= 20) {
            // Endgame phase check
            mid_game_weight = 0.0;
            // end_game_weight remains as is or could be scaled to 1.0 if mid_game_weight is 0
            // The original Python code implies end_game_weight is still 435.
        }

        // If both weights are zero (e.g. total_material_sum <= 20 and end_game_weight was also 0),
        // avoid division by zero later.
        double scalar = mid_game_weight + end_game_weight;
        if (scalar == 0.0) {
            // Should only happen if initial weights are 0 or logic flaw
            scalar = 1.0; // Prevent division by zero, though this indicates an issue.
        }


        for (const auto &pair: piece_map) {
            chess::Square square = pair.first;
            chess::Piece piece = pair.second;
            chess::PieceType piece_type = piece.piece_type;
            chess::Color color = piece.color;

            double piece_pst_score = 0.0;

            if (color == chess::WHITE) {
                if (W_PIECE_VALUES.count(piece_type)) {
                    const auto &tables = W_PIECE_VALUES.at(piece_type);
                    if (square >= 0 && square < 64) {
                        piece_pst_score = static_cast<double>(tables.mg_table[square]) * mid_game_weight +
                                          static_cast<double>(tables.eg_table[square]) * end_game_weight;
                    } else {
                        std::cerr << "Lỗi: square index " << square << " ngoài giới hạn trong calculate_score cho quân "
                                << piece.symbol() << std::endl;
                        // Xử lý lỗi, ví dụ bỏ qua quân này hoặc trả về giá trị an toàn
                    }
                }
                current_score += piece_pst_score;
            } else {
                // chess::BLACK
                if (B_PIECE_VALUES.count(piece_type)) {
                    const auto &tables = B_PIECE_VALUES.at(piece_type);
                    if (square >= 0 && square < 64) {
                        piece_pst_score = static_cast<double>(tables.mg_table[square]) * mid_game_weight +
                                          static_cast<double>(tables.eg_table[square]) * end_game_weight;
                    }
                }
                current_score -= piece_pst_score; // Subtract for black pieces
            }
        }

        return static_cast<int>(current_score / scalar);
    }


    int mobility(chess::Board &board) {
        // Takes non-const ref due to pseudo_legal_moves potentially
        std::unordered_map<chess::PieceType, int> move_counts = {
            {chess::PAWN, 0}, {chess::KNIGHT, 0}, {chess::BISHOP, 0},
            {chess::ROOK, 0}, {chess::QUEEN, 0}, {chess::KING, 0}
        };

        // The C++ pseudo_legal_moves() returns a generator object.
        for (const chess::Move &move: board.generate_pseudo_legal_moves()) {
            // Iterate through the generator
            std::optional<chess::Piece> piece_opt = board.piece_at(move.from_square);
            if (piece_opt) {
                chess::PieceType pt = piece_opt->piece_type;
                if (move_counts.count(pt)) {
                    move_counts[pt]++;
                }
            }
        }

        double mobility_score = 0.0;
        int pawns_count = 0;

        if (board.turn == chess::WHITE) {
            pawns_count = board.pieces(chess::PAWN, chess::WHITE).size();
            if (MOBILITY_PIECE_FACTORS.count(chess::KNIGHT))
                mobility_score += static_cast<double>(move_counts[chess::KNIGHT]) * MOBILITY_PIECE_FACTORS.
                        at(chess::KNIGHT) * pawns_count;
            if (MOBILITY_PIECE_FACTORS.count(chess::BISHOP))
                mobility_score += static_cast<double>(move_counts[chess::BISHOP]) * MOBILITY_PIECE_FACTORS.
                        at(chess::BISHOP) * (11 - pawns_count);
            if (MOBILITY_PIECE_FACTORS.count(chess::QUEEN))
                mobility_score += static_cast<double>(move_counts[chess::QUEEN]) * MOBILITY_PIECE_FACTORS.at(
                    chess::QUEEN);
            if (MOBILITY_PIECE_FACTORS.count(chess::ROOK))
                mobility_score += static_cast<double>(move_counts[chess::ROOK]) * MOBILITY_PIECE_FACTORS.
                        at(chess::ROOK);
        } else {
            // chess::BLACK
            pawns_count = board.pieces(chess::BLACK, chess::BLACK).size();
            if (MOBILITY_PIECE_FACTORS.count(chess::KNIGHT))
                mobility_score -= static_cast<double>(move_counts[chess::KNIGHT]) * MOBILITY_PIECE_FACTORS.
                        at(chess::KNIGHT) * pawns_count;
            if (MOBILITY_PIECE_FACTORS.count(chess::BISHOP))
                mobility_score -= static_cast<double>(move_counts[chess::BISHOP]) * MOBILITY_PIECE_FACTORS.
                        at(chess::BISHOP) * (11 - pawns_count);
            if (MOBILITY_PIECE_FACTORS.count(chess::QUEEN))
                mobility_score -= static_cast<double>(move_counts[chess::QUEEN]) * MOBILITY_PIECE_FACTORS.at(
                    chess::QUEEN);
            if (MOBILITY_PIECE_FACTORS.count(chess::ROOK))
                mobility_score -= static_cast<double>(move_counts[chess::ROOK]) * MOBILITY_PIECE_FACTORS.
                        at(chess::ROOK);
        }

        return static_cast<int>(mobility_score);
    }
}
