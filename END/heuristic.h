#ifndef HEURISTIC_H
#define HEURISTIC_H

#include <array>
#include <unordered_map> // For std::unordered_map
#include "chess/chess.h" // For chess::Board, chess::PieceType, chess::Color, chess::Square etc.
#include <cstdint>       // For fixed-width integer types, often useful with chess libraries

namespace chess_eval {

const int MATE_SCORE = 1000000; // A common value, adjust if needed.

struct PieceTables {
    const std::array<int, 64>& mg_table; // Reference to Midgame table
    const std::array<int, 64>& eg_table; // Reference to Endgame table

};

extern const std::unordered_map<chess::PieceType, PieceTables> W_PIECE_VALUES;

extern const std::unordered_map<chess::PieceType, PieceTables> B_PIECE_VALUES;

extern const std::unordered_map<chess::PieceType, int> PIECE_MATERIAL_VALUES;

extern const std::unordered_map<chess::PieceType, double> MOBILITY_PIECE_FACTORS;


/**
 * @brief Calculates the overall score of the current board position.
 * Handles terminal states like checkmate and stalemate.
 * Returns score from White's perspective (positive is good for White, negative for Black).
 *
 * @param board The chess board to evaluate. Passed by reference as it might be modified
 *              if future versions uncomment mobility calculations involving push/pop.
 * @return double The evaluation score.
 */
int score(chess::Board& board);

/**
 * @brief Calculates the material and positional score based on piece-square tables.
 * Implements tapered evaluation, blending midgame and endgame scores based on remaining material.
 * Returns score from White's perspective.
 *
 * @param board The chess board to evaluate. Passed by const reference as it's not modified.
 * @return double The calculated positional and material score.
 */
int calculate_score(const chess::Board& board);

/**
 * @brief Calculates a mobility score for the current player.
 * Considers the number of legal moves for different piece types.
 *
 * @param board The chess board to evaluate. Passed by reference as generating moves
 *              might depend on a non-const Board API in some libraries, or for future flexibility.
 * @return double The mobility score. Positive if it's White's turn and White has good mobility,
 *         negative if it's Black's turn and Black has good mobility (relative to the side to move).
 *         The current implementation in the .cpp subtracts for black pieces.
 */
int mobility(chess::Board& board);

} // namespace chess_eval

#endif // HEURISTIC_H