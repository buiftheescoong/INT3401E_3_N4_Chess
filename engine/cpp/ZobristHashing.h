
#ifndef ZOBRISTHASING_H
#define ZOBRISTHASING_H



#include "../../chess/chess.h"
#include <cstdint>

class ZobristHashing {
    public:
        ZobristHashing();

        uint64_t hash(const chess::Board& board);

    private:
        uint64_t zobrist_table[8][8][7][2];
};
#endif