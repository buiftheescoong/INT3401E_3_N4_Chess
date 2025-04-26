# -*- coding: utf-8 -*-
import pygame
import chess
import sys
from Elo_Calculation import Elo_Cal
import random
import time

from engine.ComputeMove import get_best_move
# --- Cài đặt cơ bản ---
pygame.init()

# Kích thước màn hình và bàn cờ
TOP_MARGIN = 50
WIDTH, HEIGHT = 900, 800  # Tăng chiều rộng để thêm sidebar
BOARD_SIZE = 640  # Kích thước bàn cờ (nên chia hết cho 8)
SQUARE_SIZE = BOARD_SIZE // 9
MENU_HEIGHT = HEIGHT - BOARD_SIZE
SIDEBAR_WIDTH = 250  # Chiều rộng của sidebar
SIDEBAR_X = WIDTH - SIDEBAR_WIDTH  # Vị trí X bắt đầu của sidebar
SIDEBAR_HEIGHT = BOARD_SIZE  # Chiều cao của sidebar (chỉ đến hết bàn cờ)

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
botRating = 1200 #tên biến lưu elo của bot
botWin = 0 #biến theo dõi trạng thái thắng thua của bot: 1 = thắng, -1 = thua, 0 = chưa có kết quả hoặc hòa
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
game_state = "MENU"  # MENU, ENTER_ELO, PLAYING, GAME_OVER, PROMOTION
game_mode = None  # PVP, PVC
board = chess.Board()  # Bàn cờ logic

# --- Biến cho promotion ---
promotion_move = None  # Lưu nước đi chờ phong cấp
promotion_source = None  # Ô nguồn của quân cờ phong cấp
promotion_target = None  # Ô đích của quân cờ phong cấp
promotion_options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]  # Các quân có thể phong cấp
promotion_rects = []  # Rect của các lựa chọn phong cấp


# --- Biến toàn cục ---
piece_images = {}  # Lưu trữ ảnh quân cờ đã tải và resize
selected_square = None  # Ô đang được chọn (dạng chess.Square index)
source_square = None  # Ô gốc của quân cờ được chọn
valid_moves_for_selected_piece = []  # Danh sách các đối tượng chess.Move hợp lệ
last_move = None  # Lưu trữ nước đi cuối cùng

# --- Thêm biến theo dõi thời gian suy nghĩ của bot ---
bot_thinking_start_time = 0  # Thời điểm bot bắt đầu suy nghĩ
bot_is_thinking = False  # Trạng thái bot đang suy nghĩ


# --- Biến lịch sử nước đi ---
move_history = []  # Lưu trữ tất cả các nước đi
current_move_index = -1  # Vị trí hiện tại trong lịch sử nước đi
undo_button_rect = None  # Rect của nút Undo
redo_button_rect = None  # Rect của nút Redo
is_after_undo = False  # Cờ để ngăn máy đi ngay sau khi undo

# --- Biến cho thanh cuộn ---
scroll_dragging = False  # Đang kéo thanh cuộn
thumb_rect = None  # Rect của nút cuộn (thumb)
scroll_start_y = 0  # Vị trí y ban đầu khi bắt đầu kéo
scroll_offset = 0  # Vị trí hiện tại của thanh cuộn (0 -> 1)
scrollbar_track_rect = None  # Rect của vùng thanh cuộn
move_list_rects = []  # Danh sách rect của các nước đi được hiển thị


# Biến cho giao diện
menu_buttons = []  # Lưu trữ Rect của các nút menu
back_button_game_rect = None  # Rect của nút Back khi đang chơi
back_button_over_rect = None  # Rect của nút Back khi game over
game_over_message = ""  # Thông báo khi kết thúc game

