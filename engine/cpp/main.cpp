#include <iostream>
#include <string>
#include "../../chess/chess.cpp"    // đường dẫn đến thư viện chess
#include "ComputeMove.cpp"    // đường dẫn đến file bạn vừa gửi ở trên

int main() {
    // std::string fen;
    // std::cout << "Nhập FEN của trạng thái bàn cờ: ";
    // std::getline(std::cin, fen);

    try {
        chess::Board board("r1b2k2/pp3ppp/8/2q1p3/2B1P3/3n4/PPP3PP/RNQr1R1K b Qq - 2 4");  // tạo đối tượng board từ FEN

        chess::Move move = get_best_move(board);  // tìm best move trong 10s
        std::cout << move << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Lỗi khi tạo board hoặc tìm move: " << e.what() << std::endl;
    }

    return 0;
}