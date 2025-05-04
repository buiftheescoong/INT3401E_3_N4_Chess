#ifndef COMPUTEMOVE_H
#define COMPUTEMOVE_H

#include <vector>
#include <limits>
#include "chess/chess.h"

// Constants
const int MATE_THRESHOLD = 999000000;

// Function declarations
int move_ordering(chess::Board board, chess::Move move);
std::vector<chess::Move> get_ordered_moves(const chess::Board &board);
double minimax(int depth, chess::Board board, double alpha, double beta, bool is_maximising_player);
chess::Move minimax_root(int depth, chess::Board board);
chess::Move next_move(int depth, chess::Board board);
chess::Move get_best_move(chess::Board& board, int time_limit = 200);

// ChessEngine class declaration
class ChessEngine {
public:
    ChessEngine() = default; 
    // Calculate the best move given a board and a time limit (in seconds)
    chess::Move get_best_move(chess::Board& board, int time_limit = 200);
};

#endif // COMPUTEMOVE_H