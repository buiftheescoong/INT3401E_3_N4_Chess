#include <climits>
#include <vector>
#include <algorithm>
#include <iostream>
#include <ctime>
#include <stdexcept>
#include <fstream> 
#include "heuristic.cpp"



std::vector<std::vector<chess::Move>> killer_move(64, std::vector<chess::Move>(2, chess::Move(0, 0)));

int history_move[7][2][64] = {}; // piece x color x square


int MVV_LVA[7][7] = {
    {0, 0, 0, 0, 0, 0, 0},
    {0, 15, 14, 13, 12, 11, 10},
    {0, 25, 24, 23, 22, 21, 20},
    {0, 35, 34, 33, 32, 31, 30},
    {0, 45, 44, 43, 42, 41, 40},
    {0, 55, 54, 53, 52, 51, 50},
    {0, 0, 0, 0, 0, 0, 0}
};

const int MVV_LVA_OFFSET = 1000000;

int move_ordering(chess::Board board, chess::Move move, int depth) {

    int move_score = 0;
    int to_square = move.to_square;
    int from_square = move.from_square;

    if (board.is_capture(move)) {
        move_score += MVV_LVA_OFFSET;
        Piece victim, attacker;
        if (board.is_en_passant(move)) {
            victim = PAWN; // Ensure PAWN is properly constructed as a Piece
        } else {
            if (auto optional_victim = board.piece_at(to_square)) {
                chess::Piece ptmp = *optional_victim;
                victim = Piece(ptmp.piece_type);
            } else {
                throw std::runtime_error("Invalid move: no piece at the target square.");
            }
        }
        attacker = Piece((*board.piece_at(from_square)).piece_type);
        move_score += MVV_LVA[victim][attacker];
    } else {
        if (depth < 64) {
            if (move == killer_move[depth][0])
                move_score = MVV_LVA_OFFSET - 100;
            else if (move == killer_move[depth][1])
                move_score = MVV_LVA_OFFSET - 200;
            else {
                if (auto optional_from_piece = board.piece_at(from_square)) {
                    chess::Piece from_piece = *optional_from_piece;
                    int piece = from_piece.piece_type;
                    int color = from_piece.color;
                    move_score += history_move[piece][color][to_square];
                }
            }
        }
    }

    return move_score;
}

double quiescence_search(chess::Board& board, double alpha, double beta, bool is_maximising_player) {
    double stand_pat = evaluate(board);
    if (is_maximising_player) {
        if (stand_pat >= beta) return beta;
        if (stand_pat > alpha) alpha = stand_pat;
    } else {
        if (stand_pat <= alpha) return alpha;
        if (stand_pat < beta) beta = stand_pat;
    }

    std::vector<chess::Move> captures;
    for (auto& move : board.legal_moves()) {
        if (board.is_capture(move))
            captures.push_back(move);
    }

    std::sort(captures.begin(), captures.end(), [&](const chess::Move& a, const chess::Move& b) {
        return move_ordering(board, a, 0) > move_ordering(board, b, 0);
    });

    for (auto& move : captures) {
        board.push(move);
        double score = quiescence_search(board, alpha, beta, !is_maximising_player);
        board.pop();

        if (is_maximising_player) {
            if (score > alpha) alpha = score;
        } else {
            if (score < beta) beta = score;
        }

        if (beta <= alpha) break;
    }

    return is_maximising_player ? alpha : beta;
}



std::vector<chess::Move> get_ordered_moves(chess::Board& board, int depth) {
    std::vector<chess::Move> legal_moves = board.legal_moves();
    std::sort(legal_moves.begin(), legal_moves.end(), [&](const chess::Move &a, const chess::Move &b) {
        int score_a = move_ordering(board, a, depth);
        int score_b = move_ordering(board, b, depth);
        return score_a > score_b;
    });
    return legal_moves;
}

double minimax(int depth, chess::Board& board, double alpha, double beta, bool is_maximising_player) {
    if (board.is_checkmate()) return is_maximising_player ? -MATE_SCORE : MATE_SCORE;
    if (board.is_game_over()) return 0.0;
    if (depth == 0) return quiescence_search(board, alpha, beta, is_maximising_player);

    // === Null Move Pruning ===
    if (depth >= 3 && !board.is_check() && is_maximising_player) {
        board.push(chess::Move::null());
        double score = -minimax(depth - 1 - 2, board, -beta, -beta + 1, false);
        board.pop();

        if (score >= beta) return beta;  // Fail-hard beta cutoff
    }

    double best_value = is_maximising_player ? -INFINITY : INFINITY;
    std::vector<chess::Move> moves = get_ordered_moves(board, depth);

    for (chess::Move move : moves) {
        board.push(move);
        double val = minimax(depth - 1, board, alpha, beta, !is_maximising_player);
        board.pop();

        if (is_maximising_player) {
            best_value = std::max(best_value, val);
            alpha = std::max(alpha, best_value);
        } else {
            best_value = std::min(best_value, val);
            beta = std::min(beta, best_value);
        }

        if (beta <= alpha) {
            // Update killer move if this move caused beta cutoff and is not a capture
            if (!board.is_capture(move) && depth < 64) {
                if (killer_move[depth][0] != move) {
                    killer_move[depth][1] = killer_move[depth][0];
                    killer_move[depth][0] = move;
                }
            }
        
            // Also update history heuristic
            if (!board.is_capture(move)) {
                if (auto optional_from_piece = board.piece_at(move.from_square)) {
                    chess::Piece from_piece = *optional_from_piece;
                    int piece = from_piece.piece_type;
                    int color = from_piece.color;
                    history_move[piece][color][move.to_square] += depth * depth;
                }
            }
        
            break;
        }
        
    }

    return best_value;
}


chess::Move minimax_root(int depth, chess::Board& board) {
    bool maximize = board.turn == chess::WHITE;
    double best_score = maximize ? -INFINITY : INFINITY;
    chess::Move best_move = chess::Move(0, 0);
    std::vector<chess::Move> moves = get_ordered_moves(board, depth);

    for (chess::Move move : moves) {
        board.push(move);
        double score = board.can_claim_draw() ? 0.0 : minimax(depth - 1, board, -INFINITY, INFINITY, !maximize);
        board.pop();

        if ((maximize && score > best_score) || (!maximize && score < best_score)) {
            best_score = score;
            best_move = move;
        }
    }

    return best_move;
}

chess::Move get_best_move(chess::Board& board, int time_limit = 20) {
    std::cout << "\n\nThinking..." << std::endl;
    std::time_t start = std::time(nullptr);

    chess::Move best_move = chess::Move(0,0);
    int depth = 1, max_depth = 8;
    while (std::difftime(std::time(nullptr), start) < time_limit && depth <= max_depth) {
        best_move = minimax_root(depth, board);
        std::cout << "Using heuristic for depth " << depth << std::endl;
        if (std::difftime(std::time(nullptr), start) >= time_limit) break;
        depth++;
    }

    std::cout << "\nRuntime: " << std::difftime(std::time(nullptr), start) << "s" << std::endl;
    return best_move;
}
