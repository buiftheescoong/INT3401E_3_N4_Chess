# -*- coding: utf-8 -*-
import pygame
import chess
import sys
from Elo_Calculation import Elo_Cal
import random
import time
try:
    from engine.ComputeMove import get_best_move  # Import engine for CvC mode
except ImportError:
    print("Warning: get_best_move not found. Using random moves for CvC mode.")
    get_best_move = None  # Fallback to random moves if engine is unavailable

# --- Cài đặt cơ bản ---
pygame.init()

# Kích thước màn hình và bàn cờ
TOP_MARGIN = 50
WIDTH, HEIGHT = 900, 800
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 9
MENU_HEIGHT = HEIGHT - BOARD_SIZE
SIDEBAR_WIDTH = 250
SIDEBAR_X = WIDTH - SIDEBAR_WIDTH
SIDEBAR_HEIGHT = BOARD_SIZE

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
HIGHLIGHT_COLOR = (255, 255, 0, 100)
MENU_BG_COLOR = (40, 40, 40)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)
LAST_MOVE_HIGHLIGHT_COLOR = (173, 216, 230, 150)  # Added for consistency with UICvC

# Font chữ
bot_rating = 1200  # Elo của bot trong PVC
bot_a_rating_cvc = 1200  # Elo của Bot A trong CvC
bot_b_rating_cvc = 1200  # Elo của Bot B trong CvC
bot_win = 0  # 1: Bot thắng, -1: Bot thua, 0: Hòa/Đang chơi (PVC)
bot_win_cvc = 0  # 1: Bot A thắng, -1: Bot B thắng, 0: Hòa/Đang chơi (CvC)

try:
    MENU_FONT = pygame.font.SysFont("consolas", 30)
    MSG_FONT = pygame.font.SysFont("consolas", 20)
    HISTORY_FONT = pygame.font.SysFont("consolas", 16)  # Added for move history
except pygame.error:
    print("Font 'consolas' không tìm thấy, sử dụng font mặc định.")
    MENU_FONT = pygame.font.Font(None, 40)
    MSG_FONT = pygame.font.Font(None, 30)
    HISTORY_FONT = pygame.font.Font(None, 22)

# Tạo màn hình
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Pygame Chess")
clock = pygame.time.Clock()

# Tải background image
try:
    MENU_BACKGROUND = pygame.image.load("img/menu_background.png").convert()
except pygame.error as e:
    print(f"Không thể tải background image: {e}")
    MENU_BACKGROUND = None
FPS = 30

# --- Trạng thái trò chơi ---
game_state = "MENU"  # MENU, ENTER_ELO, PLAYING, GAME_OVER, PROMOTION
game_mode = None  # PVP, PVC, CVC
board = chess.Board()

# --- Biến cho promotion ---
promotion_move = None
promotion_source = None
promotion_target = None
promotion_options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
promotion_rects = []

# --- Biến toàn cục ---
piece_images = {}
selected_square = None
source_square = None
valid_moves_for_selected_piece = []
last_move = None

# --- Biến lịch sử nước đi ---
move_history = []
current_move_index = -1
undo_button_rect = None
redo_button_rect = None
is_after_undo = False

# --- Biến cho thanh cuộn ---
scroll_dragging = False
thumb_rect = None
scroll_start_y = 0
scroll_offset = 0
scrollbar_track_rect = None
move_list_rects = []

# Biến cho giao diện
menu_buttons = []
back_button_game_rect = None
back_button_over_rect = None
game_over_message = ""

# --- ELO input ---
elo_input = ""  # Changed to string to handle input properly
is_typing_elo = False

# --- Computer move (PVC) ---
computer_move_pending = False
last_computer_move_time = 0
computer_color = chess.BLACK

# --- CvC-specific variables ---
cvc_bot_a_color = chess.WHITE
cvc_bot_b_color = chess.BLACK
cvc_move_pending = False
cvc_last_move_time = 0
CVC_MOVE_DELAY = 1000  # ms, delay between bot moves in CvC

# --- Đồng hồ ---
WHITE_TIME = 15 * 60 * 1000
BLACK_TIME = 15 * 60 * 1000
white_timer = WHITE_TIME
black_timer = BLACK_TIME
last_timer_update = pygame.time.get_ticks()

