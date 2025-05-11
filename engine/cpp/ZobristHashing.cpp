#include "ZobristHashing.h"
#include <random>

ZobristHashing::ZobristHashing() {
    std::mt19937_64 rng(std::random_device{}());
    for (int p = 0; p < NUM_PIECE_TYPES; ++p)
        for (int c = 0; c < NUM_COLORS; ++c)
            for (int s = 0; s < NUM_SQUARES; ++s)
                zobrist_keys[p][c][s] = rng();

    black_hash = rng();
}

uint64_t ZobristHashing::update_key(const chess::Board& board, const chess::Move& move, uint64_t cur_key) {
    uint64_t new_key = cur_key ^ black_hash;
    int from = move.from_square;
    int to = move.to_square;

    

    if (board.piece_at(from) && board.piece_at(to)) {
        const chess::Piece from_piece = *board.piece_at(from);
        const chess::Piece to_piece = *board.piece_at(to);
       
        int pieceF = from_piece.piece_type;
        int colorF = from_piece.color;
        new_key ^= zobrist_keys[pieceF][colorF][from];
        new_key ^= zobrist_keys[pieceF][colorF][to];
        int pieceT = to_piece.piece_type;
        int colorT = to_piece.color;
        new_key ^= zobrist_keys[pieceT][colorT][to];
            
        if (board.is_castling(move)) {
            if (board.turn) {
                if (board.is_queenside_castling(move))
                    new_key ^= zobrist_keys[4][1][0] ^ zobrist_keys[4][1][3];
                else if (board.is_kingside_castling(move))
                    new_key ^= zobrist_keys[4][1][7] ^ zobrist_keys[4][1][5];
            } else {
                if (board.is_queenside_castling(move))
                    new_key ^= zobrist_keys[4][0][56] ^ zobrist_keys[4][0][59];
                else if (board.is_kingside_castling(move))
                    new_key ^= zobrist_keys[4][0][63] ^ zobrist_keys[4][0][61];
            }
        } else if (board.is_en_passant(move)) {
            if (board.turn) {
                if (to - from == 9) new_key ^= zobrist_keys[1][0][from + 1];
                else if (to - from == 7) new_key ^= zobrist_keys[1][0][from - 1];
            } else {
                if (from - to == 9) new_key ^= zobrist_keys[1][1][from - 1];
                else if (from - to == 7) new_key ^= zobrist_keys[1][1][from + 1];
            }
        } else if (move.promotion) {
            int colorF = from_piece.color;
            int pawn = from_piece.piece_type;
            int promo = *move.promotion;
            new_key ^= zobrist_keys[pawn][colorF][to];
            new_key ^= zobrist_keys[promo][colorF][to];
        }
    }

    return new_key;
}
