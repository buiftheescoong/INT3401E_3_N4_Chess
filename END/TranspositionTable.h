#ifndef TRANSPOSITION_TABLE_H
#define TRANSPOSITION_TABLE_H

#include "chess.h" // For chess::Move and other chess types
#include <vector>
#include <optional>
#include <cstdint> // For uint64_t
#include <string>  // For std::string in chess::Move if needed by its definition

// Enum to represent the type of score stored in a TT entry
enum class TTEntryFlag {
    NONE,        // Indicates an empty or invalid slot
    EXACT,       // The score is the exact value of the position
    LOWERBOUND,  // The score is a lower bound (alpha, actual score >= stored score)
    UPPERBOUND   // The score is an upper bound (beta, actual score <= stored score)
};

// Structure to hold transposition table entries
struct TTEntry {
    uint64_t zobrist_key;    // The full Zobrist key to verify the entry
    chess::Move best_move;   // Best move found from this position
    int depth;               // Depth of the search that generated this entry
    int score;               // Score of the position
    TTEntryFlag flag;        // Flag indicating the type of score (EXACT, LOWER, UPPER)

    // Default constructor for empty/invalid entries
    TTEntry()
        : zobrist_key(0),
          best_move(chess::Move::null()), // Assumes chess::Move::null() is available
          depth(0),
          score(0),
          flag(TTEntryFlag::NONE) {}

    // Constructor to create a populated entry
    TTEntry(uint64_t key, int d, int s, TTEntryFlag f, chess::Move mv)
        : zobrist_key(key),
          depth(d),
          score(s),
          flag(f),
          best_move(mv) {}
};

class TranspositionTable {
public:
    // Constructor: table size is specified in Megabytes.
    // Default size is 4MB.
    explicit TranspositionTable(size_t size_mb = 4);

    // Stores an entry into the transposition table.
    // Uses a replacement strategy (e.g., replace if new entry is deeper).
    void store(const TTEntry& entry);

    // Looks up an entry in the transposition table.
    // Returns the entry if found and valid (Zobrist key matches), otherwise std::nullopt.
    std::optional<TTEntry> lookup(uint64_t zobrist_key);

    // Clears all entries in the transposition table (marks them as invalid).
    void clear();

    // Returns the number of entry slots in the table.
    size_t get_capacity() const;

private:
    std::vector<TTEntry> table; // The table itself, stored as a vector of entries
    size_t num_entries;         // The number of slots in the table
};

#endif // TRANSPOSITION_TABLE_H