# --- ELO input ---
elo_input = 0  # Lưu trữ giá trị ELO người chơi nhập
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
    """Highlight các ô đích của nước đi hợp lệ."""
    for move in moves:
        target_square = move.to_square
        file = chess.square_file(target_square)
        rank = chess.square_rank(target_square)
        screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
        screen_x = file * SQUARE_SIZE

        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        surface.blit(highlight_surface, (screen_x, screen_y))


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
                elo_input = 0
                is_typing_elo = False

                if i == 0:  # Chế độ PVP
                    game_mode = "PVP"
                    game_state = "PLAYING"
                    reset_move_history()  # Reset lịch sử nước đi khi bắt đầu trò chơi mới
                    last_move = None
                elif i == 1:  # Chế độ PVC
                    game_mode = "PVC"
                    game_state = "ENTER_ELO"
                    elo_input = ""  # Reset ELO input
                    is_typing_elo = True
                    reset_move_history()  # Reset lịch sử nước đi khi bắt đầu trò chơi mới
                    last_move = None

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

    # Elo ratings
    if current_game_mode == "PVC":
        elo_text = f"Player's Elo : {elo_input}    Computer's Elo : {botRating}"
        elo_surf = MSG_FONT.render(elo_text, True, TEXT_COLOR)
        elo_rect = elo_surf.get_rect(midleft=(20, BOARD_SIZE + MENU_HEIGHT * 0.5))
        surface.blit(elo_surf, elo_rect)

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
    global botWin, game_mode, computer_color
    
    if current_board.is_checkmate():
        winner = "Black" if current_board.turn == chess.WHITE else "White"
        
        # Cập nhật biến botWin nếu đang ở chế độ PVC
        if game_mode == "PVC":
            if (winner == "Black" and computer_color == chess.BLACK) or (winner == "White" and computer_color == chess.WHITE):
                botWin = 1  # Bot thắng
                print("Bot wins! botWin =", botWin)
            else:
                botWin = -1  # Bot thua
                print("Player wins! botWin =", botWin)
        
        return f"Checkmate! {winner} Wins."
    elif current_board.is_stalemate():
        # Trường hợp hòa cờ, giữ nguyên botWin = 0
        print("Draw game! botWin =", botWin)
        return "Stalemate! It's a Draw."
    elif current_board.is_insufficient_material():
        # Trường hợp hòa cờ, giữ nguyên botWin = 0
        print("Draw game! botWin =", botWin)
        return "Draw: Insufficient Material."
    elif current_board.is_seventyfive_moves():
        # Trường hợp hòa cờ, giữ nguyên botWin = 0
        print("Draw game! botWin =", botWin)
        return "Draw: 75-move rule."
    elif current_board.is_fivefold_repetition():
        # Trường hợp hòa cờ, giữ nguyên botWin = 0
        print("Draw game! botWin =", botWin)
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
    """Lấy nước đi tốt nhất từ bot và cập nhật thời gian trong khi bot đang suy nghĩ."""
    global black_timer, white_timer, last_timer_update, bot_thinking_start_time, bot_is_thinking
    
    # Thời điểm bắt đầu suy nghĩ
    bot_thinking_start_time = pygame.time.get_ticks()
    bot_is_thinking = True
    
    # Lưu thời gian trước khi bot bắt đầu suy nghĩ
    timer_before_thinking = black_timer if board.turn == chess.BLACK else white_timer
    
    try:
        # Gọi hàm get_best_move để bot suy nghĩ
        move, type = get_best_move(current_board)
        
        # Tính toán thời gian đã trôi qua khi bot suy nghĩ
        thinking_time_elapsed = pygame.time.get_ticks() - bot_thinking_start_time
        
        # Cập nhật thời gian cho bot (trừ thời gian suy nghĩ)
        if board.turn == chess.BLACK:
            black_timer = timer_before_thinking - thinking_time_elapsed
            if black_timer < 0:
                black_timer = 0
        else:
            white_timer = timer_before_thinking - thinking_time_elapsed
            if white_timer < 0:
                white_timer = 0
                
        # Cập nhật thời điểm cuối cùng để tránh bị trừ thêm thời gian
        last_timer_update = pygame.time.get_ticks()
        
        if move:
            print(type)
            bot_is_thinking = False
            return move
        else:
            # Nếu không tìm được nước đi từ hàm heuristic, tạo nước đi ngẫu nhiên
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                bot_is_thinking = False
                return None
            random_move = random.choice(legal_moves)
            print("random")
            bot_is_thinking = False
            return random_move
    except Exception as e:
        print(f"Lỗi khi bot suy nghĩ: {str(e)}")
        bot_is_thinking = False
        # Trả về một nước đi ngẫu nhiên nếu có lỗi
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        return random.choice(legal_moves)

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