# --- Tải Elo của bot ---
def load_bot_elos():
    global bot_rating, bot_a_rating_cvc, bot_b_rating_cvc
    try:
        with open('bot_elo.txt', 'r') as file:
            bot_rating = round(float(file.read().strip()))
    except (FileNotFoundError, ValueError):
        bot_rating = 1200
        with open('bot_elo.txt', 'w') as file:
            file.write(str(bot_rating))
    print(f"PVC Bot Elo loaded/set: {bot_rating}")

    try:
        with open('bot_a_elo.txt', 'r') as file:
            bot_a_rating_cvc = round(float(file.read().strip()))
    except (FileNotFoundError, ValueError):
        bot_a_rating_cvc = 1200
        with open('bot_a_elo.txt', 'w') as file:
            file.write(str(bot_a_rating_cvc))
    print(f"CvC Bot A Elo loaded/set: {bot_a_rating_cvc}")

    try:
        with open('bot_b_elo.txt', 'r') as file:
            bot_b_rating_cvc = round(float(file.read().strip()))
    except (FileNotFoundError, ValueError):
        bot_b_rating_cvc = 1200
        with open('bot_b_elo.txt', 'w') as file:
            file.write(str(bot_b_rating_cvc))
    print(f"CvC Bot B Elo loaded/set: {bot_b_rating_cvc}")

