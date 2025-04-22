# -*- coding: utf-8 -*-
import pygame
import chess
import sys
from Elo_Calculation import Elo_Calculation
import random
import time

# --- Cài đặt cơ bản ---
pygame.init()

# Kích thước màn hình và bàn cờ
TOP_MARGIN = 80
WIDTH, HEIGHT = 800, 800  # Chiều cao lớn hơn để chứa menu/thông báo
BOARD_SIZE = 640  # Kích thước bàn cờ (nên chia hết cho 8)
SQUARE_SIZE = BOARD_SIZE // 9
MENU_HEIGHT = HEIGHT - BOARD_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_SQUARE = (238, 238, 210)  # Màu ô sáng
DARK_SQUARE = (118, 150, 86)  # Màu ô tối
HIGHLIGHT_COLOR = (255, 255, 0, 100)  # Màu vàng trong suốt để highlight
MENU_BG_COLOR = (40, 40, 40)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)

# Font chữ (Thử dùng font hệ thống, nếu lỗi sẽ dùng font mặc định)
botRating = 1200
try:
    MENU_FONT = pygame.font.SysFont("consolas", 30)
    MSG_FONT = pygame.font.SysFont("consolas", 20)
except pygame.error:
    print("Font 'consolas' không tìm thấy, sử dụng font mặc định.")
    MENU_FONT = pygame.font.Font(None, 40)  # Font mặc định kích thước 40
    MSG_FONT = pygame.font.Font(None, 30)  # Font mặc định kích thước 30

# Tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Pygame Chess")

# Clock để kiểm soát FPS
clock = pygame.time.Clock()

# Tải background image
try:
    MENU_BACKGROUND = pygame.image.load("img/menu_background.png").convert()
except pygame.error as e:
    print(f"Không thể tải background image: {e}")
    MENU_BACKGROUND = None  # Xử lý nếu không tải được ảnh
FPS = 30

# --- Trạng thái trò chơi ---
game_state = "MENU"  # MENU, ENTER_ELO, PLAYING, GAME_OVER
game_mode = None  # PVP, PVC
board = chess.Board()  # Bàn cờ logic

# --- Biến toàn cục ---
piece_images = {}  # Lưu trữ ảnh quân cờ đã tải và resize
selected_square = None  # Ô đang được chọn (dạng chess.Square index)
source_square = None  # Ô gốc của quân cờ được chọn
valid_moves_for_selected_piece = []  # Danh sách các đối tượng chess.Move hợp lệ

# Biến cho giao diện
menu_buttons = []  # Lưu trữ Rect của các nút menu
back_button_game_rect = None  # Rect của nút Back khi đang chơi
back_button_over_rect = None  # Rect của nút Back khi game over
game_over_message = ""  # Thông báo khi kết thúc game

# --- ELO input ---
elo_input = ""  # Lưu trữ giá trị ELO người chơi nhập
is_typing_elo = False  # Trạng thái nhập ELO

# --- Computer move ---
computer_move_pending = False
last_computer_move_time = 0
computer_color = chess.BLACK

# --- Biến toàn cục cho đồng hồ ---
WHITE_TIME = 15 * 60 * 1000  # 15 phút (ms)
BLACK_TIME = 15 * 60 * 1000  # 15 phút (ms)
white_timer = WHITE_TIME
black_timer = BLACK_TIME
last_timer_update = pygame.time.get_ticks()


# --- Tải tài nguyên ---
def load_piece_images():
    """Tải hình ảnh quân cờ từ thư mục img và resize."""
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        try:
            img_path = f"img/{piece}.png"
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
            piece_images[piece] = img
        except pygame.error as e:
            print(f"Lỗi tải ảnh {img_path}: {e}")
            print("Hãy đảm bảo thư mục 'img' tồn tại cùng cấp với file code")
            print("và chứa đủ 12 file ảnh quân cờ được đặt tên đúng (vd: wP.png, bN.png,...).")
            pygame.quit();
            sys.exit()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {img_path}")
            print("Hãy đảm bảo thư mục 'img' tồn tại cùng cấp với file code")
            print("và chứa đủ 12 file ảnh quân cờ được đặt tên đúng (vd: wP.png, bN.png,...).")
            pygame.quit();
            sys.exit()


# --- Hàm vẽ bàn cờ ---
def draw_board(surface):
    """Vẽ các ô vuông sáng tối của bàn cờ."""
    for rank in range(8):
        for file in range(8):
            is_light_square = (rank + file) % 2 == 0
            color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
            rect = pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE + TOP_MARGIN, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)


