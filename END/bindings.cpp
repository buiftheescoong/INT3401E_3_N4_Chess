#include <iostream>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>    // Cho std::string, std::optional
#include <string>
#include <optional>
#include "ComputeMove.h"     // Nơi chứa get_best_move(chess::Board&, int)
#include "chess/chess.h"     // Nơi chứa chess::Board, chess::Move

namespace py = pybind11;
std::string get_best_move_binding_for_python(const std::string& fen_string, int time_limit_ms) {
    try {
        int time_limit_seconds = time_limit_ms / 1000;
        if (time_limit_seconds <= 0 && time_limit_ms > 0) {
            time_limit_seconds = 1;
        } else if (time_limit_ms <= 0) {
             time_limit_seconds = 0;
        }


        chess::Board board(fen_string);
        chess::Move best_move_cpp = get_best_move(board, time_limit_seconds);
        return best_move_cpp.uci();

    } catch (const std::invalid_argument& e) {
        throw py::value_error(std::string("Invalid FEN string provided: ") + e.what());
    } catch (const std::exception& e) {
        throw std::runtime_error(std::string("An error occurred in the C++ engine: ") + e.what());
    }
}

// Binding module cho pybind11
PYBIND11_MODULE(engine_binding, m) { // Tên module là "engine_binding"
    m.doc() = "Chess Engine Binding using pybind11";
    m.def("get_best_move",                               // Tên hàm ở Python
          &get_best_move_binding_for_python,           // Con trỏ tới hàm C++ wrapper
          "Get the best move from a FEN string given a time limit in milliseconds.", // Docstring
          py::arg("fen"),                              // Tên đối số thứ nhất ở Python
          py::arg("time_limit_ms") = 10000);           // Tên đối số thứ hai, giá trị mặc định 10000ms (10s)
}