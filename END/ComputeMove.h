#ifndef COMPUTEMOVE_H
#define COMPUTEMOVE_H

#include "chess/chess.h" // Hoặc "chess.h" tùy theo cấu trúc thư mục
#include <utility>      // Cho std::pair
#include <string>
#include <vector>       // Cho std::vector (mặc dù không có hàm nào trả về trực tiếp)
#include <cstdint>      // Cho uint64_t

void initialize_engine_resources(); // Đổi tên từ initialize_zobrist_keys để bao quát hơn

std::pair<chess::Move, int> get_best_move(chess::Board& board, int max_search_depth, double thinking_time_seconds = 10.0);



#endif // COMPUTEMOVE_H