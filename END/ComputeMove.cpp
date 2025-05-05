#include <climits>
#include <vector>
#include <algorithm>
#include <iostream>
#include <ctime>
#include <stdexcept>
#include <fstream>
#include "heuristic.cpp"

const int MATE_THRESHOLD =  999000000;


//chess::Move killer_move[20][2];
int history_move[7][2][64] = {};

// MVV-LVA TABLE (Most Valuable Victim - Least Valuable Aggressor)
int MVV_LVA[7][7] = {
    {0, 0, 0, 0, 0, 0, 0},    // victim NONE
    {0, 15, 14, 13, 12, 11, 10}, // victim P
    {0, 25, 24, 23, 22, 21, 20}, // victim N
    {0, 35, 34, 33, 32, 31, 30}, // victim B
    {0, 45, 44, 43, 42, 41, 40}, // victim R
    {0, 55, 54, 53, 52, 51, 50}, // victim Q
    {0, 0, 0, 0, 0, 0, 0}     // victim K
};

const int MVV_LVA_OFFSET = 1000000;

int move_ordering(chess::Board board, chess::Move move) {
    int move_score = 0;
     chess::Square to_sq   = move.to_square;
     chess::Square from_sq = move.from_square;

     if (move.promotion != std::nullopt) {
         return (board.turn == chess::WHITE)
             ? std::numeric_limits<int>::max()
             : std::numeric_limits<int>::min();
     }

    //  // 2. Capture move
    //  if (board.is_capture(move)) {
    //      move_score += MVV_LVA_OFFSET;

    //      int victim;
    //      if (board.is_en_passant(move)) {
    //          victim = PAWN;  // tốt bị ăn en passant
    //      } else {
    //          std::optional<chess::PieceType> victim = board.piece_type_at(to_sq);
    //      }

    //      std::optional<chess::PieceType> attacker = board.piece_type_at(from_sq);

    //      move_score += MVV_LVA[victim][attacker];
    //  }

    return move_score;
}





std::vector<chess::Move> get_ordered_moves(chess::Board board) {
    std::vector<chess::Move> legal_moves = board.generate_legal_moves();
    std::sort(legal_moves.begin(), legal_moves.end(), [&](const chess::Move &a, const chess::Move &b) {
        int score_a = move_ordering(board, a);
        int score_b = move_ordering(board, b);
        return board.turn == chess::WHITE ? (score_a > score_b) : (score_a < score_b);
    });

    return legal_moves;
}


double minimax(int depth,
    chess::Board board,
    double alpha,
    double beta,
    bool is_maximising_player) {

    if (board.is_checkmate()) {
        return is_maximising_player ? -MATE_SCORE : MATE_SCORE;
    }
    if (board.is_game_over()) {
        return 0.0;
    }

    // Depth limit
    if (depth == 0) {
        return evaluate(board);
    }

    if (is_maximising_player) {
        double best_value = -std::numeric_limits<double>::infinity();
        std::vector<chess::Move> moves = get_ordered_moves(board);
        for (chess::Move move : moves) {
            board.push(move);
            double curr_value = minimax(depth - 1, board, alpha, beta, false);

            if (curr_value > MATE_THRESHOLD) {
                curr_value -= 1;
            } else if (curr_value < -MATE_THRESHOLD) {
                curr_value += 1;
            }

            best_value = std::max(best_value, curr_value);
            board.pop();

            alpha = std::max(alpha, best_value);
            if (beta <= alpha) {
                break;
            }
        }
        return best_value;
    } else {
        double best_value = std::numeric_limits<double>::infinity();
        std::vector<chess::Move> moves = get_ordered_moves(board);
        for (chess::Move move : moves) {
            board.push(move);
            double curr_value = minimax(depth - 1, board, alpha, beta, true);

            if (curr_value > MATE_THRESHOLD) {
                curr_value -= 1;
            } else if (curr_value < -MATE_THRESHOLD) {
                curr_value += 1;
            }

            best_value = std::min(best_value, curr_value);
            board.pop();

            beta = std::min(beta, best_value);
            if (beta <= alpha) {
                break;
            }
        }
        return best_value;
    }
}

chess::Move minimax_root(int depth, chess::Board board) {
    bool maximize = board.turn == chess::WHITE;
    double best_move = maximize ? -std::numeric_limits<double>::infinity() : std::numeric_limits<double>::infinity();
    chess::Move best_move_found = chess::Move(0, 0);

    std::vector<chess::Move> moves = get_ordered_moves(board);

    for (chess::Move move : moves) {
        board.push(move);
        double value;

        if (board.can_claim_draw()) {
            value = 0.0;
        } else {
            value = minimax(depth - 1, board, -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::infinity(), !maximize);
        }
        board.pop();

        if (maximize && value >= best_move) {
            best_move = value;
            best_move_found = move;
        } else if (!maximize && value <= best_move) {
            best_move = value;
            best_move_found = move;
        }
    }

    return best_move_found;
}

chess::Move next_move(int depth, chess::Board board) {
    return minimax_root(depth, board);
}

chess::Move get_best_move(chess::Board& board, int time_limit = 200) {
    std::cout << "\n\nThinking..." << std::endl;
    std::time_t start = std::time(nullptr);

    chess::Move best_move = chess::Move(0,0);
    // try {
    //     std::ifstream file("data/final-book.bin", std::ios::binary);
    //     if (file.is_open()) {
    //         std::vector<chess::Move> root_moves = polyglot_reader.find_all(board);
    //         if (!root_moves.empty()) {
    //             best_move = root_moves[0];  // Chọn move đầu tiên từ polyglot book
    //             return best_move;
    //         }
    //     }
    // } catch (const std::exception& e) {
    //     std::cerr << "Polyglot Error: " << e.what() << std::endl;
    // }

    int max_depth = 15;
    int depth = 1;
    while (std::difftime(std::time(nullptr), start) < time_limit && depth < max_depth) {
        best_move = next_move(depth, board);
        std::cout << "Using heuristic for depth " << depth << std::endl;

        if (std::difftime(std::time(nullptr), start) >= time_limit) {
            break;
        }
        depth++;
    }

    std::time_t end = std::time(nullptr);
    std::cout << "\nRuntime: " << std::difftime(end, start) << "s" << std::endl;

    return best_move;
}