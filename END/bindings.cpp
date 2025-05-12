#include <iostream>
#include <pybind11/pybind11.h>
#include <string>
#include <optional>
#include <algorithm>
#include "ComputeMove.h"
#include "chess/chess.h"

namespace py = pybind11;

// Biến toàn cục
bool engine_resources_initialized = false;

// Hàm lọc ký tự không hợp lệ trong FEN
std::string sanitize_fen(const std::string& raw_fen) {
    std::string clean;
    for (char c : raw_fen) {
        if (c >= 32 && c <= 126) {  // Printable ASCII
            clean += c;
        }
    }
    return clean;
}

// Trả về chess::Move thay vì string
chess::Move get_best_move_binding(const std::string& fen_string, int max_depth, double time_limit_seconds) {
    if (!engine_resources_initialized) {
        initialize_engine_resources();
        engine_resources_initialized = true;
        std::cout << "C++ Engine resources initialized." << std::endl;
    }

    try {
        chess::Board board;
        std::string clean_fen = sanitize_fen(fen_string);

        try {
            board.set_fen(clean_fen);
        } catch (const std::invalid_argument& e) {
            throw py::value_error("Invalid FEN string: " + clean_fen + ". Error: " + e.what());
        }

        std::pair<chess::Move, int> result = get_best_move(board, max_depth, time_limit_seconds);
        chess::Move best_move = result.first;

        if (best_move == chess::Move::null()) {
            if (board.is_game_over(true)) {
                throw std::runtime_error("Game over. Result: " + board.result());
            }
            throw std::runtime_error("No legal move found.");
        }

        return best_move;

    } catch (const std::exception& e) {
        std::cerr << "C++ exception: " << e.what() << std::endl;
        throw;
    }
}

// Pybind11 module
PYBIND11_MODULE(engine_binding, m) {
    m.doc() = "Chess Engine Binding using pybind11";

    py::class_<chess::Move>(m, "Move")
    .def(py::init<>())  // Default constructor
    .def("uci", &chess::Move::uci)
    .def("is_null", &chess::Move::null)
    .def_static("from_uci", &chess::Move::from_uci);

    // Bind hàm chính
    m.def("get_best_move", &get_best_move_binding,
          "Get best move from a FEN string.",
          py::arg("fen"),
          py::arg("max_depth"),
          py::arg("time_limit_seconds") = 15);
}