# --- Hàm xử lý lịch sử nước đi ---
def add_move_to_history(move):
    """Thêm nước đi vào lịch sử."""
    global move_history, current_move_index
    
    # Nếu chúng ta đang ở giữa lịch sử và đi một nước mới,
    # cắt bỏ lịch sử từ vị trí hiện tại
    if current_move_index < len(move_history) - 1:
        move_history = move_history[:current_move_index + 1]
    
    move_history.append(move)
    current_move_index = len(move_history) - 1
    print(f"Thêm nước đi vào lịch sử: {move.uci()}, index: {current_move_index}")

def undo_move():
    """Hoàn tác nước đi gần nhất."""
    global board, current_move_index, is_after_undo, last_move
    
    if current_move_index >= 0:
        board.pop()
        current_move_index -= 1
        is_after_undo = True
        
        # Cập nhật last_move sau khi undo
        if current_move_index >= 0:
            last_move = move_history[current_move_index]
        else:
            last_move = None
            
        print(f"Hoàn tác nước đi, hiện tại ở vị trí {current_move_index + 1}")
        return True
    return False

def redo_move():
    """Làm lại nước đi đã hoàn tác."""
    global board, current_move_index, move_history, is_after_undo, last_move
    
    if current_move_index < len(move_history) - 1:
        next_move = move_history[current_move_index + 1]
        board.push(next_move)
        current_move_index += 1
        is_after_undo = True
        # Cập nhật last_move sau khi redo
        last_move = next_move
        print(f"Làm lại nước đi, hiện tại ở vị trí {current_move_index + 1}")
        return True
    return False

def reset_move_history():
    """Đặt lại lịch sử nước đi."""
    global move_history, current_move_index
    move_history = []
    current_move_index = -1
    print("Đặt lại lịch sử nước đi")

