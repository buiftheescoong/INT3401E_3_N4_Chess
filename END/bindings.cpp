#include <iostream>
#include <pybind11/pybind11.h>
#include <string>
#include <optional>
#include <algorithm>
#include "ComputeMove.h"
#include "chess/chess.h"

namespace py = pybind11;

bool engine_resources_initialized = false;

// Hàm lọc ký tự không hợp lệ trong FEN (ASCII printable)
std::string sanitize_fen(const std::string& raw_fen) {
    std::string clean;
    for (char c : raw_fen) {
        // Giữ lại các ký tự in được và bỏ các ký tự điều khiển như \n, \r
        if (c >= 32 && c <= 126) {
            clean += c;
        }
    }
    return clean;
}


std::string get_best_move_binding(const std::string& fen_string, int max_depth, double time_limit_seconds) {

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
            throw py::value_error(std::string("Invalid FEN string for board setup: '") + clean_fen + "'. Error: " + e.what());
        }

        std::pair<chess::Move, int> result = get_best_move(board, max_depth, time_limit_seconds);
        chess::Move best_move_cpp = result.first;

        if (best_move_cpp == chess::Move::null()) {
            if (board.is_game_over(true)) {
                throw std::runtime_error(std::string("Game is over or no legal moves. Result: ") + board.result());
            }
            throw std::runtime_error("Engine could not determine a best move, but game is not over.");
        }

        return best_move_cpp.uci();

    } catch (const py::value_error& e) {
        throw;
    } catch (const std::invalid_argument& e) {
        std::cerr << "C++ engine caught std::invalid_argument: " << e.what() << std::endl;
        throw py::value_error(std::string("Invalid argument encountered in C++ engine: ") + e.what());
    } catch (const std::out_of_range& e) {
        std::cerr << "C++ engine caught std::out_of_range: " << e.what() << std::endl;
        throw std::runtime_error(std::string("C++ engine error (std::out_of_range): ") + e.what());
    } catch (const std::exception& e) {
        std::cerr << "C++ engine caught std::exception: " << e.what() << std::endl;
        throw std::runtime_error(std::string("An error occurred in the C++ engine: ") + e.what());
    } catch (...) {
        std::cerr << "C++ engine caught unknown exception type." << std::endl;
        throw std::runtime_error("An unknown error occurred in the C++ engine.");
    }
}

PYBIND11_MODULE(engine_binding, m) {
    m.doc() = "Chess Engine Binding using pybind11";

    m.def("get_best_move", &get_best_move_binding, "Get best move from FEN string.",
          py::arg("fen"),
          py::arg("max_depth"),
          py::arg("time_limit_seconds") = 10.0);

    struct EngineInitializer {
        EngineInitializer() {
            if (!engine_resources_initialized) {
                initialize_engine_resources();
                engine_resources_initialized = true;
            }
        }
    };
}
