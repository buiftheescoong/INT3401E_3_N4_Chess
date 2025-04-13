# -*- coding: utf-8 -*-
import pygame
import chess
import sys
import random
import time

# --- Cài đặt cơ bản ---
pygame.init()

# Kích thước màn hình và bàn cờ
WIDTH, HEIGHT = 900, 750 # Chiều cao lớn hơn để chứa menu/thông báo
BOARD_SIZE = 640 # Kích thước bàn cờ (nên chia hết cho 8)
SQUARE_SIZE = BOARD_SIZE // 8
MENU_HEIGHT = HEIGHT - BOARD_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_SQUARE = (238, 238, 210) # Màu ô sáng
DARK_SQUARE = (118, 150, 86)   # Màu ô tối
HIGHLIGHT_COLOR = (255, 255, 0, 100) # Màu vàng trong suốt để highlight
MENU_BG_COLOR = (40, 40, 40)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)

# Font chữ (Thử dùng font hệ thống, nếu lỗi sẽ dùng font mặc định)
try:
    MENU_FONT = pygame.font.SysFont("consolas", 30)
    MSG_FONT = pygame.font.SysFont("consolas", 20)
except pygame.error:
    print("Font 'consolas' không tìm thấy, sử dụng font mặc định.")
    MENU_FONT = pygame.font.Font(None, 40) # Font mặc định kích thước 40
    MSG_FONT = pygame.font.Font(None, 30)  # Font mặc định kích thước 30

# Tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Pygame Chess (Full)")

# Clock để kiểm soát FPS
clock = pygame.time.Clock()
FPS = 30

# --- Trạng thái trò chơi ---
game_state = "MENU" # MENU, PLAYING, GAME_OVER
game_mode = None    # PVP, PVC, CVC
board = chess.Board() # Bàn cờ logic

# --- Biến toàn cục ---
piece_images = {}   # Lưu trữ ảnh quân cờ đã tải và resize
selected_square = None # Ô đang được chọn (dạng chess.Square index)
source_square = None   # Ô gốc của quân cờ được chọn
valid_moves_for_selected_piece = [] # Danh sách các đối tượng chess.Move hợp lệ

# Biến cho giao diện
menu_buttons = []   # Lưu trữ Rect của các nút menu
back_button_game_rect = None # Rect của nút Back khi đang chơi
back_button_over_rect = None # Rect của nút Back khi game over
game_over_message = "" # Thông báo khi kết thúc game

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
            pygame.quit(); sys.exit()
        except FileNotFoundError:
             print(f"Lỗi: Không tìm thấy file {img_path}")
             print("Hãy đảm bảo thư mục 'img' tồn tại cùng cấp với file code")
             print("và chứa đủ 12 file ảnh quân cờ được đặt tên đúng (vd: wP.png, bN.png,...).")
             pygame.quit(); sys.exit()

# --- Hàm vẽ ---
def draw_board(surface):
    """Vẽ các ô vuông sáng tối của bàn cờ."""
    for rank in range(8):
        for file in range(8):
            is_light_square = (rank + file) % 2 == 0
            color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
            rect = pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)

def get_piece_symbol(piece):
    """Lấy ký hiệu để tìm ảnh (vd: 'wP', 'bN')."""
    if piece is None: return None
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
                    screen_y = rank * SQUARE_SIZE
                    surface.blit(piece_images[piece_symbol], (screen_x, screen_y))

def highlight_square(surface, square_index):
    """Highlight ô cờ được chọn."""
    if square_index is not None:
        file = chess.square_file(square_index)
        rank = chess.square_rank(square_index)
        screen_y = (7 - rank) * SQUARE_SIZE
        screen_x = file * SQUARE_SIZE
        highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        surface.blit(highlight_surface, (screen_x, screen_y))

def highlight_valid_moves(surface, moves):
    """Vẽ các chấm tròn nhỏ để chỉ các nước đi hợp lệ."""
    for move in moves:
        target_square = move.to_square
        file = chess.square_file(target_square)
        rank = chess.square_rank(target_square)
        screen_y = (7 - rank) * SQUARE_SIZE
        screen_x = file * SQUARE_SIZE
        center_x = screen_x + SQUARE_SIZE // 2
        center_y = screen_y + SQUARE_SIZE // 2
        pygame.draw.circle(surface, GRAY, (center_x, center_y), SQUARE_SIZE // 6)

def draw_menu(surface):
    """Vẽ menu chính và trả về Rect của các nút."""
    surface.fill(MENU_BG_COLOR)
    title_text = MENU_FONT.render("Simple Pygame Chess", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    surface.blit(title_text, title_rect)

    button_texts = ["Player vs Player", "Player vs Computer", "Computer vs Computer"]
    button_rects = []
    button_height = 60
    button_width = 350
    total_button_height = len(button_texts) * button_height + (len(button_texts) - 1) * 20
    start_y = (HEIGHT - total_button_height) // 2 + 50
    mouse_pos = pygame.mouse.get_pos()

    for i, text in enumerate(button_texts):
        rect = pygame.Rect((WIDTH - button_width) // 2, start_y + i * (button_height + 20), button_width, button_height)
        button_rects.append(rect)
        is_hovering = rect.collidepoint(mouse_pos)
        button_color = BUTTON_HOVER_COLOR if is_hovering else BUTTON_COLOR
        pygame.draw.rect(surface, button_color, rect, border_radius=10)
        btn_text_surf = MENU_FONT.render(text, True, TEXT_COLOR)
        btn_text_rect = btn_text_surf.get_rect(center=rect.center)
        surface.blit(btn_text_surf, btn_text_rect)

    return button_rects

def draw_game_info(surface, current_board, current_game_mode):
    """Vẽ khu vực thông tin dưới bàn cờ và trả về Rect nút Back."""
    global game_state # Cần global để có thể thay đổi trạng thái nếu hết cờ ở đây (dù nên tránh)

    info_area_rect = pygame.Rect(0, BOARD_SIZE, WIDTH, MENU_HEIGHT)
    pygame.draw.rect(surface, MENU_BG_COLOR, info_area_rect)

    # Lượt đi
    turn_text = "White's Turn" if current_board.turn == chess.WHITE else "Black's Turn"
    turn_surf = MSG_FONT.render(turn_text, True, TEXT_COLOR)
    turn_rect = turn_surf.get_rect(midleft=(20, BOARD_SIZE + MENU_HEIGHT * 0.25))
    surface.blit(turn_surf, turn_rect)

    # Chế độ chơi
    mode_text = f"Mode: {current_game_mode}"
    mode_surf = MSG_FONT.render(mode_text, True, TEXT_COLOR)
    mode_rect = mode_surf.get_rect(midright=(WIDTH - 20, BOARD_SIZE + MENU_HEIGHT * 0.25))
    surface.blit(mode_surf, mode_rect)

    # Trạng thái game (Check, Checkmate, Stalemate, ...)
    status_text = ""
    is_game_currently_over = False # Chỉ kiểm tra, không thay đổi game_state ở đây

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
        status_color = (255, 100, 100) if is_game_currently_over else (255, 200, 0) # Đỏ nếu hết, Vàng nếu Chiếu
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

    return back_rect # Trả về Rect của nút để xử lý click

