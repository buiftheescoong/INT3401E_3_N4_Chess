#include "TranspositionTable.h"
#include <stdexcept> // For std::bad_alloc (though <new> is more direct)
#include <new>       // For std::bad_alloc
#include <iostream>  // For error reporting (optional)
#include <algorithm> // For std::fill (optional for clear)

// Constructor
TranspositionTable::TranspositionTable(size_t size_mb) : num_entries(0) {
    if (size_mb == 0) {
        // Cannot have a 0 MB table, default to a minimal sensible size or handle error.
        // For this example, let's prevent 0-size if sizeof(TTEntry) is positive.
        // If you want to allow 0 entries, this logic can change.
        if (sizeof(TTEntry) > 0) {
             size_mb = 1; // Ensure at least some memory if possible.
        } else {
            // This case (sizeof(TTEntry) == 0) is highly unlikely for a non-empty struct.
            // No entries can be stored.
            return;
        }
    }

    size_t table_size_bytes = size_mb * 1024 * 1024;
    if (sizeof(TTEntry) > 0) {
        this->num_entries = table_size_bytes / sizeof(TTEntry);
    } else {
        this->num_entries = 0; // Should not happen with a proper TTEntry struct
    }


    if (this->num_entries == 0 && table_size_bytes > 0) {
        // If TTEntry is so large that even 1MB can't hold one, allow at least one entry
        // if memory was requested. This is mostly a safeguard.
        this->num_entries = 1;
    }

    if (this->num_entries > 0) {
        try {
            // Each entry will be default-constructed (flag = TTEntryFlag::NONE)
            table.resize(this->num_entries);
        } catch (const std::bad_alloc& e) {
            // Handle allocation failure, e.g., by trying a smaller size or re-throwing
            std::cerr << "Error: Failed to allocate TranspositionTable (" << size_mb << "MB). "
                      << e.what() << std::endl;
            this->num_entries = 0; // Indicate failure by setting num_entries to 0
            table.clear(); // Ensure vector is empty
            // Optionally re-throw or throw a custom exception
            // throw;
        }
    }
    // If num_entries is 0 after this, the TT is effectively disabled.
}

// Stores an entry into the transposition table
void TranspositionTable::store(const TTEntry& new_entry) {
    if (num_entries == 0) {
        return; // Table is not allocated or has zero capacity
    }

    size_t index = new_entry.zobrist_key % num_entries;
    TTEntry& existing_entry = table[index];

    // Replacement strategy:
    // 1. If the slot is empty (flag == NONE).
    // 2. If the new entry is for a different position (collision), overwrite.
    // 3. If the new entry is for the same position, overwrite if it's from an equal or deeper search.
    if (existing_entry.flag == TTEntryFlag::NONE ||
        new_entry.zobrist_key != existing_entry.zobrist_key ||
        new_entry.depth >= existing_entry.depth)
    {
        table[index] = new_entry;
    }
    // More sophisticated strategies might consider the TTEntryFlag (e.g. prefer EXACT over bounds)
    // or an aging mechanism if entries had timestamps/generation counts.
}

// Looks up an entry in the transposition table
std::optional<TTEntry> TranspositionTable::lookup(uint64_t zobrist_key) {
    if (num_entries == 0) {
        return std::nullopt;
    }

    size_t index = zobrist_key % num_entries;
    const TTEntry& entry = table[index];

    // Check if the entry is valid (not NONE) AND the Zobrist key matches
    if (entry.flag != TTEntryFlag::NONE && entry.zobrist_key == zobrist_key) {
        return entry; // Return a copy of the found entry
    }

    return std::nullopt; // Entry not found, or it's a collision for a different position
}

// Clears all entries in the transposition table
void TranspositionTable::clear() {
    if (num_entries == 0) {
        return;
    }
    // Fill the table with default-constructed (empty) TTEntry objects
    // This effectively marks all slots as invalid/empty.
    std::fill(table.begin(), table.end(), TTEntry());
    // Alternatively, if TTEntry's default constructor is light:
    // for (size_t i = 0; i < num_entries; ++i) {
    //     table[i] = TTEntry(); // Or table[i].flag = TTEntryFlag::NONE; table[i].zobrist_key = 0;
    // }
}

// Returns the number of entry slots in the table
size_t TranspositionTable::get_capacity() const {
    return num_entries;
}