#ifndef ZOBRIST_HASHING_H
#define ZOBRIST_HASHING_H

#include <cstdint>
#include "../../chess/chess.h" 


class ZobristHashing {
public:
    ZobristHashing();

    uint64_t update_key(const chess::Board& board, const chess::Move& move, uint64_t cur_key);


    static constexpr int NUM_PIECE_TYPES = 7;
    static constexpr int NUM_COLORS = 2;
    static constexpr int NUM_SQUARES = 64;

    uint64_t zobrist_keys[NUM_PIECE_TYPES][NUM_COLORS][NUM_SQUARES];
    uint64_t black_hash;
};

#endif // ZOBRIST_HASHING_H
