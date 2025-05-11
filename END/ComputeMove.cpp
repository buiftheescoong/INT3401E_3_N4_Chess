#include "chess/chess.h"
#include "TranspositionTable.h"
#include "heuristic.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <iomanip>
#include <map> // For PV table in IDS

// --- Global Variables and Constants ---
constexpr int MAX_PLY_KILLER = 64;
std::vector<std::array<chess::Move, 3> > killer_moves(MAX_PLY_KILLER);
int history_moves[7][2][64];

int MVV_LVA[7][7] = {
    //      NONE P   N   B   R   Q   K
    {0, 0, 0, 0, 0, 0, 0}, // NONE
    {50, 51, 52, 53, 54, 55, 0}, // P
    {40, 41, 42, 43, 44, 45, 0}, // N
    {30, 31, 32, 33, 34, 35, 0}, // B
    {20, 21, 22, 23, 24, 25, 0}, // R
    {10, 11, 12, 13, 14, 15, 0}, // Q
    {0, 0, 0, 0, 0, 0, 0} // K
};

const int MVV_LVA_OFFSET = 1000000;

std::unordered_map<chess::PieceType, int> PIECE_SEE_VALUES = {
    {chess::PAWN, 100},
    {chess::KNIGHT, 320},
    {chess::BISHOP, 330},
    {chess::ROOK, 500},
    {chess::QUEEN, 900},
    {chess::KING, 20000} // King rất lớn
};

uint64_t zobrist_keys[7][2][64];
uint64_t black_to_move_hash;
uint64_t castling_hashes[16]; // For all 2^4=16 castling right combinations
uint64_t enpassant_hashes[64]; // One for each possible en passant square

TranspositionTable transposition_table(64);

// --- Function Declarations ---
// void initialize_engine_resources();
// uint64_t calculate_board_zobrist_key(const chess::Board &board); // Calculates full key
// int move_ordering_score(chess::Board &board, chess::Move move, chess::Move pv_tt_move, int ply);
// int quiescence_search(chess::Board &board, int alpha, int beta, int depth);
// int negamax(chess::Board &board, int depth, int alpha, int beta, bool do_null_move, uint64_t current_board_key);
// std::pair<chess::Move, int> get_best_move(chess::Board &board, int max_search_depth, double thinking_time_seconds);


// --- Zobrist Key Management ---
//killer_moves && history_moves
void initialize_engine_resources() {
    std::mt19937_64 rng(std::chrono::system_clock::now().time_since_epoch().count());
    std::uniform_int_distribution<uint64_t> distrib;

    for (int pt = chess::PAWN; pt <= chess::KING; ++pt) {
        for (int color_idx = 0; color_idx < 2; ++color_idx) {
            for (int sq = 0; sq < 64; ++sq) {
                zobrist_keys[pt][color_idx][sq] = distrib(rng);
            }
        }
    }
    black_to_move_hash = distrib(rng);
    for (int i = 0; i < 16; ++i) castling_hashes[i] = distrib(rng);
    for (int i = 0; i < 64; ++i) enpassant_hashes[i] = distrib(rng);


    for (int i = 0; i < MAX_PLY_KILLER; ++i) {
        killer_moves[i][0] = chess::Move::null();
        killer_moves[i][1] = chess::Move::null();
        killer_moves[i][2] = chess::Move::null();
    }
    std::fill(&history_moves[0][0][0], &history_moves[0][0][0] + 7 * 2 * 64, 0);
}