def get_piece_symbol(piece):
    """Lấy ký hiệu để tìm ảnh (vd: 'wP', 'bN')."""
    if piece is None:
        return None
    color_prefix = 'w' if piece.color == chess.WHITE else 'b'
    piece_suffix = piece.symbol().upper()
    return f"{color_prefix}{piece_suffix}"


def draw_pieces(surface, current_board):
    """Vẽ các quân cờ lên bàn cờ (surface)."""
    for rank in range(8):
        for file in range(8):
            square_index = chess.square(file, 7 - rank)
            piece = current_board.piece_at(square_index)
            if piece:
                piece_symbol = get_piece_symbol(piece)
                if piece_symbol in piece_images:
                    screen_x = file * SQUARE_SIZE
                    screen_y = rank * SQUARE_SIZE + TOP_MARGIN
                    surface.blit(piece_images[piece_symbol], (screen_x, screen_y))


# --- Hàm highlight ô cờ ---
def highlight_square(surface, square_index):
    """Highlight ô cờ được chọn."""
    if square_index is not None:
        file = chess.square_file(square_index)
        rank = chess.square_rank(square_index)
        screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
        screen_x = file * SQUARE_SIZE
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        surface.blit(highlight_surface, (screen_x, screen_y))


# --- Hàm highlight nước đi hợp lệ ---
def highlight_valid_moves(surface, moves):
    """Vẽ các chấm tròn nhỏ để chỉ các nước đi hợp lệ."""
    for move in moves:
        target_square = move.to_square
        file = chess.square_file(target_square)
        rank = chess.square_rank(target_square)
        screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
        screen_x = file * SQUARE_SIZE
        center_x = screen_x + SQUARE_SIZE // 2
        center_y = screen_y + SQUARE_SIZE // 2
        pygame.draw.circle(surface, GRAY, (center_x, center_y), SQUARE_SIZE // 6)


def draw_menu(surface):
    """Vẽ menu chính và trả về Rect của các nút."""
    # Vẽ background image
    if MENU_BACKGROUND:
        surface.blit(MENU_BACKGROUND, (0, 0))
    else:
        surface.fill(MENU_BG_COLOR)  # Fallback nếu không có ảnh

    # Cấu hình nút
    button_texts = ["PVP", "PVC"]
    button_rects = []
    button_width = 200  # Kích thước nút
    button_height = 50
    button_y_start = HEIGHT // 2 - 60  # Vị trí y ban đầu của nút

    # Tạo nút
    for i, text in enumerate(button_texts):
        rect = pygame.Rect(WIDTH // 2 - button_width // 2, button_y_start + i * (button_height + 20), button_width, button_height)
        button_rects.append(rect)
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = rect.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER_COLOR if is_hovering else BUTTON_COLOR
        pygame.draw.rect(surface, button_color, rect, border_radius=10)
        btn_text_surf = MENU_FONT.render(text, True, TEXT_COLOR)
        btn_text_rect = btn_text_surf.get_rect(center=rect.center)
        surface.blit(btn_text_surf, btn_text_rect)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click chuột trái
        click_pos = pygame.mouse.get_pos()
        for i, button_rect in enumerate(button_rects):
            if button_rect.collidepoint(click_pos):
                # Reset game state for new game
                global board, selected_square, source_square, valid_moves_for_selected_piece, game_over_message, white_timer, black_timer, last_timer_update, game_mode, is_typing_elo, elo_input
                board = chess.Board()
                selected_square = source_square = None
                valid_moves_for_selected_piece = []
                game_over_message = ""
                white_timer = WHITE_TIME
                black_timer = BLACK_TIME
                last_timer_update = pygame.time.get_ticks()
                elo_input = ""
                is_typing_elo = False

                if i == 0:  # Chế độ PVP
                    game_mode = "PVP"
                    game_state = "PLAYING"
                elif i == 1:  # Chế độ PVC
                    game_mode = "PVC"
                    game_state = "ENTER_ELO"
                    is_typing_elo = True

                print(f"Chế độ đã chọn: {game_mode}")
                break

    return button_rects


def draw_game_info(surface, current_board, current_game_mode):
    """Vẽ khu vực thông tin dưới bàn cờ và trả về Rect nút Back."""
    global game_state, game_mode, board, selected_square, source_square, valid_moves_for_selected_piece, computer_move_pending  # Cần global để có thể thay đổi trạng thái nếu hết cờ ở đây (dù nên tránh)

    info_area_rect = pygame.Rect(0, BOARD_SIZE, WIDTH, MENU_HEIGHT)
    pygame.draw.rect(surface, MENU_BG_COLOR, info_area_rect)

    # Lượt đi
    turn_text = "White's Turn" if current_board.turn == chess.WHITE else "Black's Turn"
    turn_surf = MSG_FONT.render(turn_text, True, TEXT_COLOR)
    turn_rect = turn_surf.get_rect(midleft=(20, BOARD_SIZE + MENU_HEIGHT * 0.25 + 60))
    surface.blit(turn_surf, turn_rect)

    # Chế độ chơi
    mode_text = f"Mode: {current_game_mode}"
    mode_surf = MSG_FONT.render(mode_text, True, TEXT_COLOR)
    mode_rect = mode_surf.get_rect(midright=(WIDTH - 20, BOARD_SIZE + MENU_HEIGHT * 0.25))
    surface.blit(mode_surf, mode_rect)

    # Trạng thái game (Check, Checkmate, Stalemate, ...)
    status_text = ""
    is_game_currently_over = False  # Chỉ kiểm tra, không thay đổi game_state ở đây

    if current_board.is_checkmate():
        winner = "Black" if current_board.turn == chess.WHITE else "White"
        status_text = f"CHECKMATE! {winner} wins."
        is_game_currently_over = True
    elif current_board.is_stalemate():
        status_text = "STALEMATE! Draw."
        is_game_currently_over = True
    elif current_board.is_insufficient_material():
        status_text = "DRAW: Insufficient Material."
        is_game_currently_over = True
    elif current_board.is_seventyfive_moves():
        status_text = "DRAW: 75-move rule."
        is_game_currently_over = True
    elif current_board.is_fivefold_repetition():
        status_text = "DRAW: Fivefold Repetition."
        is_game_currently_over = True
    elif current_board.is_check():
        status_text = "CHECK!"

    if status_text:
        status_color = (255, 100, 100) if is_game_currently_over else (255, 200, 0)  # Đỏ nếu hết, Vàng nếu Chiếu
        status_surf = MSG_FONT.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(midleft=(20, BOARD_SIZE + MENU_HEIGHT * 0.75))
        surface.blit(status_surf, status_rect)

    # Nút Back to Menu (khi đang chơi)
    back_rect = pygame.Rect(WIDTH - 160, BOARD_SIZE + MENU_HEIGHT * 0.6, 140, 40)
    mouse_pos = pygame.mouse.get_pos()
    hover = back_rect.collidepoint(mouse_pos)
    btn_color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(surface, btn_color, back_rect, border_radius=5)
    back_text_surf = MSG_FONT.render("Back to Menu", True, TEXT_COLOR)
    back_text_rect = back_text_surf.get_rect(center=back_rect.center)
    surface.blit(back_text_surf, back_text_rect)

    return back_rect  # Trả về Rect của nút


def get_game_over_message(current_board):
    """Lấy thông báo kết thúc trò chơi dựa vào trạng thái bàn cờ."""
    if current_board.is_checkmate():
        winner = "Black" if current_board.turn == chess.WHITE else "White"
        return f"Checkmate! {winner} Wins."
    elif current_board.is_stalemate():
        return "Stalemate! It's a Draw."
    elif current_board.is_insufficient_material():
        return "Draw: Insufficient Material."
    elif current_board.is_seventyfive_moves():
        return "Draw: 75-move rule."
    elif current_board.is_fivefold_repetition():
        return "Draw: Fivefold Repetition."
    else:
        # Có thể thêm các luật hòa khác nếu cần
        return "Game Over!"  # Trường hợp khác


def draw_game_over(surface, message):
    """Vẽ màn hình Game Over với thông báo và nút Back."""
    # Vẽ lớp phủ màu đen bán trong suốt lên trên màn hình game
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt 180/255
    surface.blit(overlay, (0, 0))

    # Hiển thị thông báo kết thúc
    end_text_surf = MENU_FONT.render(message, True, WHITE)
    end_text_rect = end_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(end_text_surf, end_text_rect)

    # Nút Back to Menu (trên màn hình Game Over)
    back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
    mouse_pos = pygame.mouse.get_pos()
    hover = back_rect.collidepoint(mouse_pos)
    btn_color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(surface, btn_color, back_rect, border_radius=5)
    back_text_surf = MSG_FONT.render("Back to Menu", True, TEXT_COLOR)
    back_text_rect = back_text_surf.get_rect(center=back_rect.center)
    surface.blit(back_text_surf, back_text_rect)
    return back_rect  # Trả về Rect của nút


# --- Hàm trợ giúp: Lấy ô cờ từ tọa độ chuột ---
def get_square_from_mouse(pos):
    """Chuyển đổi tọa độ chuột (x, y) thành chess.Square index (0-63)."""
    x, y = pos
    if x < 0 or x >= BOARD_SIZE or y < TOP_MARGIN or y >= BOARD_SIZE + TOP_MARGIN:
        return None
    file = x // SQUARE_SIZE
    rank = 7 - ((y - TOP_MARGIN) // SQUARE_SIZE)
    return chess.square(file, rank)


# --- Logic Máy Chơi ---
def make_random_computer_move(current_board):
    """Thêm code"""
    time.sleep(1)  # Để máy đi không quá nhanh
    legal_moves = list(current_board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        return move
    return False  # Trả về False nếu không có nước đi hợp lệ


# --- Hàm vẽ đồng hồ ---
def draw_timer(surface, time_left, is_top):
    """Vẽ đồng hồ đếm ngược."""
    minutes = time_left // 60000
    seconds = (time_left % 60000) // 1000
    timer_text = f"{minutes:02}:{seconds:02}"
    timer_surf = MENU_FONT.render(timer_text, True, TEXT_COLOR)
    timer_rect = timer_surf.get_rect(center=(WIDTH // 2, 30 if is_top else HEIGHT - 30))
    surface.blit(timer_surf, timer_rect)


# --- Cập nhật đồng hồ ---
def update_timers():
    """Cập nhật thời gian còn lại cho mỗi bên."""
    global white_timer, black_timer, last_timer_update, game_state

    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - last_timer_update
    last_timer_update = current_time

    if game_state == "PLAYING":
        if board.turn == chess.WHITE:
            white_timer -= elapsed_time
            if white_timer <= 0:
                white_timer = 0
                game_state = "GAME_OVER"
                print("Black wins! White ran out of time.")
        else:
            black_timer -= elapsed_time
            if black_timer <= 0:
                black_timer = 0
                game_state = "GAME_OVER"
                print("White wins! Black ran out of time.")


# --- Vòng lặp chính ---
load_piece_images()
running = True

while running:
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    # --- Xử lý sự kiện ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click chuột trái
                click_pos = pygame.mouse.get_pos()
                for i, button_rect in enumerate(menu_buttons):
                    if button_rect.collidepoint(click_pos):
                        # Reset game state for new game
                        board = chess.Board()
                        selected_square = source_square = None
                        valid_moves_for_selected_piece = []
                        game_over_message = ""
                        white_timer = WHITE_TIME
                        black_timer = BLACK_TIME
                        last_timer_update = pygame.time.get_ticks()

                        if i == 0:  # Chế độ PVP
                            game_mode = "PVP"
                            game_state = "PLAYING"
                        elif i == 1:  # Chế độ PVC
                            game_mode = "PVC"
                            game_state = "ENTER_ELO"
                            elo_input = ""  # Reset ELO input
                            is_typing_elo = True

                        print(f"Chế độ đã chọn: {game_mode}")
                        break

        elif game_state == "ENTER_ELO":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Nhấn Enter để xác nhận
                    if elo_input.isdigit():  # Kiểm tra ELO hợp lệ
                        print(f"Player ELO: {elo_input}")
                        game_state = "PLAYING"
                        computer_color = chess.BLACK  # Máy mặc định là Đen
                        last_timer_update = pygame.time.get_ticks()
                    else:
                        print("Invalid ELO. Please enter a number.")
                elif event.key == pygame.K_BACKSPACE:  # Xóa ký tự
                    elo_input = elo_input[:-1]
                else:
                    elo_input += event.unicode  # Thêm ký tự vào ELO

        elif game_state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click chuột trái
                click_pos = pygame.mouse.get_pos()

                # Kiểm tra click nút Back to Menu
                if back_button_game_rect and back_button_game_rect.collidepoint(click_pos):
                    game_state = "MENU"
                    game_mode = None
                    board = chess.Board()
                    selected_square = source_square = None
                    valid_moves_for_selected_piece = []
                    computer_move_pending = False
                    elo_input = ""
                    is_typing_elo = False
                    continue

                # Xác định xem người chơi có được tương tác không
                is_player_interaction_allowed = (game_mode == "PVP") or \
                                                (game_mode == "PVC" and board.turn != computer_color)

                if is_player_interaction_allowed:
                    clicked_square = get_square_from_mouse(click_pos)
                    if clicked_square is not None:
                        piece_at_click = board.piece_at(clicked_square)

                        if selected_square is None:
                            if piece_at_click and piece_at_click.color == board.turn:
                                selected_square = clicked_square
                                source_square = clicked_square
                                valid_moves_for_selected_piece = [
                                    m for m in board.legal_moves if m.from_square == source_square
                                ]
                                if not valid_moves_for_selected_piece:
                                    selected_square = source_square = None
                        else:
                            target_square = clicked_square
                            move_to_try = chess.Move(source_square, target_square)

                            piece_type = board.piece_type_at(source_square)
                            if piece_type == chess.PAWN:
                                target_rank = chess.square_rank(target_square)
                                if (board.turn == chess.WHITE and target_rank == 7) or \
                                   (board.turn == chess.BLACK and target_rank == 0):
                                    move_to_try = chess.Move(source_square, target_square, promotion=chess.QUEEN)

                            if move_to_try in valid_moves_for_selected_piece:
                                board.push(move_to_try)
                                print(f"Player ({'White' if board.turn != chess.WHITE else 'Black'}) moves: {move_to_try.uci()}")
                                selected_square = source_square = None
                                valid_moves_for_selected_piece = []
                                if board.is_game_over():
                                    game_state = "GAME_OVER"
                                    game_over_message = get_game_over_message(board)
                                    print(f"Game Over: {game_over_message}")

                            elif piece_at_click and piece_at_click.color == board.turn:
                                selected_square = clicked_square
                                source_square = clicked_square
                                valid_moves_for_selected_piece = [
                                    m for m in board.legal_moves if m.from_square == source_square
                                ]
                                if not valid_moves_for_selected_piece:
                                    selected_square = source_square = None
                            else:
                                selected_square = source_square = None
                                valid_moves_for_selected_piece = []
                    else:
                        selected_square = source_square = None
                        valid_moves_for_selected_piece = []

        elif game_state == "GAME_OVER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = pygame.mouse.get_pos()
                if back_button_over_rect and back_button_over_rect.collidepoint(click_pos):
                    game_state = "MENU"
                    game_mode = None
                    board = chess.Board()
                    selected_square = source_square = None
                    valid_moves_for_selected_piece = []
                    computer_move_pending = False

    # --- Cập nhật trạng thái ---
    update_timers()

    # Máy đi cờ (nếu đến lượt và không có pending move)
    if game_mode == "PVC" and board.turn == computer_color and not computer_move_pending and game_state == "PLAYING":
        computer_move_pending = True
        last_computer_move_time = current_time

    if computer_move_pending and (current_time - last_computer_move_time > 500):  # Delay 0.5s
        computer_move = make_random_computer_move(board)
        if computer_move:
            board.push(computer_move)
            print(f"Computer moves: {computer_move.uci()}")
            if board.is_game_over():
                game_state = "GAME_OVER"
                game_over_message = get_game_over_message(board)
                print(f"Game Over: {game_over_message}")
        computer_move_pending = False

    # --- Vẽ màn hình ---
    screen.fill(MENU_BG_COLOR)

    if game_state == "MENU":
        menu_buttons = draw_menu(screen)
        back_button_game_rect = None
        back_button_over_rect = None
    elif game_state == "ENTER_ELO":
        # Vẽ textfield để nhập ELO
        pygame.draw.rect(screen, WHITE, pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40), border_radius=5)
        pygame.draw.rect(screen, BLACK, pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40), 2, border_radius=5)
        elo_surface = MSG_FONT.render(elo_input, True, BLACK)
        screen.blit(elo_surface, (WIDTH // 2 - 90, HEIGHT // 2 - 10))
        instruction_surface = MSG_FONT.render("Enter your ELO and press Enter", True, TEXT_COLOR)
        screen.blit(instruction_surface, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
    elif game_state == "PLAYING":
        board_surface = screen.subsurface(pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        if selected_square is not None:
            highlight_square(board_surface, selected_square)
            highlight_valid_moves(board_surface, valid_moves_for_selected_piece)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = None

        # Vẽ đồng hồ
        draw_timer(screen, black_timer, is_top=True)
        draw_timer(screen, white_timer, is_top=False)

    elif game_state == "GAME_OVER":
        board_surface = screen.subsurface(pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = draw_game_over(screen, game_over_message)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
