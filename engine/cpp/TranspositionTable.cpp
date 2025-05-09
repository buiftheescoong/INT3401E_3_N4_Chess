#include "TranspositionTable.h"

Entry* TranspositionTable::lookup(uint64_t key) {
    uint64_t index = key % HASH_SIZE;
    auto it = table.find(index);
    if (it != table.end()) {
        return &it->second;
    }
    return nullptr;
}

void TranspositionTable::store(const Entry& entry) {
    uint64_t index = entry.key % HASH_SIZE;
    table[index] = entry;
}
