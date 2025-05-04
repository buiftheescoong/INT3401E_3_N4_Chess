#ifndef HEURISTIC_H
#define HEURISTIC_H

#include <array>
#include <map>
#include "chess/chess.h"

// Constants
extern const int MATE_SCORE;

// Piece type enumeration
enum Piece {
    PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
};

enum Color { WHITE, BLACK };

// Piece-Square Tables declarations
extern const std::array<int, 64> WPAWN_MG, WPAWN_EG;
extern const std::array<int, 64> WKNIGHT_MG, WKNIGHT_EG;
extern const std::array<int, 64> WBISHOP_MG, WBISHOP_EG;
extern const std::array<int, 64> WROOK_MG, WROOK_EG;
extern const std::array<int, 64> WQUEEN_MG, WQUEEN_EG;
extern const std::array<int, 64> WKING_MG, WKING_EG;

extern const std::array<int, 64> BPAWN_MG, BPAWN_EG;
extern const std::array<int, 64> BKNIGHT_MG, BKNIGHT_EG;
extern const std::array<int, 64> BBISHOP_MG, BBISHOP_EG;
extern const std::array<int, 64> BROOK_MG, BROOK_EG;
extern const std::array<int, 64> BQUEEN_MG, BQUEEN_EG;
extern const std::array<int, 64> BKING_MG, BKING_EG;

// Type definitions
using PieceValuePair = std::pair<const std::array<int, 64>&, const std::array<int, 64>&>;

// Piece values maps
extern const std::map<Piece, PieceValuePair> wpiece_values;
extern const std::map<Piece, PieceValuePair> bpiece_values;
extern const std::map<Piece, double> mobility_weights;

// Evaluation weights
extern int W_MOBILITY;
extern int W_KING_SAFETY;
extern int W_PAWN_STRUCTURE;
extern int W_BISHOP_PAIR;
extern int W_CENTER_CONTROL;
extern int W_PAWN_SHELTER;
extern int W_ROOK_OPEN;
extern int W_OUTPOST;
extern int W_TROPISM;
extern int W_SPACE;
extern int W_THREAT;

// Function declarations
int evaluate(chess::Board board);

#endif // HEURISTIC_H