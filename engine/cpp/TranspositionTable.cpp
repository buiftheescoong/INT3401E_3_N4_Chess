#include <unordered_map>
#include "ZobristHashing.h"
#include <cstdint>

enum class NodeType { EXACT, LOWERBOUND, UPPERBOUND };


class TranspositionTable {
public:
    struct Entry {
        uint64_t key;
        double score;
        int depth;
        chess::Move best_move= chess::Move(0, 0);
        NodeType flag;
       
    };

    TranspositionTable(ZobristHashing& zobrist_ref)
    : zobrist(zobrist_ref) {
        table = new Entry[TT_SIZE];
    }

    ~TranspositionTable() {
        delete[] table;
    }


    void store(const chess::Board& board, double score ,int depth, chess::Move best_move, NodeType flag) {
        uint64_t key = zobrist.hash(board);
        size_t index = key % TT_SIZE;

        // Chỉ lưu nếu độ sâu mới >= độ sâu cũ
        if (table[index].depth <= depth || table[index].key != key) {
            table[index] = Entry{key, score, depth, best_move, flag};
        }
    }

    Entry* retrieve(const chess::Board& board, int depth) {
        uint64_t key = zobrist.hash(board);
        size_t index = key % TT_SIZE;

        if (table[index].key == key && table[index].depth >= depth) {
            return &table[index];
        }
        return nullptr;
    }

private:
    static constexpr size_t TT_SIZE = 1 << 20;
    Entry* table;
    ZobristHashing& zobrist;
};