//get_attackers_to_square
chess::Bitboard get_attackers_to_square(const chess::Board &board, chess::Square target_sq, chess::Color attacker_color,
                                        chess::Bitboard occupied_for_sliders) {
    chess::Bitboard attackers = 0;
    // Pawns
    attackers |= chess::BB_PAWN_ATTACKS[!attacker_color][target_sq] & board.pawns & board.occupied_co[attacker_color];
    // Knights
    attackers |= chess::BB_KNIGHT_ATTACKS[target_sq] & board.knights & board.occupied_co[attacker_color];
    // Bishops & Queens (diagonal)
    attackers |= (chess::BB_DIAG_ATTACKS[target_sq].at(chess::BB_DIAG_MASKS[target_sq] & occupied_for_sliders)) &
            (board.bishops | board.queens) & board.occupied_co[attacker_color];
    // Rooks & Queens (rank/file)
    attackers |= (chess::BB_RANK_ATTACKS[target_sq].at(chess::BB_RANK_MASKS[target_sq] & occupied_for_sliders) |
                  chess::BB_FILE_ATTACKS[target_sq].at(chess::BB_FILE_MASKS[target_sq] & occupied_for_sliders)) &
            (board.rooks | board.queens) & board.occupied_co[attacker_color];
    // Kings
    attackers |= chess::BB_KING_ATTACKS[target_sq] & board.kings & board.occupied_co[attacker_color];

    return attackers;
}

//SEE ko đệ quy
int see_non_recursive(chess::Board board, chess::Square target_sq, chess::Color attacker_color) {
    std::vector<int> gain;
    gain.reserve(32);

    chess::Bitboard occupied = board.occupied;
    chess::Color side_to_move = attacker_color;
    chess::Bitboard attackers = get_attackers_to_square(board, target_sq, side_to_move, occupied);

    std::optional<chess::Piece> target_piece_opt = board.piece_at(target_sq);
    if (!target_piece_opt) return 0;

    gain.push_back(PIECE_SEE_VALUES[target_piece_opt->piece_type]);

    int depth = 0;

    while (true) {
        // Tìm quân tấn công có giá trị nhỏ nhất (LVA)
        chess::PieceType lva_type = chess::KING + 1;
        chess::Square lva_sq = chess::A1; // Dummy
        std::optional<chess::Piece> lva_piece = std::nullopt;

        for (chess::Square attacker_sq: chess::scan_forward(attackers)) {
            auto p_opt = board.piece_at(attacker_sq);
            if (p_opt && PIECE_SEE_VALUES[p_opt->piece_type] < PIECE_SEE_VALUES[lva_type]) {
                lva_type = p_opt->piece_type;
                lva_sq = attacker_sq;
                lva_piece = p_opt;
            }
        }

        if (!lva_piece) break;

        ++depth;
        gain.push_back(PIECE_SEE_VALUES[lva_piece->piece_type] - gain[depth - 1]);

        // Cập nhật bàn cờ và thông tin tấn công
        board.remove_piece_at(lva_sq);
        board.set_piece_at(target_sq, chess::Piece{lva_piece->piece_type, lva_piece->color});
        occupied ^= chess::BB_SQUARES[lva_sq];
        side_to_move = !side_to_move;
        attackers = get_attackers_to_square(board, target_sq, side_to_move, occupied);
    }

    // Backward induction
    for (int i = depth - 1; i >= 0; --i) {
        gain[i] = std::max(-gain[i + 1], gain[i]);
    }

    return gain[0];
}

//đánh giá trao đổi tĩnh
int static_exchange_evaluation(const chess::Board &board, chess::Move move) {
    if (!board.is_capture(move)) {
        if (board.is_en_passant(move)) return PIECE_SEE_VALUES[1]; // Ăn tốt EP
        return 0;
    }

    chess::Square target_sq = move.to_square;
    chess::Square from_sq = move.from_square;

    std::optional<chess::Piece> attacker_opt = board.piece_at(from_sq);
    if (!attacker_opt) return 0; // Không có quân nào đi từ from_sq

    std::optional<chess::Piece> victim_opt;
    if (board.is_en_passant(move)) {
        // Xử lý đặc biệt nếu là bắt tốt qua đường
        chess::Square ep_pawn_sq = target_sq + (attacker_opt->color == chess::WHITE ? -8 : 8);
        victim_opt = board.piece_at(ep_pawn_sq);
    } else {
        victim_opt = board.piece_at(target_sq);
    }
    if (!victim_opt) return 0;
    chess::Board temp_board = board;
    temp_board.remove_piece_at(from_sq);
    if (board.is_en_passant(move)) {
        chess::Square ep_pawn_sq = target_sq + (attacker_opt->color == chess::WHITE ? -8 : 8);
        temp_board.remove_piece_at(ep_pawn_sq);
    }
    temp_board.set_piece_at(target_sq, std::optional<chess::Piece>{
                                chess::Piece(attacker_opt->piece_type, attacker_opt->color)
                            });

    return see_non_recursive(temp_board, target_sq,!attacker_opt->color);
}


