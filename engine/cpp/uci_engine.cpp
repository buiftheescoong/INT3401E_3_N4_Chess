#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <thread>
#include <chrono>
#include <random>
#include <algorithm>

// Simple UCI chess engine implementation
// Supports 'depth' and 'movetime' options

class UCIEngine {
private:
    bool running;
    int searchDepth;
    int moveTimeMs;
    std::string position;
    std::mt19937 rng;

    // Parse a move from UCI format (e.g., "e2e4")
    std::string parseMove(const std::string& fen, const std::string& moveStr) {
        // This is just a placeholder in a real engine
        // you would validate and convert the move properly
        return moveStr;
    }

    // Generate a random legal move
    std::string generateRandomMove(const std::string& fen) {
        // These are some example moves - in a real engine
        // you would generate actual legal moves from the position
        std::vector<std::string> possibleMoves = {
            "e2e4", "d2d4", "g1f3", "b1c3", "e7e5", "e7e6", "c7c5", "c7c6"
        };

        std::uniform_int_distribution<int> dist(0, possibleMoves.size() - 1);
        return possibleMoves[dist(rng)];
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