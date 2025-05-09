// #include <iostream>
// #include <cstdlib>
// #include <ctime>
// #include "ZobristHashing.h"



//     class ZobristHashing {
//     public:
//         ZobristHashing() {
//             srand(static_cast<unsigned int>(time(0))); 

//             for (int r = 0; r < 8; ++r) {
//                 for (int c = 0; c < 8; ++c) {
//                     for (int p = 0; p < 7; ++p) {  
//                         for (int color = 0; color < 2; ++color) {  
//                             zobrist_table[r][c][p][color] = rand(); 
//                         }
//                     }
//                 }
//             }
//         }

//         size_t hash(const chess::Board& board) {
//             size_t hash_value = 0;
            
//             // Duyệt qua toàn bộ bàn cờ và tính toán băm dựa trên vị trí của các quân cờ
//             for (int r = 0; r < 8; ++r) {
//                 for (int c = 0; c < 8; ++c) {
//                     if (board.piece_at(r * 8 + c)) {
//                         // XOR với giá trị ngẫu nhiên của quân cờ tại vị trí (r, c)
//                         chess::Piece piece = *board.piece_at(r * 8 + c);
//                         hash_value ^= zobrist_table[r][c][static_cast<int>(piece.piece_type)][static_cast<int>(piece.color)];
//                     }
//                 }
//             }

//             // Thêm thông tin về trạng thái của game (kiểm tra, kết thúc game)
//             // if (board.is_check()) hash_value ^= 0x8000000000000000;  // Thêm một bit nếu đang bị chiếu
//             // if (board.is_game_over) hash_value ^= 0x4000000000000000;  // Thêm một bit nếu game kết thúc

//             return hash_value;
//         }

//     private:
//         size_t zobrist_table[8][8][7][2];  // Bảng ngẫu nhiên cho các quân cờ và màu sắc
//     };
    
#include "ZobristHashing.h"
#include <cstdlib>
#include <ctime>
#include <random>

ZobristHashing::ZobristHashing() {
    std::mt19937_64 rng(static_cast<unsigned int>(time(0))); // random 64-bit
    std::uniform_int_distribution<uint64_t> dist;


    for (int r = 0; r < 8; ++r) {
        for (int c = 0; c < 8; ++c) {
            for (int p = 0; p < 7; ++p) {
                for (int color = 0; color < 2; ++color) {
                    zobrist_table[r][c][p][color] = dist(rng);
                }
            }
        }
    }
}

uint64_t ZobristHashing::hash(const chess::Board& board) {
    uint64_t hash_value = 0;

    for (int r = 0; r < 8; ++r) {
        for (int c = 0; c < 8; ++c) {
            if (board.piece_at(r * 8 + c)) {
                chess::Piece piece = *board.piece_at(r * 8 + c);
                hash_value ^= zobrist_table[r][c][static_cast<int>(piece.piece_type - 1)][static_cast<int>(piece.color)];
            }
        }
    }

    return hash_value;
}