def draw_move_history_sidebar(surface):
    """Vẽ sidebar chứa lịch sử nước đi và nút undo/redo."""
    global undo_button_rect, redo_button_rect, thumb_rect, scrollbar_track_rect, move_list_rects
    
    # Reset danh sách các rect cho mỗi nước đi
    move_list_rects = []
    
    # Vẽ nền sidebar
    sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
    pygame.draw.rect(surface, MENU_BG_COLOR, sidebar_rect)
    pygame.draw.line(surface, WHITE, (SIDEBAR_X, 0), (SIDEBAR_X, SIDEBAR_HEIGHT), 2)
    
    # Vẽ tiêu đề
    title_surf = MSG_FONT.render("Lịch sử nước đi", True, TEXT_COLOR)
    title_rect = title_surf.get_rect(center=(SIDEBAR_X + SIDEBAR_WIDTH // 2, 30))
    surface.blit(title_surf, title_rect)
    
    # Vẽ nút undo và redo
    button_width = SIDEBAR_WIDTH - 20
    button_height = 40
    button_margin = 10
    
    # Nút Undo (chỉ kích hoạt nếu có nước để undo)
    undo_button_rect = pygame.Rect(SIDEBAR_X + 10, 60, button_width, button_height)
    undo_color = BUTTON_COLOR if current_move_index >= 0 else (50, 50, 50)
    pygame.draw.rect(surface, undo_color, undo_button_rect, border_radius=5)
    undo_text = MSG_FONT.render("Undo", True, TEXT_COLOR)
    undo_text_rect = undo_text.get_rect(center=undo_button_rect.center)
    surface.blit(undo_text, undo_text_rect)
    
    # Nút Redo (chỉ kích hoạt nếu có nước để redo)
    redo_button_rect = pygame.Rect(SIDEBAR_X + 10, 60 + button_height + button_margin, button_width, button_height)
    redo_color = BUTTON_COLOR if current_move_index < len(move_history) - 1 else (50, 50, 50)
    pygame.draw.rect(surface, redo_color, redo_button_rect, border_radius=5)
    redo_text = MSG_FONT.render("Redo", True, TEXT_COLOR)
    redo_text_rect = redo_text.get_rect(center=redo_button_rect.center)
    surface.blit(redo_text, redo_text_rect)
    
    # Vẽ danh sách nước đi với thanh cuộn
    move_list_start_y = 60 + (button_height + button_margin) * 2 + 20
    move_height = 25
    
    # Tính toán khu vực hiển thị danh sách nước đi
    list_view_height = SIDEBAR_HEIGHT - move_list_start_y - 20  # Trừ padding dưới
    max_visible_moves = list_view_height // move_height
    
    # Vẽ khung danh sách nước đi
    list_view_rect = pygame.Rect(SIDEBAR_X + 10, move_list_start_y, 
                                SIDEBAR_WIDTH - 30, list_view_height)
    pygame.draw.rect(surface, (30, 30, 30), list_view_rect, border_radius=5)
    
    # Vẽ thanh cuộn
    scrollbar_width = 10
    scrollbar_track_rect = pygame.Rect(SIDEBAR_X + SIDEBAR_WIDTH - 20, move_list_start_y, 
                                       scrollbar_width, list_view_height)
    pygame.draw.rect(surface, (70, 70, 70), scrollbar_track_rect, border_radius=5)
    
    if move_history:
        total_moves = len(move_history)
        
        # Tính vị trí bắt đầu hiển thị
        if total_moves <= max_visible_moves:
            # Hiển thị tất cả nếu có thể
            start_idx = 0
            scroll_ratio = 0  # Không cần cuộn
            thumb_height = list_view_height
        else:
            # Vị trí cuộn dựa vào current_move_index hoặc scroll_offset
            if current_move_index >= 0:
                # Tự động cuộn để hiển thị nước đi hiện tại
                scroll_ratio = min(1, max(0, current_move_index / (total_moves - 1)))
            else:
                scroll_ratio = scroll_offset
            
            # Vị trí bắt đầu để current_move_index nằm gần giữa viewport
            middle_offset = max_visible_moves // 2
            if current_move_index < middle_offset:
                start_idx = 0
            elif current_move_index >= total_moves - middle_offset:
                start_idx = max(0, total_moves - max_visible_moves)
            else:
                start_idx = max(0, current_move_index - middle_offset)
            
            # Áp dụng vị trí cuộn thủ công nếu người dùng đang cuộn
            if scroll_dragging:
                start_idx = int(scroll_ratio * (total_moves - max_visible_moves))
                start_idx = max(0, min(start_idx, total_moves - max_visible_moves))
            
            # Vẽ thumb với kích thước tỷ lệ với số nước có thể thấy
            thumb_height = max(50, list_view_height * max_visible_moves / total_moves)
            
        # Tính vị trí thumb
        thumb_y = move_list_start_y + (list_view_height - thumb_height) * scroll_ratio
        thumb_rect = pygame.Rect(SIDEBAR_X + SIDEBAR_WIDTH - 20, thumb_y, 
                                scrollbar_width, thumb_height)
        pygame.draw.rect(surface, BUTTON_COLOR, thumb_rect, border_radius=5)
        
        end_idx = min(start_idx + max_visible_moves, total_moves)
        
        # Vẽ các nước đi trong vùng nhìn thấy
        move_list_rects = []  # Lưu rect của các nước đi
        for i, move in enumerate(move_history[start_idx:end_idx]):
            idx = start_idx + i
            # Định dạng số nước đi (ví dụ: "1. e2e4" cho trắng, "1... e7e5" cho đen)
            if idx % 2 == 0:  # Nước đi của trắng
                move_number = (idx // 2) + 1
                move_text = f"{move_number}. {move.uci()}"
            else:  # Nước đi của đen
                move_number = (idx // 2) + 1
                move_text = f"{move_number}... {move.uci()}"
            
            # Highlight nước đi hiện tại
            text_color = (255, 255, 0) if idx == current_move_index else TEXT_COLOR
            bg_color = (50, 50, 50) if idx == current_move_index else None
            
            move_surf = MSG_FONT.render(move_text, True, text_color)
            y_pos = move_list_start_y + 5 + i * move_height
            
            # Vẽ text trong vùng hiển thị
            if move_list_start_y <= y_pos < move_list_start_y + list_view_height - move_height:
                clip_rect = pygame.Rect(SIDEBAR_X + 15, move_list_start_y, 
                                      SIDEBAR_WIDTH - 35, list_view_height)
                old_clip = surface.get_clip()
                surface.set_clip(clip_rect)
                
                # Lưu rect cho việc kiểm tra click
                move_rect = pygame.Rect(SIDEBAR_X + 15, y_pos, SIDEBAR_WIDTH - 45, move_height)
                move_list_rects.append((move_rect, idx))
                
                # Vẽ background cho nước đi được chọn
                if bg_color:
                    pygame.draw.rect(surface, bg_color, move_rect, border_radius=3)
                
                text_rect = move_surf.get_rect(x=SIDEBAR_X + 15, y=y_pos)
                surface.blit(move_surf, text_rect)
                
                surface.set_clip(old_clip)


def handle_sidebar_click(click_pos):
    """Xử lý các click trên sidebar."""
    global undo_button_rect, redo_button_rect, board, current_move_index, is_after_undo, thumb_rect, scrollbar_track_rect, move_list_rects, scroll_dragging
    
    # Xử lý click vào các nút Undo/Redo
    if undo_button_rect and undo_button_rect.collidepoint(click_pos):
        if undo_move():
            return True
    
    if redo_button_rect and redo_button_rect.collidepoint(click_pos):
        if redo_move():
            return True
            
    # Xử lý click vào thanh cuộn
    if scrollbar_track_rect and scrollbar_track_rect.collidepoint(click_pos):
        if thumb_rect and thumb_rect.collidepoint(click_pos):
            # Đã xử lý ở phần event MOUSEBUTTONDOWN
            scroll_dragging = True
            return True
        else:
            # Click vào track (không phải thumb) - cuộn nhanh đến vị trí đó
            track_height = scrollbar_track_rect.height
            relative_y = click_pos[1] - scrollbar_track_rect.y
            global scroll_offset
            scroll_offset = relative_y / track_height
            if scroll_offset < 0: scroll_offset = 0
            if scroll_offset > 1: scroll_offset = 1
            return True
    
    # Xử lý click vào một nước đi cụ thể trong lịch sử
    for move_rect, move_idx in move_list_rects:
        if move_rect.collidepoint(click_pos):
            # Nhảy đến vị trí đã chọn
            jump_to_move(move_idx)
            return True
            
    return False

def jump_to_move(move_idx):
    """Nhảy đến vị trí cụ thể trong lịch sử nước đi."""
    global board, current_move_index, is_after_undo, last_move
    
    if move_idx < 0 or move_idx >= len(move_history):
        return False
        
    # Tạo bàn cờ mới từ đầu
    new_board = chess.Board()
    
    # Áp dụng các nước đi cho đến vị trí được chọn
    for i in range(move_idx + 1):
        new_board.push(move_history[i])
        
    # Cập nhật bàn cờ và chỉ số hiện tại
    board = new_board
    current_move_index = move_idx
    is_after_undo = True
    
    # Cập nhật last_move để highlight nước đi hiện tại
    last_move = move_history[move_idx]
    
    return True

def check_promotion(source_square, target_square):
    """Kiểm tra xem nước đi có phải là phong cấp hay không."""
    global game_state, promotion_source, promotion_target
    
    if source_square is None or target_square is None:
        return False
        
    piece = board.piece_at(source_square)
    if piece and piece.piece_type == chess.PAWN:
        target_rank = chess.square_rank(target_square)
        if (piece.color == chess.WHITE and target_rank == 7) or \
           (piece.color == chess.BLACK and target_rank == 0):
            # Lưu thông tin cho màn hình phong cấp
            promotion_source = source_square
            promotion_target = target_square
            game_state = "PROMOTION"
            return True
    return False

def draw_promotion_screen(surface):
    """Vẽ màn hình chọn phong cấp."""
    global promotion_rects
    promotion_rects = []
    
    # Overlay nửa trong suốt trên toàn màn hình
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Màu đen với độ trong suốt 200/255
    surface.blit(overlay, (0, 0))
    
    # Vẽ hộp chọn phong cấp
    box_width = 400
    box_height = 150
    box_rect = pygame.Rect((WIDTH - box_width) // 2, (HEIGHT - box_height) // 2, box_width, box_height)
    pygame.draw.rect(surface, MENU_BG_COLOR, box_rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, box_rect, 2, border_radius=10)
    
    # Vẽ tiêu đề
    title_text = MENU_FONT.render("Chọn quân cờ phong cấp", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, (HEIGHT - box_height) // 2 + 30))
    surface.blit(title_text, title_rect)
    
    # Vẽ các lựa chọn phong cấp
    piece_size = 60
    piece_margin = 20
    total_width = (piece_size + piece_margin) * 4 - piece_margin
    start_x = (WIDTH - total_width) // 2
    start_y = (HEIGHT - box_height) // 2 + 70
    
    # Xác định màu của quân cờ (theo màu của tốt đang phong cấp)
    color_prefix = "w" if board.turn == chess.WHITE else "b"
    
    pieces = [
        (chess.QUEEN, f"{color_prefix}Q"),
        (chess.ROOK, f"{color_prefix}R"),
        (chess.BISHOP, f"{color_prefix}B"),
        (chess.KNIGHT, f"{color_prefix}N")
    ]
    
    for i, (piece_type, symbol) in enumerate(pieces):
        x = start_x + i * (piece_size + piece_margin)
        
        # Vẽ nền cho từng quân cờ
        piece_rect = pygame.Rect(x, start_y, piece_size, piece_size)
        pygame.draw.rect(surface, LIGHT_SQUARE, piece_rect, border_radius=5)
        
        # Vẽ quân cờ lên nền
        if symbol in piece_images:
            # Căn giữa quân cờ trong ô
            center_x = x + (piece_size - SQUARE_SIZE) // 2
            center_y = start_y + (piece_size - SQUARE_SIZE) // 2
            surface.blit(piece_images[symbol], (center_x, center_y))
            
        # Lưu rect để kiểm tra click
        promotion_rects.append((piece_rect, piece_type))

def highlight_last_move(surface, move, game_current_state):
    """Highlight nước đi vừa thực hiện, chỉ làm khi đang trong trạng thái chơi."""
    # Chỉ highlight khi đang ở trạng thái PLAYING
    if game_current_state != "PLAYING" or move is None:
        return
    
    # Tạo màu cho highlight nước đi cuối cùng (màu xanh lá nhạt với độ trong suốt)
    LAST_MOVE_COLOR = (100, 200, 100, 150)  # Màu xanh lá nhạt, khác với màu highlight thông thường
    
    # Vẽ highlight cho ô nguồn
    if move.from_square is not None:
        file = chess.square_file(move.from_square)
        rank = chess.square_rank(move.from_square)
        screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
        screen_x = file * SQUARE_SIZE
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(LAST_MOVE_COLOR)
        surface.blit(highlight_surface, (screen_x, screen_y))
    
    # Vẽ highlight cho ô đích
    if move.to_square is not None:
        file = chess.square_file(move.to_square)
        rank = chess.square_rank(move.to_square)
        screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
        screen_x = file * SQUARE_SIZE
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(LAST_MOVE_COLOR)
        surface.blit(highlight_surface, (screen_x, screen_y))


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
                            reset_move_history()  # Reset lịch sử nước đi khi bắt đầu trò chơi mới
                            last_move = None
                        elif i == 1:  # Chế độ PVC
                            game_mode = "PVC"
                            game_state = "ENTER_ELO"
                            elo_input = ""  # Reset ELO input
                            is_typing_elo = True
                            reset_move_history()  # Reset lịch sử nước đi khi bắt đầu trò chơi mới
                            last_move = None

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

                # Kiểm tra click trên sidebar trước
                if click_pos[0] >= SIDEBAR_X:
                    if handle_sidebar_click(click_pos):
                        # Reset selection sau khi undo/redo
                        selected_square = source_square = None
                        valid_moves_for_selected_piece = []
                        continue

                # Kiểm tra click nút Back to Menu
                if back_button_game_rect and back_button_game_rect.collidepoint(click_pos):
                    game_state = "MENU"
                    game_mode = None
                    board = chess.Board()
                    selected_square = source_square = None
                    valid_moves_for_selected_piece = []
                    computer_move_pending = False
                    reset_move_history()  # Reset lịch sử nước đi
                    elo_input = 0
                    is_typing_elo = False
                    botWin = 0  # Reset botWin về 0 khi quay lại menu
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
                            
                            # Kiểm tra xem đây có phải nước đi phong cấp không
                            if check_promotion(source_square, target_square):
                                # Nếu là nước phong cấp, chuyển sang màn hình phong cấp
                                # Các nước đi tiếp theo sẽ được xử lý ở trạng thái PROMOTION
                                continue
                                
                            move_to_try = chess.Move(source_square, target_square)

                            # Kiểm tra nước đi hợp lệ
                            if move_to_try in valid_moves_for_selected_piece:
                                board.push(move_to_try)
                                add_move_to_history(move_to_try)  # Thêm nước đi vào lịch sử
                                last_move = move_to_try  # Lưu nước đi cuối cùng
                                is_after_undo = False  # Người chơi đã đi, reset cờ
                                print(f"Player ({'White' if board.turn != chess.WHITE else 'Black'}) moves: {move_to_try.uci()}")
                                selected_square = source_square = None
                                valid_moves_for_selected_piece = []
                                if board.is_game_over():
                                    game_state = "GAME_OVER"
                                    game_over_message = get_game_over_message(board)
                                    print(f"Game Over: {game_over_message}")
                                elif game_mode == "PVC":
                                    computer_move_pending = True
                                    last_computer_move_time = current_time

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
                    reset_move_history()  # Reset lịch sử nước đi khi quay lại menu từ game over
                    elo_input = 0
                    is_typing_elo = False
                    botWin = 0  # Reset botWin về 0 khi quay lại menu
                    last_move = None

        elif game_state == "PROMOTION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Click chuột trái
                click_pos = pygame.mouse.get_pos()
                
                promotion_selected = False
                # Kiểm tra xem người dùng đã click vào quân cờ nào để phong cấp
                for piece_rect, piece_type in promotion_rects:
                    if piece_rect.collidepoint(click_pos):
                        # Tạo nước đi phong cấp với quân cờ được chọn
                        promotion_move = chess.Move(promotion_source, promotion_target, promotion=piece_type)
                        
                        # Thực hiện nước đi
                        if promotion_move in board.legal_moves:
                            board.push(promotion_move)
                            add_move_to_history(promotion_move)
                            print(f"Player promotes to {chess.piece_name(piece_type)}")
                            
                            # Reset các biến và trở về trạng thái chơi
                            selected_square = source_square = None
                            valid_moves_for_selected_piece = []
                            is_after_undo = False
                            game_state = "PLAYING"
                            
                            # Kiểm tra kết thúc game
                            if board.is_game_over():
                                game_state = "GAME_OVER"
                                game_over_message = get_game_over_message(board)
                                print(f"Game Over: {game_over_message}")
                            elif game_mode == "PVC" and board.turn == computer_color:
                                computer_move_pending = True
                                last_computer_move_time = current_time
                            
                            promotion_selected = True
                            break
                
                # Nếu click ngoài các quân cờ phong cấp, hủy bỏ phong cấp
                if not promotion_selected:
                    # Chỉ hủy bỏ selection, không hủy toàn bộ phong cấp
                    if not any(rect.collidepoint(click_pos) for rect, _ in promotion_rects):
                        game_state = "PLAYING"  # Trở lại trạng thái chơi

        # --- Xử lý cuộn thanh bên ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Cuộn lên
                scroll_offset -= 0.1
                if scroll_offset < 0:
                    scroll_offset = 0
            elif event.button == 5:  # Cuộn xuống
                scroll_offset += 0.1
                if scroll_offset > 1:
                    scroll_offset = 1
            elif event.button == 1:  # Nhấn chuột trái để kéo
                if thumb_rect and thumb_rect.collidepoint(mouse_pos):
                    scroll_dragging = True
                    scroll_start_y = mouse_pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Thả chuột trái
                scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if scroll_dragging:
                dy = mouse_pos[1] - scroll_start_y
                scroll_start_y = mouse_pos[1]
                scroll_offset += dy / (SIDEBAR_HEIGHT - 50)  # 50 là chiều cao của thumb
                if scroll_offset < 0:
                    scroll_offset = 0
                elif scroll_offset > 1:
                    scroll_offset = 1

    # --- Cập nhật trạng thái ---
    update_timers()

    # Máy đi cờ (nếu đến lượt và không có pending move)
    if game_mode == "PVC" and board.turn == computer_color and not computer_move_pending and game_state == "PLAYING" and not is_after_undo:
        computer_move_pending = True
        last_computer_move_time = current_time

    if computer_move_pending and (current_time - last_computer_move_time > 500):  # Delay 0.5s
        computer_move = make_random_computer_move(board)
        if computer_move:
            board.push(computer_move)
            add_move_to_history(computer_move)  # Thêm nước đi vào lịch sử
            last_move = computer_move  # Cập nhật last_move khi máy tính đi
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
        last_move = None  # Đảm bảo xóa highlight khi quay về menu
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
        # Vẽ highlight cho nước đi cuối cùng trước khi vẽ highlight cho ô được chọn
        highlight_last_move(screen, last_move, game_state)
        if selected_square is not None:
            highlight_square(board_surface, selected_square)
            highlight_valid_moves(board_surface, valid_moves_for_selected_piece)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = None

        # Vẽ đồng hồ
        draw_timer(screen, black_timer, is_top=True)
        draw_timer(screen, white_timer, is_top=False)

        draw_move_history_sidebar(screen)
        # Vẽ sidebar lịch sử nước đi

    elif game_state == "GAME_OVER":
        board_surface = screen.subsurface(pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = draw_game_over(screen, game_over_message)

    elif game_state == "PROMOTION":
        board_surface = screen.subsurface(pygame.Rect(0, 0, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        if selected_square is not None:
            highlight_square(board_surface, selected_square)
            highlight_valid_moves(board_surface, valid_moves_for_selected_piece)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        
        # Vẽ màn hình phong cấp trên toàn màn hình
        draw_promotion_screen(screen)

    # --- Highlight nước đi cuối cùng ---
    highlight_last_move(screen, last_move, game_state)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()