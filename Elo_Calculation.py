#Opening nếu muốn nhập thành
"""
def __init__(self):
        # Khai cuộc Reti cơ bản
        self.reti_moves = [
            "Nf3",  # 1. Nf3 - Mở cánh vua, kiểm soát trung tâm
            "d4",  # 2. d4 - Tiếp tục kiểm soát trung tâm
            "c4",  # 3. c4 - Tiến thêm vào trung tâm
            "g3",  # 4. g3 - Chuẩn bị fianchetto
            "Bg2",  # 5. Bg2 - Đưa mã về vị trí kiểm soát tốt
            "O-O"  # 6. Nhập thành
        ]
        # Dữ liệu phản ứng của Đen (chỉ là ví dụ, bạn có thể thêm tùy ý)
        self.reactions = {
            "d5": ["Nf3", "d4", "c4", "g3", "Bg2", "O-O"],  # Đen chơi 1...d5
            "Nf6": ["Nf3", "d4", "c4", "g3", "Bg2", "O-O"],  # Đen chơi 1...Nf6
            "e6": ["Nf3", "d4", "c4", "g3", "Bg2", "O-O"],  # Đen chơi 1...e6
        }
def get_next_move(self, move_sequence):
        # Trả về nước đi tiếp theo trong chuỗi khai cuộc Reti, có thể tùy biến dựa trên phản ứng của Đen.
        position = " ".join(move_sequence)

        # Kiểm tra xem Đen phản ứng như thế nào
        if position == "Nf3":  # Nếu Trắng đã đi Nf3
            last_move = move_sequence[-1]
            if last_move == "d5":
                return self.reactions["d5"][len(move_sequence) - 1]
            elif last_move == "Nf6":
                return self.reactions["Nf6"][len(move_sequence) - 1]
            elif last_move == "e6":
                return self.reactions["e6"][len(move_sequence) - 1]

        # Trả về nước đi cố định nếu chưa có phản ứng từ Đen
        if len(move_sequence) < len(self.reti_moves):
            return self.reti_moves[len(move_sequence)]

        return None  # Không còn nước đi nào để tiếp tục
def build_opening(self):
        #Xây dựng một chuỗi khai cuộc hoàn chỉnh từ Reti
        moves = []
        for move in self.reti_moves:
            moves.append(move)
        return moves
"""

#Opening nếu không muốn nhập thành

def Elo_Cal(rating1, rating2, result):
    if (rating1 > 2400):
        k = 10
    elif rating1 <= 2400 and rating1 > 2000:
        k = 15
    elif rating1 <= 2000 and rating1 > 1600:
        k = 20
    else:
        k = 25
    Qa, Qb = 10 ** (rating1 / 400), 10 ** (rating2 / 400)
    Ea = Qa / (Qa + Qb)
    Eb = Qb / (Qa + Qb)
    if result is True:
        return rating1 + k * (1 - Ea)
    else:
        return rating1 + k * (0 - Eb)
