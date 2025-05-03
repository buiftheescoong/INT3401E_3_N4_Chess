#include <iostream>
#include <string>
#include "../../chess/chess.cpp"    // đường dẫn đến thư viện chess
#include "ComputeMove.cpp"    // đường dẫn đến file bạn vừa gửi ở trên

int main() {
    // std::string fen;
    // std::cout << "Nhập FEN của trạng thái bàn cờ: ";
    // std::getline(std::cin, fen);

    try {
        chess::Board board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");  // tạo đối tượng board từ FEN

        chess::Move move = get_best_move(board, 200);  // tìm best move trong 10s
        std::cout << "Best move: " << move << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Lỗi khi tạo board hoặc tìm move: " << e.what() << std::endl;
    }

    return 0;
}