//calculate_board_zobrist_key
uint64_t calculate_board_zobrist_key(const chess::Board &board) {
    uint64_t key = 0;
    for (chess::Square sq_idx = chess::A1; sq_idx <= chess::H8; ++sq_idx) {
        std::optional<chess::Piece> piece_opt = board.piece_at(sq_idx);
        if (piece_opt) {
            chess::Piece piece = *piece_opt;
            key ^= zobrist_keys[piece.piece_type][static_cast<int>(piece.color)][sq_idx];
        }
    }
    if (board.turn == chess::BLACK) {
        key ^= black_to_move_hash;
    }
    int castling_idx = 0;
    if (board.castling_rights & chess::BB_SQUARES[chess::H1]) castling_idx |= 1;
    // White Kingside (assuming H1 is rook for K-side)
    if (board.castling_rights & chess::BB_SQUARES[chess::A1]) castling_idx |= 2; // White Queenside
    if (board.castling_rights & chess::BB_SQUARES[chess::H8]) castling_idx |= 4; // Black Kingside
    if (board.castling_rights & chess::BB_SQUARES[chess::A8]) castling_idx |= 8; // Black Queenside
    key ^= castling_hashes[castling_idx];

    if (board.ep_square) {
        // python-chess uses has_legal_en_passant() for its _transposition_key.
        // This is important. A simple board.ep_square check might not be enough.
        // For now, using board.ep_square directly.
        if (board.has_legal_en_passant()) {
            // More accurate for TT hits
            key ^= enpassant_hashes[*board.ep_square];
        }
    }
    return key;
}


// --- Move Ordering ---
int move_ordering_score(chess::Board &board, chess::Move move, chess::Move pv_tt_move, int ply) {
    if (move == pv_tt_move) {
        return 20000000;
    }
    chess::Square to_square = move.to_square;
    chess::Square from_square = move.from_square;
    int score = 0;
    std::optional<chess::Piece> attacker_piece_opt = board.piece_at(move.from_square);

    chess::PieceType attacker_type = attacker_piece_opt->piece_type;

    if (board.is_capture(move)) {
        int see_score = static_exchange_evaluation(board, move);
        if (see_score < 0) {
            score += see_score; // Phạt nặng các nước capture có SEE âm
        } else {
            score += MVV_LVA_OFFSET;
            chess::PieceType victim_type;
            if (board.is_en_passant(move)) {
                victim_type = chess::PAWN;
            } else {
                std::optional<chess::Piece> victim_piece_opt = board.piece_at(move.to_square);
                if (!victim_piece_opt) return MVV_LVA_OFFSET; // Should not happen on capture
                victim_type = victim_piece_opt->piece_type;
            }
            attacker_type = board.piece_at(move.from_square)->piece_type;
            score += MVV_LVA[victim_type][attacker_type];
        }
    } else {
        if (ply >= 0 && ply < MAX_PLY_KILLER) {
            if (move == killer_moves[ply][0]) {
                score = MVV_LVA_OFFSET - 100;
            } else if (move == killer_moves[ply][1]) {
                score = MVV_LVA_OFFSET - 200;
            } else if (move == killer_moves[ply][2]) {
                score = MVV_LVA_OFFSET - 300;
            } else {
                std::optional<chess::Piece> attacker_piece_opt = board.piece_at(move.from_square);
                score += history_moves[attacker_piece_opt->piece_type][static_cast<int>(attacker_piece_opt->color)][move
                    .to_square];
            }
        }
    }
    return score;
}


