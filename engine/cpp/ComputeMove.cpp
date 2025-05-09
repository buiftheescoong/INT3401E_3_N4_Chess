#include <climits>
#include <vector>
#include <algorithm>
#include <iostream>
#include <ctime>
#include <stdexcept>
#include <fstream> 
#include "heuristic.cpp"
#include "TranspositionTable.cpp"
#include "ZobristHashing.cpp"
#include <chrono>


TranspositionTable transposition_table;
ZobristHashing zobrist;
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

double quiescence_search(chess::Board& board, double alpha, double beta, bool is_maximising_player, int depth) {
    double stand_pat = is_maximising_player *  evaluate(board);
    
    if (stand_pat >= beta) return beta;
    
    if (stand_pat > alpha) alpha = stand_pat;
    if (depth == 0) {
        return stand_pat;
    }

    std::vector<chess::Move> captures;
    for (auto& move : board.generate_legal_moves()) {
        if (board.is_capture(move))
            captures.push_back(move);
    }

    // std::sort(captures.begin(), captures.end(), [&](const chess::Move& a, const chess::Move& b) {
    //     return move_ordering(board, a, 0) > move_ordering(board, b, 0);
    // });

    for (auto& move : captures) {
        board.push(move);
        double score = -quiescence_search(board, -beta, -alpha, !is_maximising_player, depth - 1);
        board.pop();

       
        if (score >= beta) return beta;
       
        if (score > alpha) alpha = score;
    }

    return alpha;
}



std::vector<chess::Move> get_ordered_moves(chess::Board& board, int depth) {
    std::vector<chess::Move> legal_moves = board.generate_legal_moves();
    std::sort(legal_moves.begin(), legal_moves.end(), [&](const chess::Move &a, const chess::Move &b) {
        int score_a = move_ordering(board, a, depth);
        int score_b = move_ordering(board, b, depth);
        return score_a > score_b;
    });
    return legal_moves;
}

double negamax(int depth, chess::Board& board, double alpha, double beta, bool is_maximising_player,bool do_null, uint64_t key) {
    double original_alpha = alpha;
    // if (TranspositionTable::Entry* entry = tt.retrieve(board, depth)) {
    //     if (entry->depth >= depth) {
    //         switch (entry->flag) {
    //             case NodeType::EXACT:
    //                 return entry->score;
    //             case NodeType::LOWERBOUND:
    //                 alpha = std::max(alpha, entry->score);         
    //                 break;
    //             case NodeType::UPPERBOUND:
    //                 beta = std::min(beta, entry->score);
    //                 break;
    //         }
    //         if (alpha >= beta) return entry->score;
    //     }
    // }

    Entry* cur_entry = transposition_table.lookup(key);
    if (cur_entry != nullptr && cur_entry->depth >= depth) {
        if (cur_entry->flag == NodeType::EXACT) {
            return cur_entry->score;
        } else if (cur_entry->flag == NodeType::LOWER) {
            alpha = std::max(alpha, cur_entry->score);
        } else if (cur_entry->flag == NodeType::UPPER) {
            beta = std::min(beta, cur_entry->score);
        }

        if (alpha >= beta) {
            return cur_entry->score;
        }
    }

    if (board.outcome()) return is_maximising_player * evaluate(board);
    // if (board.is_checkmate()) return is_maximising_player ? -MATE_SCORE : MATE_SCORE;
    // if (board.is_game_over()) return 0.0;
    if (depth == 0) {
        if (!board.is_check()) {
            return quiescence_search(board, alpha, beta, is_maximising_player, 6);
        }
        return is_maximising_player * evaluate(board);
    }

    // === Null Move Pruning ===
    if (do_null && depth >= 3 && !board.is_check()) {
        uint64_t new_key = zobrist.update_key(board, chess::Move::null(), key);
        board.push(chess::Move::null());
        double score = -negamax(depth - 3, board, -beta, -beta + 1, !is_maximising_player, false,new_key);
        board.pop();

        if (score >= beta) return beta;  // Fail-hard beta cutoff
    }

    double best_value =  -1000000;
    
    chess::Move best_move = chess::Move(0, 0);
    std::vector<chess::Move> moves = get_ordered_moves(board, depth);

    for (chess::Move move : moves) {
        uint64_t new_key = zobrist.update_key(board, move, key);
        board.push(move);
        double val = -negamax(depth - 1, board, -beta, -alpha, !is_maximising_player,true, new_key);
        board.pop();

        if (best_value < val) {
            best_value = val;
            best_move = move;
        }
        // if (is_maximising_player) {
        //     if (best_value < val) {
        //         best_value = val;
        //         best_move = move;
        //     }
        //     alpha = std::max(alpha, best_value);
        // } else {
        //     if (best_value > val) {
        //         best_value = val;
        //         best_move = move;

        //     }
        //     beta = std::min(beta, best_value);
        // }

        if (best_value > alpha) {
            alpha = best_value;
            if (!board.is_capture(move)) {
                int from_square = move.from_square;
                int to_square = move.to_square;
                if (board.piece_at(from_square)) {
                    chess::Piece from_piece = *board.piece_at(from_square);
                    int piece = from_piece.piece_type;
                    int color = from_piece.color;
                    history_move[piece][color][to_square] += depth * depth;
                }
            }
        }
        if (beta <= alpha) {
            // Update killer move if this move caused beta cutoff and is not a capture
            if (!board.is_capture(move) && move != killer_move[depth][0]) {
               
                    killer_move[depth][1] = killer_move[depth][0];
                    killer_move[depth][0] = move;
            
            }
        
            // Also update history heuristic
            // if (!board.is_capture(move) ) {
            //     if (auto optional_from_piece = board.piece_at(move.from_square)) {
            //         chess::Piece from_piece = *optional_from_piece;
            //         int piece = from_piece.piece_type;
            //         int color = from_piece.color;
            //         history_move[piece][color][move.to_square] += depth * depth;
            //     }
            // }
        
            break;
        }
        
    }
    NodeType flag;
    if (best_value <= original_alpha) {
        flag = NodeType::UPPER;
    } else if (best_value >= beta) {
        flag = NodeType::LOWER;
    } else {
        flag = NodeType::EXACT;
    }

    Entry new_entry(key, best_value, depth, best_move, flag);
    transposition_table.store(new_entry);
    return best_value;
}


