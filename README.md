# INT3401E_3_N4_Chess
A high-performance chess engine implemented in C++ with Python bindings.
# DEMO
LinkVidDemo:
# Thành viên
Trương Minh Phước - 22028024 - Thuật toán <br>
Bùi Thế Công - 22028193 - Thuật toán <br>
Nguyễn Văn Trung - 23021745 - Thuật toán <br>
Nguyễn Văn Tráng - 23021737 - UI <br>
Bùi Đức Trọng - 23021741 - UI <br>
# Features
Strong AI: Implements negamax search with alpha-beta pruning <br>
Optimization: <br>
Opening Book: <br>
Evaluation Function: <br>


Python Integration: Easy to use from Python applications via bridge <br>
GUI Ready: Compatible with the included Python UI <br>
# Project Structure


# Technical Details


## Search Algorithm



## Evaluation Function
🔹Material Balance

Static piece values (Pawn = 100, Knight = 320, Bishop = 330, Rook = 500, Queen = 900)

Bonus for Bishop pair

Penalty for insufficient material

🔹 Piece-Square Tables (PST)

Separate PSTs for midgame and endgame

Tables for all 6 piece types × both colors


🔹 Mobility

Rooks/bishops/queens rewarded for open/semi-open file access

Penalize blocked or undeveloped pieces

🔹 King Safety

Pawn shield evaluation (especially around the castled king)

Penalty for exposed king or weakened structure (e.g., missing f/g/h pawns)


🔹 Pawn Structure

Penalties for:

Isolated pawns

Doubled pawns

Backward pawns

Pawn islands

Bonuses for:

Passed pawns 

Connected pawns

Protected passed pawns

🔹 Center Control

Control over central squares (d4, d5, e4, e5)

Bonus for pawns and pieces occupying or attacking central zones

🔹 Outposts

Bonus for knights and bishops occupying safe squares that cannot be attacked by enemy pawns.
Encourages strong positional placement in the opponent’s half of the board.


## Opening Book



# Building
## Prerequisites
Python <br>
C++ <br>
CMake <br>
# Acknowledgments
This chess engine uses the chess-library for move generation and board representation.