// --- Quiescence Search ---
int quiescence_search(chess::Board &board, int alpha, int beta, int depth) {
    int white_pov_score = chess_eval::score(board); // Hàm score của bạn
    int stand_pat = (board.turn == chess::WHITE) ? white_pov_score : -white_pov_score;

    if (depth == 0) {
        return stand_pat; // Đạt độ sâu tối đa của qsearch
    }

    if (stand_pat >= beta) {
        return beta; // Fail-high cho người chơi hiện tại
    }

    if (alpha < stand_pat) {
        alpha = stand_pat; // Cập nhật alpha nếu điểm tĩnh tốt hơn
    }

    std::vector<std::pair<chess::Move, int> > scored_moves;

    std::vector<chess::Move> moves_to_consider;
    bool currently_in_check = board.is_check();

    if (currently_in_check) {
        depth = std::max(depth, 1); // Đảm bảo tìm kiếm ít nhất 1 ply để thoát chiếu
        for (chess::Move move: board.generate_legal_moves()) {
            int order_score = board.is_capture(move)
                                  ? (MVV_LVA_OFFSET + PIECE_SEE_VALUES[board.piece_at(move.to_square)->piece_type] -
                                     PIECE_SEE_VALUES[board.piece_at(move.from_square)->piece_type])
                                  : 0;
            if (board.gives_check(move)) order_score += 50; // Thưởng nhẹ cho chiếu lại
            scored_moves.push_back({move, order_score});
        }
        if (scored_moves.empty()) {
            // Checkmate
            return stand_pat; // stand_pat lúc này nên là -MATE_SCORE (từ hàm score)
        }
    } else {
        const int SEE_THRESHOLD = -50;
        for (chess::Move move: board.generate_legal_captures()) {
            int see_value = static_exchange_evaluation(board, move);
            if (see_value >= SEE_THRESHOLD) {
                scored_moves.push_back({move, see_value});
                // Chỉ xét các nước ăn quân có lợi hoặc an toàn
                moves_to_consider.push_back(move);
            }
        }
        if (moves_to_consider.empty()) {
            return stand_pat;
        }
    }

    std::sort(moves_to_consider.begin(), moves_to_consider.end(), [&](chess::Move a, chess::Move b) {
        return move_ordering_score(board, a, chess::Move::null(), depth) > move_ordering_score(
                   board, b, chess::Move::null(), depth);
    });


    for (chess::Move move: moves_to_consider) {
        board.push(move);
        int current_eval = -quiescence_search(board, -beta, -alpha, depth - 1);
        board.pop();

        if (current_eval >= beta) {
            return beta; // Fail-high
        }
        if (current_eval > alpha) {
            alpha = current_eval;
        }
    }
    return alpha;
}