// chess::Move minimax_root(int depth, chess::Board& board, TranspositionTable& tt) {
//     bool maximize = board.turn == chess::WHITE;
//     double best_score = maximize ? -INFINITY : INFINITY;
//     chess::Move best_move = chess::Move(0, 0);
//     std::vector<chess::Move> moves = get_ordered_moves(board, depth);

//     for (chess::Move move : moves) {
//         board.push(move);
//         double score = board.can_claim_draw() ? 0.0 : minimax(depth - 1, board, -INFINITY, INFINITY, !maximize, tt);
//         board.pop();

//         if ((maximize && score > best_score) || (!maximize && score < best_score)) {
//             best_score = score;
//             best_move = move;
//         }
//     }

//     return best_move;
// }

chess::Move get_best_move(chess::Board& board, int time_limit = 10) {
    bool maximize = board.turn == chess::WHITE;
    std::cout << "\n\nThinking..." << std::endl;
    chess::Move best_move = chess::Move::null();
    uint64_t current_key = 0;
    for (int square = 0; square < 64; ++square) {
        if (board.piece_at(square)) {
            chess::Piece piece = *board.piece_at(square);
            current_key ^= zobrist.zobrist_keys[piece.piece_type][piece.color][square];
        }
    }

   
    if (!board.turn) {
        current_key ^= zobrist.black_hash;
    }

    int depth = 1, max_depth = 15;
    auto ids_start = std::chrono::high_resolution_clock::now();
    double runtime = 0;
    while (runtime < time_limit && depth <= max_depth) {
         std::cout << "\ndepth: " << (depth + 1) << std::endl;

        std::vector<chess::Move> moves = get_ordered_moves(board, depth);
        double best_eval =  -1000000;
        double alpha = -1000000;
        double beta = 1000000;
    
        for (const chess::Move& move : moves) {
            uint64_t new_key = zobrist.update_key(board, move, current_key);
            board.push(move);
            double eval = -negamax(depth, board, -beta, -alpha, board.turn ? 1 : -1, true, new_key);
            

            if (eval > best_eval) {
                best_eval = eval;
                best_move = move;
                // std::cout << "\nmove: " << move.toString()
                //           << "\neval: " << eval
                //           << "\ndepth: " << (cur_depth + 1) << std::endl;
            }
            board.pop();
            alpha = std::max(alpha, best_eval);
            
            auto now = std::chrono::high_resolution_clock::now();
            runtime = std::chrono::duration<double>(now - ids_start).count();
            if (runtime > 10) break;
        }
        depth++;
    }

    auto end = std::chrono::high_resolution_clock::now();
    double total_runtime = std::chrono::duration<double>(end - ids_start).count();
    std::cout << "\nruntime: " << std::round(total_runtime * 100) / 100 << "s\n";
    return best_move;
}
