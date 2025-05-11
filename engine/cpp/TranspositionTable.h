#ifndef TRANSPOSITION_TABLE_H
#define TRANSPOSITION_TABLE_H

#include <cstdint>
#include <unordered_map>
#include "../../chess/chess.h" 

constexpr uint64_t HASH_SIZE = 4294967569;
enum class NodeType { EXACT, LOWER, UPPER};

struct Entry {
    uint64_t key;
    double score;
    int depth;
    chess::Move best_move= chess::Move(0, 0);
    NodeType flag;

    Entry()
    : key(0),
      score(0.0),
      depth(-1),
      best_move(chess::Move::null()),
      flag(NodeType::EXACT)
  {}

    Entry(uint64_t key, double score, int depth,  chess::Move best_move, NodeType flag)
        : key(key), depth(depth), score(score), flag(flag), best_move(best_move) {}
};

class TranspositionTable {
public:
    Entry* lookup(uint64_t key);
    void store(const Entry& entry);

private:
    std::unordered_map<uint64_t, Entry> table;
};

#endif // TRANSPOSITION_TABLE_H