// --- Negamax Search ---
int negamax(chess::Board &board, int depth, int alpha, int beta, bool do_null_move, uint64_t board_key) {
    int original_alpha = alpha;

    std::optional<TTEntry> tt_entry_opt = transposition_table.lookup(board_key);
    chess::Move tt_best_move = chess::Move::null();

    if (tt_entry_opt) {
        TTEntry tt_entry = *tt_entry_opt;
        tt_best_move = tt_entry.best_move;
        if (tt_entry.depth >= depth) {
            if (tt_entry.flag == TTEntryFlag::EXACT) return tt_entry.score;
            if (tt_entry.flag == TTEntryFlag::LOWERBOUND) alpha = std::max(alpha, tt_entry.score);
            if (tt_entry.flag == TTEntryFlag::UPPERBOUND) beta = std::min(beta, tt_entry.score);
            if (alpha >= beta) return tt_entry.score;
        }
    }

    if (board.outcome()) {
        int white_pov_score = chess_eval::score(board);
        return (board.turn == chess::WHITE) ? white_pov_score : -white_pov_score;
    }

    if (depth == 0) {
        if (!board.is_check()) {
            return quiescence_search(board, alpha, beta, 10);
        }
        return (board.turn == chess::WHITE) ? chess_eval::score(board) : -chess_eval::score(board);
    }

    if (do_null_move && !board.is_check() && depth >= 3) {
        board.push(chess::Move::null());
        uint64_t new_board_key_null = calculate_board_zobrist_key(board); // Recalculate after null move
        int null_move_score = -negamax(board, depth - 3, -beta, -beta + 1, false, new_board_key_null);
        board.pop();
        if (null_move_score >= beta) {
            // Optional: Store a shallow depth TT entry for beta cutoff
            // transposition_table.store(TTEntry(board_key, depth, beta, TTEntryFlag::LOWERBOUND, chess::Move::null()));
            return beta;
        }
    }

    int max_eval = -chess_eval::MATE_SCORE - 1000;
    chess::Move best_move_found = chess::Move::null();

    std::vector<chess::Move> legal_moves;
    for (auto &m: board.generate_legal_moves()) legal_moves.push_back(m);
    if (legal_moves.empty()) {
        int white_pov_score = chess_eval::score(board);
        return (board.turn == chess::WHITE) ? white_pov_score : -white_pov_score;
    }


    std::sort(legal_moves.begin(), legal_moves.end(), [&](chess::Move a, chess::Move b) {
        return move_ordering_score(board, a, chess::Move::null(), depth) > move_ordering_score(
                   board, b, chess::Move::null(), depth);
    });

    for (chess::Move move: legal_moves) {
        board.push(move);
        int extension = 0;
        if (board.is_check()) {
            // Nếu nước đi 'move' của mình làm đối thủ bị chiếu
            extension = 1; // Tăng độ sâu tìm kiếm thêm 1 ply
        }
        uint64_t new_board_key = calculate_board_zobrist_key(board); // Recalculate after move
        int eval = -negamax(board, depth - 1 + extension, -beta, -alpha, true, new_board_key);
        board.pop();

        if (eval > max_eval) {
            max_eval = eval;
            best_move_found = move;
        }

        if (max_eval > alpha) {
            alpha = max_eval;
            if (!board.is_capture(move)) {
                std::optional<chess::Piece> p_opt = board.piece_at(move.from_square);
                if (p_opt && depth < MAX_PLY_KILLER) {
                    history_moves[p_opt->piece_type][static_cast<int>(p_opt->color)][move.to_square] += depth * depth;
                }
            }
        }

        if (alpha >= beta) {
            if (!board.is_capture(move) && depth < MAX_PLY_KILLER) {
                if (move != killer_moves[depth][0]) {
                    killer_moves[depth][2] = killer_moves[depth][1];
                    killer_moves[depth][1] = killer_moves[depth][0];
                    killer_moves[depth][0] = move;
                }
            }
            break;
        }
    }

    TTEntryFlag flag;
    if (max_eval <= original_alpha) flag = TTEntryFlag::UPPERBOUND;
    else if (max_eval >= beta) flag = TTEntryFlag::LOWERBOUND;
    else flag = TTEntryFlag::EXACT;

    TTEntry new_entry(board_key, depth, max_eval, flag, best_move_found);
    transposition_table.store(new_entry);
    return max_eval;
}


// --- Iterative Deepening Search ---
std::map<int, chess::Move> principal_variation_table; // Stores PV for IDS

