# INT3401E_3_N4_Chess
A high-performance chess engine implemented in C++ with Python bindings.
# DEMO
[Demo my bot plays with chess engine 2200 ELO:](https://drive.google.com/file/d/1ODzqP8zBzFM3Iy-9Vq-TN8cBcawQeAgO/view?usp=sharing)
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
🔹Opening Book

🔹Negamax Search

🔹Alpha-Beta Pruning

🔹Quiescence Search

🔹Transposition Table

🔹Static Exchange Evaluation

🔹MVV-LVA

🔹Killer Moves

🔹History Moves

🔹Move Ordering

🔹Null Move Pruning


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

Pawn islands

Bonuses for:

Passed pawns 

Connected pawns


🔹 Center Control

Control over central squares (d4, d5, e4, e5)

Bonus for pawns and pieces occupying or attacking central zones

🔹 Outposts

Bonus for knights and bishops occupying safe squares that cannot be attacked by enemy pawns.



## Opening Book



# Building
## Prerequisites
Python <br>
C++ <br>
CMake <br>
# Acknowledgments
This chess engine uses the chess-library for move generation and board representation.
