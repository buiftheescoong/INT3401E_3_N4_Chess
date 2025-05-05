#include <pybind11/pybind11.h>
#include <string>
#include <optional>
#include "ComputeMove.h"     // nơi chứa get_best_move
#include "chess/chess.h"

namespace py = pybind11;

// Chuyển từ Square (int 0–63) sang dạng "e2", "h8", ...
std::string square_to_str(int square) {
    char file = 'a' + (square % 8);
    char rank = '1' + (square / 8);
    return std::string() + file + rank;
}

// Chuyển từ chess::Move thành chuỗi UCI (ví dụ: "e2e4", "e7e8q")
std::string move_to_string(const chess::Move &move) {
    std::string s = square_to_str(move.from_square) + square_to_str(move.to_square);

    if (move.promotion.has_value()) {
        char promo_char;
        switch (move.promotion.value()) {
            case chess::QUEEN: promo_char = 'q';
                break;
            case chess::ROOK: promo_char = 'r';
                break;
            case chess::BISHOP: promo_char = 'b';
                break;
            case chess::KNIGHT: promo_char = 'n';
                break;
            default: promo_char = '?';
                break;
        }
        s += promo_char;
    }

    return s;
}

// Hàm giao tiếp với Python: nhận FEN và trả nước đi tốt nhất dưới dạng UCI
std::string get_best_move_fen(const std::string &fen, int time_limit = 200) {
    chess::Board board(fen);
    chess::Move move = get_best_move(board, time_limit);
    return move_to_string(move);
}

// Binding module cho pybind11
PYBIND11_MODULE(engine_binding, m) {
    m.doc() = "Chess Engine Binding using pybind11";
    m.def("get_best_move", &get_best_move_fen, "Get best move from FEN", py::arg("fen"), py::arg("time_limit") = 200);
}