std::pair<chess::Move, int> get_best_move(chess::Board &board, int max_search_depth, double thinking_time_seconds) {
    std::cout << "\nThinking...\n";
    auto ids_start_time = std::chrono::high_resolution_clock::now();
    principal_variation_table.clear();

    // Khởi tạo best_eval_overall là giá trị cực tiểu (điểm luôn từ góc nhìn của người chơi hiện tại ở gốc)
    int best_eval_overall = -chess_eval::MATE_SCORE - 10000;
    chess::Move best_move_overall = chess::Move::null();

    // Lấy danh sách nước đi hợp lệ một lần ở gốc
    std::vector<chess::Move> root_legal_moves;
    for (chess::Move m: board.generate_legal_moves()) {
        root_legal_moves.push_back(m);
    }

    if (root_legal_moves.empty()) {
        std::cout << "No legal moves at root. Game may be over." << std::endl;
        if (board.is_checkmate()) {
            best_eval_overall = -chess_eval::MATE_SCORE; // Bị chiếu hết (điểm từ góc nhìn người chơi hiện tại)
        } else {
            // Stalemate or other draw
            best_eval_overall = 0;
        }
        return {chess::Move::null(), best_eval_overall};
    }
    best_move_overall = root_legal_moves[0];


    for (int iteration_depth = 1; iteration_depth <= max_search_depth; ++iteration_depth) {
        auto depth_start_time = std::chrono::high_resolution_clock::now();

        transposition_table.clear();

        uint64_t root_board_key = calculate_board_zobrist_key(board);

        std::vector<chess::Move> current_iter_moves = root_legal_moves;

        chess::Move pv_move_from_last_iter = chess::Move::null();
        if (principal_variation_table.count(0)) {
            pv_move_from_last_iter = principal_variation_table[0];
        }

        std::sort(current_iter_moves.begin(), current_iter_moves.end(), [&](chess::Move a, chess::Move b) {
            return move_ordering_score(board, a, chess::Move::null(), iteration_depth) > move_ordering_score(
                       board, b, chess::Move::null(), iteration_depth);
        });

        int alpha = -chess_eval::MATE_SCORE - 1000;
        int beta = chess_eval::MATE_SCORE + 1000;

        int current_iteration_best_eval = -chess_eval::MATE_SCORE - 10000; // Điểm tốt nhất trong iteration này
        chess::Move current_iteration_best_move = current_iter_moves[0]; // Nước đi tốt nhất trong iteration này

        for (size_t i = 0; i < current_iter_moves.size(); ++i) {
            chess::Move move = current_iter_moves[i];
            board.push(move);
            uint64_t new_board_key = calculate_board_zobrist_key(board);
            int eval;

            if (i == 0) {
                // Nước đi đầu tiên (thường là PV) -> full window search
                eval = -negamax(board, iteration_depth - 1, -beta, -alpha, true, new_board_key);
            } else {
                // PVS
                eval = -negamax(board, iteration_depth - 1, -alpha - 1, -alpha, true, new_board_key); // Zero window
                if (eval > alpha && eval < beta) {
                    // Nếu nằm ngoài dự đoán nhưng vẫn trong khoảng (alpha,beta)
                    eval = -negamax(board, iteration_depth - 1, -beta, -alpha, true, new_board_key); // Re-search
                }
            }
            board.pop();

            if (eval > current_iteration_best_eval) {
                current_iteration_best_eval = eval;
                current_iteration_best_move = move;
            }
            alpha = std::max(alpha, eval); // Cập nhật alpha cho các nước đi sau ở gốc

            auto current_time_check = std::chrono::high_resolution_clock::now();
            std::chrono::duration<double> elapsed_total_check = current_time_check - ids_start_time;
            if (elapsed_total_check.count() >= thinking_time_seconds) {
                std::cout << "Thinking time limit reached during depth " << iteration_depth << std::endl;
                if (current_iteration_best_eval > best_eval_overall) {
                    best_eval_overall = current_iteration_best_eval;
                    best_move_overall = current_iteration_best_move;
                    principal_variation_table[0] = best_move_overall;
                }
                goto end_search_ids;
            }
        }

        if (iteration_depth == 1 || current_iteration_best_eval > best_eval_overall) {
            best_eval_overall = current_iteration_best_eval;
            best_move_overall = current_iteration_best_move;
            principal_variation_table[0] = best_move_overall;
            std::cout << "Overall best updated after depth " << iteration_depth << ": "
                    << best_move_overall.uci() << " (" << best_eval_overall << ")" << std::endl;
        } else {
            std::cout << "Depth " << iteration_depth << " finished. Iteration best: "
                    << current_iteration_best_move.uci() << " (" << current_iteration_best_eval << ")."
                    << " Overall best remains: " << best_move_overall.uci() << " (" << best_eval_overall << ")" <<
                    std::endl;
        }

        if (best_eval_overall >= chess_eval::MATE_SCORE || best_eval_overall <= -chess_eval::MATE_SCORE + 100
            /*thêm khoảng đệm cho mate score*/) {
            std::cout << "Mate found or near-mate score at depth " << iteration_depth << ". Best move: " <<
                    best_move_overall.uci() << std::endl;
            break;
        }
    }

end_search_ids:

    if (best_move_overall == chess::Move::null() && !root_legal_moves.empty()) {
        std::cout << "Warning: No best move found by IDS search logic, picking first legal move from initial list." <<
                std::endl;
        best_move_overall = root_legal_moves[0];
    }


    return {best_move_overall, best_eval_overall};
}