# --- Tải tài nguyên ---
def load_piece_images():
    pieces = ['wP', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bP', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        try:
            img_path = f"img/{piece}.png"
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.smoothscale(img, (SQUARE_SIZE, SQUARE_SIZE))
            piece_images[piece] = img
        except pygame.error as e:
            print(f"Lỗi tải ảnh {img_path}: {e}")
            pygame.quit()
            sys.exit()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {img_path}")
            pygame.quit()
            sys.exit()

# --- Hàm vẽ bàn cờ ---
def draw_board(surface):
    for rank in range(8):
        for file in range(8):
            is_light_square = (rank + file) % 2 == 0
            color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
            rect = pygame.Rect(file * SQUARE_SIZE, rank * SQUARE_SIZE + TOP_MARGIN, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(surface, color, rect)

def get_piece_symbol(piece):
    if piece is None:
        return None
    color_prefix = 'w' if piece.color == chess.WHITE else 'b'
    piece_suffix = piece.symbol().upper()
    return f"{color_prefix}{piece_suffix}"

def draw_pieces(surface, current_board):
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
    if MENU_BACKGROUND:
        surface.blit(MENU_BACKGROUND, (0, 0))
    else:
        surface.fill(MENU_BG_COLOR)

    button_texts = ["PVP", "PVC", "CVC"]  # Added CVC option
    button_rects = []
    button_width = 200
    button_height = 50
    button_y_start = HEIGHT // 2 - 60

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

    return button_rects

def draw_game_info(surface, current_board, current_game_mode):
    global game_state, game_mode, board, selected_square, source_square, valid_moves_for_selected_piece, computer_move_pending, cvc_move_pending

    info_area_rect = pygame.Rect(0, BOARD_SIZE + TOP_MARGIN, WIDTH, MENU_HEIGHT)
    pygame.draw.rect(surface, MENU_BG_COLOR, info_area_rect)

    turn_text = "White's Turn" if current_board.turn == chess.WHITE else "Black's Turn"
    turn_surf = MSG_FONT.render(turn_text, True, TEXT_COLOR)
    turn_rect = turn_surf.get_rect(midleft=(20, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.25))
    surface.blit(turn_surf, turn_rect)

    mode_text = f"Mode: {current_game_mode}"
    mode_surf = MSG_FONT.render(mode_text, True, TEXT_COLOR)
    mode_rect = mode_surf.get_rect(midright=(WIDTH - 20, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.25))
    surface.blit(mode_surf, mode_rect)

    status_text = ""
    is_game_currently_over = False

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
        status_color = (255, 100, 100) if is_game_currently_over else (255, 200, 0)
        status_surf = MSG_FONT.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(midleft=(20, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.75))
        surface.blit(status_surf, status_rect)

    if current_game_mode == "PVC":
        elo_text = f"Player's Elo: {elo_input}                                        Computer's Elo: {bot_rating}"
        elo_surf = MSG_FONT.render(elo_text, True, TEXT_COLOR)
        elo_rect = elo_surf.get_rect(midleft=(20, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.5))
        surface.blit(elo_surf, elo_rect)
    elif current_game_mode == "CVC":
        elo_text = f"Bot A (W) Elo: {bot_a_rating_cvc}                                        Bot B (B) Elo: {bot_b_rating_cvc}"
        elo_surf = MSG_FONT.render(elo_text, True, TEXT_COLOR)
        elo_rect = elo_surf.get_rect(midleft=(20, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.5))
        surface.blit(elo_surf, elo_rect)

    back_rect = pygame.Rect(WIDTH - 160, BOARD_SIZE + TOP_MARGIN + MENU_HEIGHT * 0.6, 140, 40)
    mouse_pos = pygame.mouse.get_pos()
    hover = back_rect.collidepoint(mouse_pos)
    btn_color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(surface, btn_color, back_rect, border_radius=5)
    back_text_surf = MSG_FONT.render("Back to Menu", True, TEXT_COLOR)
    back_text_rect = back_text_surf.get_rect(center=back_rect.center)
    surface.blit(back_text_surf, back_text_rect)

    return back_rect

def get_game_over_message(current_board):
    global bot_win, bot_win_cvc, game_mode, computer_color, cvc_bot_a_color, cvc_bot_b_color
    
    if current_board.is_checkmate():
        winner = "Black" if current_board.turn == chess.WHITE else "White"
        if game_mode == "PVC":
            if (winner == "Black" and computer_color == chess.BLACK) or (winner == "White" and computer_color == chess.WHITE):
                bot_win = 1
                print("Bot wins! bot_win =", bot_win)
            else:
                bot_win = -1
                print("Player wins! bot_win =", bot_win)
        elif game_mode == "CVC":
            bot_win_cvc = 1 if winner == "White" else -1  # Bot A (White) wins: 1, Bot B (Black) wins: -1
            print(f"CvC: {'Bot A' if bot_win_cvc == 1 else 'Bot B'} wins! bot_win_cvc =", bot_win_cvc)
        return f"Checkmate! {winner} Wins."
    elif current_board.is_stalemate():
        if game_mode == "CVC":
            bot_win_cvc = 0
            print("CvC Draw game! bot_win_cvc =", bot_win_cvc)
        print("Draw game! bot_win =", bot_win)
        return "Stalemate! It's a Draw."
    elif current_board.is_insufficient_material():
        if game_mode == "CVC":
            bot_win_cvc = 0
            print("CvC Draw game! bot_win_cvc =", bot_win_cvc)
        print("Draw game! bot_win =", bot_win)
        return "Draw: Insufficient Material."
    elif current_board.is_seventyfive_moves():
        if game_mode == "CVC":
            bot_win_cvc = 0
            print("CvC Draw game! bot_win_cvc =", bot_win_cvc)
        print("Draw game! bot_win =", bot_win)
        return "Draw: 75-move rule."
    elif current_board.is_fivefold_repetition():
        if game_mode == "CVC":
            bot_win_cvc = 0
            print("CvC Draw game! bot_win_cvc =", bot_win_cvc)
        print("Draw game! bot_win =", bot_win)
        return "Draw: Fivefold Repetition."
    else:
        return "Game Over!"

def calculate_and_save_elos_cvc():
    global bot_a_rating_cvc, bot_b_rating_cvc, bot_win_cvc
    if bot_win_cvc != 0:
        new_a_elo = Elo_Cal(bot_a_rating_cvc, bot_b_rating_cvc, bot_win_cvc)
        new_b_elo = Elo_Cal(bot_b_rating_cvc, bot_a_rating_cvc, -bot_win_cvc)
        print(f"CvC Elo: Bot A old={bot_a_rating_cvc}, new={round(new_a_elo,2)}")
        print(f"CvC Elo: Bot B old={bot_b_rating_cvc}, new={round(new_b_elo,2)}")
        bot_a_rating_cvc = round(new_a_elo)
        bot_b_rating_cvc = round(new_b_elo)
        with open('bot_a_elo.txt', 'w') as file:
            file.write(str(bot_a_rating_cvc))
        with open('bot_b_elo.txt', 'w') as file:
            file.write(str(bot_b_rating_cvc))

def get_game_elo(current_board):
    global bot_rating, bot_win
    if game_mode == "PVC" and current_board.is_checkmate():
        if current_board.turn == chess.WHITE:
            return Elo_Cal(bot_rating, int(elo_input) if elo_input.isdigit() else 1200, 0)
        else:
            return Elo_Cal(bot_rating, int(elo_input) if elo_input.isdigit() else 1200, 1)
    return bot_rating

def draw_game_over(surface, message):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    end_text_surf = MENU_FONT.render(message, True, WHITE)
    end_text_rect = end_text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    surface.blit(end_text_surf, end_text_rect)

    if game_mode == "CVC":
        elo_info_str = f"New Elo: Bot A: {bot_a_rating_cvc}, Bot B: {bot_b_rating_cvc}"
        elo_info_surf = MSG_FONT.render(elo_info_str, True, WHITE)
        elo_info_rect = elo_info_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        surface.blit(elo_info_surf, elo_info_rect)

    back_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
    mouse_pos = pygame.mouse.get_pos()
    hover = back_rect.collidepoint(mouse_pos)
    btn_color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
    pygame.draw.rect(surface, btn_color, back_rect, border_radius=5)
    back_text_surf = MSG_FONT.render("Back to Menu", True, TEXT_COLOR)
    back_text_rect = back_text_surf.get_rect(center=back_rect.center)
    surface.blit(back_text_surf, back_text_rect)
    return back_rect

def get_square_from_mouse(pos):
    x, y = pos
    if x < 0 or x >= BOARD_SIZE or y < TOP_MARGIN or y >= BOARD_SIZE + TOP_MARGIN:
        return None
    file = x // SQUARE_SIZE
    rank = 8 - ((y - TOP_MARGIN) // SQUARE_SIZE)
    return chess.square(file, rank)

def make_random_computer_move(current_board):
    time.sleep(1)
    legal_moves = list(current_board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        return move
    return False

def make_engine_move(current_board):
    if get_best_move:
        move, _ = get_best_move(current_board.copy(), time_limit=1)
        if move and current_board.is_legal(move):
            return move
        print("Engine returned invalid or no move.")
    return make_random_computer_move(current_board)  # Fallback to random move

def draw_timer(surface, time_left, is_top):
    minutes = time_left // 60000
    seconds = (time_left % 60000) // 1000
    timer_text = f"{minutes:02}:{seconds:02}"
    timer_surf = MENU_FONT.render(timer_text, True, TEXT_COLOR)
    timer_rect = timer_surf.get_rect(center=(WIDTH // 2, 30 if is_top else HEIGHT - 30))
    surface.blit(timer_surf, timer_rect)

def update_timers():
    global white_timer, black_timer, last_timer_update, game_state, game_over_message, bot_win, bot_win_cvc
    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - last_timer_update
    last_timer_update = current_time

    if game_state == "PLAYING":
        if board.turn == chess.WHITE:
            white_timer -= elapsed_time
            if white_timer <= 0:
                white_timer = 0
                game_state = "GAME_OVER"
                game_over_message = "Black wins! White ran out of time."
                if game_mode == "PVC":
                    bot_win = 1 if computer_color == chess.BLACK else -1
                    print("Black wins! White ran out of time.")
                elif game_mode == "CVC":
                    bot_win_cvc = -1  # Bot B (Black) wins
                    print("Black wins! White ran out of time.")
        else:
            black_timer -= elapsed_time
            if black_timer <= 0:
                black_timer = 0
                game_state = "GAME_OVER"
                game_over_message = "White wins! Black ran out of time."
                if game_mode == "PVC":
                    bot_win = 1 if computer_color == chess.WHITE else -1
                    print("White wins! Black ran out of time.")
                elif game_mode == "CVC":
                    bot_win_cvc = 1  # Bot A (White) wins
                    print("White wins! Black ran out of time.")
        if game_state == "GAME_OVER" and game_mode == "CVC":
            calculate_and_save_elos_cvc()

def add_move_to_history(move):
    global move_history, current_move_index
    if current_move_index < len(move_history) - 1:
        move_history = move_history[:current_move_index + 1]
    move_history.append(move)
    current_move_index = len(move_history) - 1
    print(f"Thêm nước đi vào lịch sử: {move.uci()}, index: {current_move_index}")

def undo_move():
    global board, current_move_index, is_after_undo, last_move
    if current_move_index >= 0:
        board.pop()
        current_move_index -= 1
        is_after_undo = True
        if current_move_index >= 0:
            last_move = move_history[current_move_index]
        else:
            last_move = None
        print(f"Hoàn tác nước đi, hiện tại ở vị trí {current_move_index + 1}")
        return True
    return False

def redo_move():
    global board, current_move_index, move_history, is_after_undo, last_move
    if current_move_index < len(move_history) - 1:
        next_move = move_history[current_move_index + 1]
        board.push(next_move)
        current_move_index += 1
        is_after_undo = True
        last_move = next_move
        print(f"Làm lại nước đi, hiện tại ở vị trí {current_move_index + 1}")
        return True
    return False

def reset_move_history():
    global move_history, current_move_index, last_move
    move_history = []
    current_move_index = -1
    last_move = None
    print("Đặt lại lịch sử nước đi")

def draw_move_history_sidebar(surface):
    global undo_button_rect, redo_button_rect, thumb_rect, scrollbar_track_rect, move_list_rects
    move_list_rects = []
    sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
    pygame.draw.rect(surface, MENU_BG_COLOR, sidebar_rect)
    pygame.draw.line(surface, WHITE, (SIDEBAR_X, 0), (SIDEBAR_X, SIDEBAR_HEIGHT), 2)
    title_surf = MSG_FONT.render("Lịch sử nước đi", True, TEXT_COLOR)
    title_rect = title_surf.get_rect(center=(SIDEBAR_X + SIDEBAR_WIDTH // 2, 30))
    surface.blit(title_surf, title_rect)
    button_width = SIDEBAR_WIDTH - 20
    button_height = 40
    button_margin = 10
    undo_button_rect = pygame.Rect(SIDEBAR_X + 10, 60, button_width, button_height)
    undo_color = BUTTON_COLOR if current_move_index >= 0 else (50, 50, 50)
    pygame.draw.rect(surface, undo_color, undo_button_rect, border_radius=5)
    undo_text = MSG_FONT.render("Undo", True, TEXT_COLOR)
    undo_text_rect = undo_text.get_rect(center=undo_button_rect.center)
    surface.blit(undo_text, undo_text_rect)
    redo_button_rect = pygame.Rect(SIDEBAR_X + 10, 60 + button_height + button_margin, button_width, button_height)
    redo_color = BUTTON_COLOR if current_move_index < len(move_history) - 1 else (50, 50, 50)
    pygame.draw.rect(surface, redo_color, redo_button_rect, border_radius=5)
    redo_text = MSG_FONT.render("Redo", True, TEXT_COLOR)
    redo_text_rect = redo_text.get_rect(center=redo_button_rect.center)
    surface.blit(redo_text, redo_text_rect)
    move_list_start_y = 60 + (button_height + button_margin) * 2 + 20
    move_height = 25
    list_view_height = SIDEBAR_HEIGHT - move_list_start_y - 20
    max_visible_moves = list_view_height // move_height
    list_view_rect = pygame.Rect(SIDEBAR_X + 10, move_list_start_y, SIDEBAR_WIDTH - 30, list_view_height)
    pygame.draw.rect(surface, (30, 30, 30), list_view_rect, border_radius=5)
    scrollbar_width = 10
    scrollbar_track_rect = pygame.Rect(SIDEBAR_X + SIDEBAR_WIDTH - 20, move_list_start_y, scrollbar_width, list_view_height)
    pygame.draw.rect(surface, (70, 70, 70), scrollbar_track_rect, border_radius=5)
    if move_history:
        total_moves = len(move_history)
        if total_moves <= max_visible_moves:
            start_idx = 0
            scroll_ratio = 0
            thumb_height = list_view_height
        else:
            if current_move_index >= 0:
                scroll_ratio = min(1, max(0, current_move_index / (total_moves - 1)))
            else:
                scroll_ratio = scroll_offset
            middle_offset = max_visible_moves // 2
            if current_move_index < middle_offset:
                start_idx = 0
            elif current_move_index >= total_moves - middle_offset:
                start_idx = max(0, total_moves - max_visible_moves)
            else:
                start_idx = max(0, current_move_index - middle_offset)
            if scroll_dragging:
                start_idx = int(scroll_ratio * (total_moves - max_visible_moves))
                start_idx = max(0, min(start_idx, total_moves - max_visible_moves))
            thumb_height = max(50, list_view_height * max_visible_moves / total_moves)
        thumb_y = move_list_start_y + (list_view_height - thumb_height) * scroll_ratio
        thumb_rect = pygame.Rect(SIDEBAR_X + SIDEBAR_WIDTH - 20, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(surface, BUTTON_COLOR, thumb_rect, border_radius=5)
        end_idx = min(start_idx + max_visible_moves, total_moves)
        for i, move in enumerate(move_history[start_idx:end_idx]):
            idx = start_idx + i
            if idx % 2 == 0:
                move_number = (idx // 2) + 1
                move_text = f"{move_number}. {board.san(move) if board.is_legal(move) else move.uci()}"
            else:
                move_number = (idx // 2) + 1
                move_text = f"{move_number}... {board.san(move) if board.is_legal(move) else move.uci()}"
            text_color = (255, 255, 0) if idx == current_move_index else TEXT_COLOR
            bg_color = (50, 50, 50) if idx == current_move_index else None
            move_surf = MSG_FONT.render(move_text, True, text_color)
            y_pos = move_list_start_y + 5 + i * move_height
            if move_list_start_y <= y_pos < move_list_start_y + list_view_height - move_height:
                clip_rect = pygame.Rect(SIDEBAR_X + 15, move_list_start_y, SIDEBAR_WIDTH - 35, list_view_height)
                old_clip = surface.get_clip()
                surface.set_clip(clip_rect)
                move_rect = pygame.Rect(SIDEBAR_X + 15, y_pos, SIDEBAR_WIDTH - 45, move_height)
                move_list_rects.append((move_rect, idx))
                if bg_color:
                    pygame.draw.rect(surface, bg_color, move_rect, border_radius=3)
                text_rect = move_surf.get_rect(x=SIDEBAR_X + 15, y=y_pos)
                surface.blit(move_surf, text_rect)
                surface.set_clip(old_clip)

def handle_sidebar_click(click_pos):
    global undo_button_rect, redo_button_rect, board, current_move_index, is_after_undo, thumb_rect, scrollbar_track_rect, move_list_rects, scroll_dragging
    if undo_button_rect and undo_button_rect.collidepoint(click_pos):
        if undo_move():
            return True
    if redo_button_rect and redo_button_rect.collidepoint(click_pos):
        if redo_move():
            return True
    if scrollbar_track_rect and scrollbar_track_rect.collidepoint(click_pos):
        if thumb_rect and thumb_rect.collidepoint(click_pos):
            scroll_dragging = True
            return True
        else:
            track_height = scrollbar_track_rect.height
            relative_y = click_pos[1] - scrollbar_track_rect.y
            global scroll_offset
            scroll_offset = relative_y / track_height
            if scroll_offset < 0: scroll_offset = 0
            if scroll_offset > 1: scroll_offset = 1
            return True
    for move_rect, move_idx in move_list_rects:
        if move_rect.collidepoint(click_pos):
            jump_to_move(move_idx)
            return True
    return False

def jump_to_move(move_idx):
    global board, current_move_index, is_after_undo, last_move
    if move_idx < 0 or move_idx >= len(move_history):
        return False
    new_board = chess.Board()
    for i in range(move_idx + 1):
        new_board.push(move_history[i])
    board = new_board
    current_move_index = move_idx
    is_after_undo = True
    last_move = move_history[move_idx]
    return True

def check_promotion(source_square, target_square):
    global game_state, promotion_source, promotion_target
    if source_square is None or target_square is None:
        return False
    piece = board.piece_at(source_square)
    if piece and piece.piece_type == chess.PAWN:
        target_rank = chess.square_rank(target_square)
        if (piece.color == chess.WHITE and target_rank == 7) or \
           (piece.color == chess.BLACK and target_rank == 0):
            promotion_source = source_square
            promotion_target = target_square
            game_state = "PROMOTION"
            return True
    return False

def draw_promotion_screen(surface):
    global promotion_rects
    promotion_rects = []
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    box_width = 400
    box_height = 150
    box_rect = pygame.Rect((WIDTH - box_width) // 2, (HEIGHT - box_height) // 2, box_width, box_height)
    pygame.draw.rect(surface, MENU_BG_COLOR, box_rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, box_rect, 2, border_radius=10)
    title_text = MENU_FONT.render("Chọn quân cờ phong cấp", True, TEXT_COLOR)
    title_rect = title_text.get_rect(center=(WIDTH // 2, (HEIGHT - box_height) // 2 + 30))
    surface.blit(title_text, title_rect)
    piece_size = 60
    piece_margin = 20
    total_width = (piece_size + piece_margin) * 4 - piece_margin
    start_x = (WIDTH - total_width) // 2
    start_y = (HEIGHT - box_height) // 2 + 70
    color_prefix = "w" if board.turn == chess.WHITE else "b"
    pieces = [
        (chess.QUEEN, f"{color_prefix}Q"),
        (chess.ROOK, f"{color_prefix}R"),
        (chess.BISHOP, f"{color_prefix}B"),
        (chess.KNIGHT, f"{color_prefix}N")
    ]
    for i, (piece_type, symbol) in enumerate(pieces):
        x = start_x + i * (piece_size + piece_margin)
        piece_rect = pygame.Rect(x, start_y, piece_size, piece_size)
        pygame.draw.rect(surface, LIGHT_SQUARE, piece_rect, border_radius=5)
        if symbol in piece_images:
            center_x = x + (piece_size - SQUARE_SIZE) // 2
            center_y = start_y + (piece_size - SQUARE_SIZE) // 2
            surface.blit(piece_images[symbol], (center_x, center_y))
        promotion_rects.append((piece_rect, piece_type))

# def highlight_last_move(surface, move, game_current_state):
#     if game_current_state != "PLAYING" or move is None:
#         return
#     highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
#     highlight_surface.fill(LAST_MOVE_HIGHLIGHT_COLOR)
#     if move.from_square is not None:
#         file = chess.square_file(move.from_square)
#         rank = chess.square_rank(move.from_square)
#         screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
#         screen_x = file * SQUARE_SIZE
#         surface.blit(highlight_surface, (screen_x, screen_y))
#     if move.to_square is not None:
#         file = chess.square_file(move.to_square)
#         rank = chess.square_rank(move.to_square)
#         screen_y = (7 - rank) * SQUARE_SIZE + TOP_MARGIN
#         screen_x = file * SQUARE_SIZE
#         surface.blit(highlight_surface, (screen_x, screen_y))

# --- Vòng lặp chính ---
load_piece_images()
load_bot_elos()
running = True
while running:
    current_time = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = pygame.mouse.get_pos()
                for i, button_rect in enumerate(menu_buttons):
                    if button_rect.collidepoint(click_pos):
                        board = chess.Board()
                        selected_square = source_square = None
                        valid_moves_for_selected_piece = []
                        game_over_message = ""
                        white_timer = WHITE_TIME
                        black_timer = BLACK_TIME
                        last_timer_update = pygame.time.get_ticks()
                        elo_input = ""
                        is_typing_elo = False
                        bot_win = 0
                        bot_win_cvc = 0
                        if i == 0:  # PVP
                            game_mode = "PVP"
                            game_state = "PLAYING"
                            reset_move_history()
                            last_move = None
                        elif i == 1:  # PVC
                            game_mode = "PVC"
                            game_state = "ENTER_ELO"
                            elo_input = ""
                            is_typing_elo = True
                            reset_move_history()
                            last_move = None
                        elif i == 2:  # CVC
                            game_mode = "CVC"
                            game_state = "PLAYING"
                            cvc_move_pending = False
                            cvc_last_move_time = 0
                            reset_move_history()
                            last_move = None
                            print("Starting Computer vs Computer Game")
                        print(f"Chế độ đã chọn: {game_mode}")
                        break

        elif game_state == "ENTER_ELO":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if elo_input.isdigit():
                        print(f"Player ELO: {elo_input}")
                        game_state = "PLAYING"
                        computer_color = chess.BLACK
                        last_timer_update = pygame.time.get_ticks()
                    else:
                        print("Invalid ELO. Please enter a number.")
                elif event.key == pygame.K_BACKSPACE:
                    elo_input = elo_input[:-1]
                else:
                    if event.unicode.isdigit():
                        elo_input += event.unicode

        elif game_state == "PLAYING":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = pygame.mouse.get_pos()
                if click_pos[0] >= SIDEBAR_X and game_mode != "CVC":  # Disable sidebar interaction in CvC
                    if handle_sidebar_click(click_pos):
                        selected_square = source_square = None
                        valid_moves_for_selected_piece = []
                        continue
                if back_button_game_rect and back_button_game_rect.collidepoint(click_pos):
                    game_state = "MENU"
                    game_mode = None
                    board = chess.Board()
                    selected_square = source_square = None
                    valid_moves_for_selected_piece = []
                    computer_move_pending = False
                    cvc_move_pending = False
                    reset_move_history()
                    elo_input = ""
                    is_typing_elo = False
                    bot_win = 0
                    bot_win_cvc = 0
                    last_move = None
                    continue
                if game_mode == "CVC":
                    continue  # No player interaction in CvC
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
                            if check_promotion(source_square, target_square):
                                continue
                            move_to_try = chess.Move(source_square, target_square)
                            if move_to_try in valid_moves_for_selected_piece:
                                board.push(move_to_try)
                                add_move_to_history(move_to_try)
                                last_move = move_to_try
                                is_after_undo = False
                                print(f"Player ({'White' if board.turn != chess.WHITE else 'Black'}) moves: {move_to_try.uci()}")
                                selected_square = source_square = None
                                valid_moves_for_selected_piece = []
                                if board.is_game_over():
                                    game_state = "GAME_OVER"
                                    game_over_message = get_game_over_message(board)
                                    if game_mode == "PVC":
                                        bot_rating = get_game_elo(board)
                                        with open('bot_elo.txt', 'w') as file:
                                            file.write(str(bot_rating))
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
                    cvc_move_pending = False
                    reset_move_history()
                    elo_input = ""
                    is_typing_elo = False
                    bot_win = 0
                    bot_win_cvc = 0
                    last_move = None

        elif game_state == "PROMOTION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = pygame.mouse.get_pos()
                promotion_selected = False
                for piece_rect, piece_type in promotion_rects:
                    if piece_rect.collidepoint(click_pos):
                        promotion_move = chess.Move(promotion_source, promotion_target, promotion=piece_type)
                        if promotion_move in board.legal_moves:
                            board.push(promotion_move)
                            add_move_to_history(promotion_move)
                            print(f"Player promotes to {chess.piece_name(piece_type)}")
                            selected_square = source_square = None
                            valid_moves_for_selected_piece = []
                            is_after_undo = False
                            game_state = "PLAYING"
                            if board.is_game_over():
                                game_state = "GAME_OVER"
                                game_over_message = get_game_over_message(board)
                                if game_mode == "PVC":
                                    bot_rating = get_game_elo(board)
                                    with open('bot_elo.txt', 'w') as file:
                                        file.write(str(bot_rating))
                                print(f"Game Over: {game_over_message}")
                            elif game_mode == "PVC" and board.turn == computer_color:
                                computer_move_pending = True
                                last_computer_move_time = current_time
                            promotion_selected = True
                            break
                if not promotion_selected:
                    if not any(rect.collidepoint(click_pos) for rect, _ in promotion_rects):
                        game_state = "PLAYING"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                scroll_offset -= 0.1
                if scroll_offset < 0:
                    scroll_offset = 0
            elif event.button == 5:
                scroll_offset += 0.1
                if scroll_offset > 1:
                    scroll_offset = 1
            elif event.button == 1:
                if thumb_rect and thumb_rect.collidepoint(mouse_pos):
                    scroll_dragging = True
                    scroll_start_y = mouse_pos[1]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                scroll_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if scroll_dragging:
                dy = mouse_pos[1] - scroll_start_y
                scroll_start_y = mouse_pos[1]
                scroll_offset += dy / (SIDEBAR_HEIGHT - 50)
                if scroll_offset < 0:
                    scroll_offset = 0
                elif scroll_offset > 1:
                    scroll_offset = 1

    update_timers()

    if game_mode == "PVC" and board.turn == computer_color and not computer_move_pending and game_state == "PLAYING" and not is_after_undo:
        computer_move_pending = True
        last_computer_move_time = current_time

    if game_mode == "CVC" and game_state == "PLAYING" and not board.is_game_over(claim_draw=True):
        if not cvc_move_pending:
            cvc_move_pending = True
            cvc_last_move_time = current_time
        if cvc_move_pending and (current_time - cvc_last_move_time > CVC_MOVE_DELAY):
            current_player = "Bot A (White)" if board.turn == cvc_bot_a_color else "Bot B (Black)"
            print(f"{current_player} đang suy nghĩ...")
            best_move = make_engine_move(board)
            if best_move:
                move_uci = best_move.uci()
                if best_move.promotion:
                    move_uci += chess.piece_symbol(best_move.promotion).lower()
                    print(f"{current_player} moves: {move_uci} (promotes to {chess.piece_name(best_move.promotion).upper()})")
                else:
                    print(f"{current_player} moves: {move_uci}")
                try:
                    san_move = board.san(best_move)
                except ValueError:
                    san_move = move_uci
                board.push(best_move)
                add_move_to_history(best_move)
                last_move = best_move
                if board.is_game_over(claim_draw=True):
                    game_state = "GAME_OVER"
                    game_over_message = get_game_over_message(board)
                    calculate_and_save_elos_cvc()
                    print(f"Game Over: {game_over_message}")
            else:
                print(f"{current_player} không tìm thấy nước đi hợp lệ.")
                game_state = "GAME_OVER"
                game_over_message = get_game_over_message(board)
                calculate_and_save_elos_cvc()
                print(f"Game Over: {game_over_message}")
            cvc_move_pending = False

    if computer_move_pending and (current_time - last_computer_move_time > 500):
        computer_move = make_random_computer_move(board)
        if computer_move:
            board.push(computer_move)
            add_move_to_history(computer_move)
            last_move = computer_move
            print(f"Computer moves: {computer_move.uci()}")
            if board.is_game_over():
                game_state = "GAME_OVER"
                game_over_message = get_game_over_message(board)
                bot_rating = get_game_elo(board)
                with open('bot_elo.txt', 'w') as file:
                    file.write(str(bot_rating))
                print(f"Game Over: {game_over_message}")
        computer_move_pending = False

    screen.fill(MENU_BG_COLOR)
    if game_state == "MENU":
        menu_buttons = draw_menu(screen)
        back_button_game_rect = None
        back_button_over_rect = None
        last_move = None
    elif game_state == "ENTER_ELO":
        pygame.draw.rect(screen, WHITE, pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40), border_radius=5)
        pygame.draw.rect(screen, BLACK, pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40), 2, border_radius=5)
        elo_surface = MSG_FONT.render(elo_input, True, BLACK)
        screen.blit(elo_surface, (WIDTH // 2 - 90, HEIGHT // 2 - 10))
        instruction_surface = MSG_FONT.render("Enter your ELO and press Enter", True, TEXT_COLOR)
        screen.blit(instruction_surface, (WIDTH // 2 - 150, HEIGHT // 2 - 60))
    elif game_state == "PLAYING":
        board_surface = screen.subsurface(pygame.Rect(0, TOP_MARGIN, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        # highlight_last_move(screen, last_move, game_state)
        if selected_square is not None:
            highlight_square(board_surface, selected_square)
            highlight_valid_moves(board_surface, valid_moves_for_selected_piece)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = None
        draw_timer(screen, black_timer, is_top=True)
        draw_timer(screen, white_timer, is_top=False)
        draw_move_history_sidebar(screen)
    elif game_state == "GAME_OVER":
        board_surface = screen.subsurface(pygame.Rect(0, TOP_MARGIN, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        back_button_over_rect = draw_game_over(screen, game_over_message)
        draw_move_history_sidebar(screen)
    elif game_state == "PROMOTION":
        board_surface = screen.subsurface(pygame.Rect(0, TOP_MARGIN, BOARD_SIZE, BOARD_SIZE))
        draw_board(board_surface)
        if selected_square is not None:
            highlight_square(board_surface, selected_square)
            highlight_valid_moves(board_surface, valid_moves_for_selected_piece)
        draw_pieces(board_surface, board)
        back_button_game_rect = draw_game_info(screen, board, game_mode)
        draw_promotion_screen(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()