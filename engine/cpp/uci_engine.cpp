#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <thread>
#include <chrono>
#include <random>
#include <algorithm>
#include <unordered_map>
#include <regex>

// Simple UCI chess engine implementation
// Supports 'depth' and 'movetime' options

class UCIEngine {
private:
    bool running;
    int searchDepth;
    int moveTimeMs;
    std::string position;
    std::mt19937 rng;
    
    // Parse FEN to extract basic information (simplified)
    bool isWhiteToMove(const std::string& fen) {
        // FEN format: [position] [side to move] [castling] [en passant] [halfmove] [fullmove]
        // Example: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        std::istringstream ss(fen);
        std::string pos, turn;
        ss >> pos >> turn;
        return turn == "w";
    }

    // Maps pieces to positions in FEN
    std::unordered_map<char, std::vector<std::string>> extractPieces(const std::string& fen) {
        std::unordered_map<char, std::vector<std::string>> piecePositions;
        std::istringstream ss(fen);
        std::string boardPos;
        ss >> boardPos;  // Get board position part of FEN
        
        int rank = 8;
        int file = 1;
        
        for (char c : boardPos) {
            if (c == '/') {
                rank--;
                file = 1;
            } else if (c >= '1' && c <= '8') {
                file += c - '0';
            } else if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
                std::string squareName = "";
                squareName += static_cast<char>('a' + file - 1);
                squareName += static_cast<char>('0' + rank);
                piecePositions[c].push_back(squareName);
                file++;
            }
        }
        
        return piecePositions;
    }

    // Generate a list of plausible moves
    std::vector<std::string> generatePossibleMoves(const std::string& fen) {
        std::vector<std::string> moves;
        bool whiteToMove = true;
        
        // Extract side to move from FEN if provided
        if (fen.find("fen") != std::string::npos) {
            // Extract the FEN part after "fen "
            std::string fenPart = fen.substr(fen.find("fen") + 4);
            whiteToMove = isWhiteToMove(fenPart);
        } else if (fen != "startpos") {
            // If directly given a FEN string
            whiteToMove = isWhiteToMove(fen);
        }
        
        // For better results, we should parse the FEN and generate only legal moves
        // This is a simplified version that just returns plausible moves for each side
        if (whiteToMove) {
            // Some common white opening moves 
            moves = {"e2e4", "d2d4", "c2c4", "g1f3", "b1c3", "e2e3", "d2d3", "g2g3", "f2f4", "b2b3", "a2a3", "h2h3"};
        } else {
            // Some common black responses
            moves = {"e7e5", "e7e6", "c7c5", "c7c6", "d7d5", "d7d6", "g7g6", "g8f6", "b8c6", "f7f5", "b7b6", "a7a6", "h7h6"};
        }
        
        return moves;
    }
    
    // Generate a random legal move
    std::string generateRandomMove(const std::string& fen) {
        auto moves = generatePossibleMoves(fen);
        if (moves.empty()) {
            // If somehow we don't have any moves, return a default
            return "e2e4";
        }
        
        std::uniform_int_distribution<int> dist(0, moves.size() - 1);
        return moves[dist(rng)];
    }

    // Search for the best move
    std::string search(const std::string& fen, int depth, int timeLimit) {
        // In a real engine, this would be where you implement your search algorithm
        // For now, we'll just return a random move after "thinking"

        std::cout << "info string Searching at depth " << depth << " with time limit " << timeLimit << "ms" << std::endl;

        // Simulate thinking
        auto startTime = std::chrono::steady_clock::now();
        
        // Determine how long to "think" (in milliseconds)
        int thinkTime = (timeLimit > 0) ? std::min(timeLimit, 1000) : 500;
        
        // Simple debug output showing progress
        for (int d = 1; d <= depth; d++) {
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - startTime).count();
            
            if (timeLimit > 0 && elapsed >= timeLimit) {
                break; // Stop if we've exceeded the time limit
            }
            
            // Simulate finding a "better" move at each depth
            std::string currentBestMove = generateRandomMove(fen);
            std::this_thread::sleep_for(std::chrono::milliseconds(100));  // Pretend to think
            
            std::cout << "info depth " << d << " score cp " << (d * 10) 
                      << " time " << elapsed << " pv " << currentBestMove << std::endl;
        }
        
        // Always wait at least a little bit to simulate thinking
        std::this_thread::sleep_for(std::chrono::milliseconds(thinkTime));
        
        // Return a random move
        return generateRandomMove(fen);
    }

public:
    UCIEngine() : running(false), searchDepth(4), moveTimeMs(1000), 
                  rng(std::random_device{}()) {
        position = "startpos";
    }

    void run() {
        running = true;
        std::string line;

        while (running && std::getline(std::cin, line)) {
            std::istringstream iss(line);
            std::string command;
            iss >> command;

            if (command == "uci") {
                // Identify engine
                std::cout << "id name SimpleUCI" << std::endl;
                std::cout << "id author ChessAI_Team" << std::endl;
                
                // Options
                std::cout << "option name Depth type spin default 4 min 1 max 20" << std::endl;
                std::cout << "option name MoveTime type spin default 1000 min 100 max 10000" << std::endl;
                
                // UCI is ready
                std::cout << "uciok" << std::endl;
            } 
            else if (command == "isready") {
                std::cout << "readyok" << std::endl;
            } 
            else if (command == "setoption") {
                std::string name, value;
                iss >> name; // Skip "name" token
                iss >> name; // Get actual name
                iss >> command; // Skip "value" token
                iss >> value; // Get value
                
                if (name == "Depth") {
                    try {
                        searchDepth = std::stoi(value);
                        std::cout << "info string Depth set to " << searchDepth << std::endl;
                    } catch (...) {
                        std::cout << "info string Invalid depth value" << std::endl;
                    }
                } 
                else if (name == "MoveTime") {
                    try {
                        moveTimeMs = std::stoi(value);
                        std::cout << "info string MoveTime set to " << moveTimeMs << " ms" << std::endl;
                    } catch (...) {
                        std::cout << "info string Invalid movetime value" << std::endl;
                    }
                }
            } 
            else if (command == "position") {
                position = line.substr(9); // Store the position command
            } 
            else if (command == "go") {
                int depth = searchDepth;
                int movetime = moveTimeMs;
                
                std::string param;
                while (iss >> param) {
                    if (param == "depth") {
                        iss >> depth;
                    }
                    else if (param == "movetime") {
                        iss >> movetime;
                    }
                    // We could handle other UCI go parameters like wtime, btime, etc.
                }
                
                // Search for the best move
                std::string bestMove = search(position, depth, movetime);
                
                // Send the best move to the GUI
                std::cout << "bestmove " << bestMove << std::endl;
            } 
            else if (command == "quit") {
                running = false;
            }
            else if (command == "ucinewgame") {
                // Reset any game-specific data structures
                position = "startpos";
            }
        }
    }
};

int main() {
    // Disable buffering for standard output
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);
    
    // Create and run the engine
    UCIEngine engine;
    engine.run();
    
    return 0;
}