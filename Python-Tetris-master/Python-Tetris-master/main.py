import pygame
import sys
from copy import deepcopy
from random import choice

# --- CẤU HÌNH ---
W, H = 10, 20
TILE = 30 
FPS = 60
RES = 1100, 750

pygame.init()
pygame.key.set_repeat(200, 50) 
sc = pygame.display.set_mode(RES)
pygame.display.set_caption("Tetris Battle")
clock = pygame.time.Clock()

# --- TẢI HÌNH NỀN ---
bg_img = pygame.image.load('img/bg.jpg').convert()
bg_img = pygame.transform.scale(bg_img, RES) 

# --- BẬT NHẠC NỀN ---
# 1. Nhạc nền
pygame.mixer.init()
pygame.mixer.music.load('sound/ThemeSound.mp3') 
pygame.mixer.music.set_volume(0.4) 
pygame.mixer.music.play(-1) 

# 2. Âm thanh ăn điểm
clear_sound = pygame.mixer.Sound('sound/ClearRow.mp3')
clear_sound.set_volume(0.8)

# --- MÀU SẮC ---
CYAN = '#41AFDE'
BLUE = '#1165B5'
ORANGE = '#F38927'
YELLOW = '#F6D03C'
GREEN = '#42B642'
PURLE = '#B451AC'
RED = '#EF624D'

# --- DỮ LIỆU KHỐI ---
FIGURES_DATA = [
    {'pos': [(0, 0), (-1, 0), (1, 0), (-2, 0)], 'color': CYAN},     # I 
    {'pos': [(0, 0), (-1, 0), (0, -1), (-1, -1)], 'color': BLUE},    # O 
    {'pos': [(0, 0), (-1, 0), (0, -1), (1, -1)], 'color': ORANGE}, # S 
    {'pos': [(0, 0), (1, 0), (0, -1), (-1, -1)], 'color': YELLOW}, # Z   
    {'pos': [(0, 0), (-1, 0), (1, 0), (-1, -1)], 'color': GREEN},  # J 
    {'pos': [(0, 0), (-1, 0), (1, 0), (1, -1)], 'color': PURLE},   # L 
    {'pos': [(0, 0), (-1, 0), (1, 0), (0, -1)], 'color': RED}      # T 
]

class Player:
    """
    Lớp đại diện cho thực thể người chơi, quản lý tọa độ, điểm số, trạng thái 
    và đồ họa độc lập cho từng không gian sân chơi.
    """
    def __init__(self, x_offset, name):
        """
        Khởi tạo đối tượng người chơi mới.

        Args:
            x_offset (int): Độ lệch trục X trên màn hình, dùng để định tuyến không gian vẽ bàn chơi.
            name (str): Chuỗi định danh hiển thị tên người chơi trên UI.
        """
        self.x_offset = x_offset
        self.name = name
        self.field = [[0 for _ in range(W)] for _ in range(H)]
        self.score = 0
        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
        self.game_over = False
        self.next_figure = self.get_new_figure()
        self.figure = self.get_new_figure()
    
    def get_new_figure(self):
        """
        Khởi tạo và trích xuất ngẫu nhiên một đối tượng khối gạch (Tetromino) từ tập dữ liệu.

        Returns:
            dict: Từ điển chứa cấu trúc khối gạch, bao gồm danh sách các khung chữ nhật (`rects`), 
                  mã màu (`color`), và tọa độ nguyên thủy (`raw_pos`).
        """
        fig = choice(FIGURES_DATA)
        return {
            'rects': [pygame.Rect(x + W // 2, y - 1, 1, 1) for x, y in fig['pos']],
            'color': fig['color'],
            'raw_pos': fig['pos'] 
        }
    
    def check_borders(self, rects):
        """
        Kiểm tra trạng thái va chạm của khối gạch với biên của sân chơi và các khối đã cố định.

        Args:
            rects (list): Danh sách 4 đối tượng `pygame.Rect` cấu thành nên khối gạch cần kiểm tra.

        Returns:
            bool: `True` nếu vị trí hợp lệ (không va chạm), `False` nếu xảy ra va chạm.
        """
        for i in range(4):
            if rects[i].x < 0 or rects[i].x > W - 1: return False
            if rects[i].y > H - 1 or (rects[i].y >= 0 and self.field[rects[i].y][rects[i].x]):
                return False
        return True

    def update(self, dx, dy, rotate, hard_drop):
        """
        Xử lý logic vật lý vòng đời: di chuyển, xoay, giả lập trọng lực rơi và khóa khối gạch.

        Args:
            dx (int): Biến thiên trục X (-1, 0, 1) tương ứng thao tác dịch ngang.
            dy (int): Biến thiên trục Y tương ứng thao tác thả rơi mềm (Soft drop).
            rotate (bool): Cờ trạng thái kích hoạt xoay khối gạch.
            hard_drop (bool): Cờ trạng thái kích hoạt thả khối gạch rơi tự do (Hard drop).
        """
        if self.game_over: return

        if not self.check_borders(self.figure['rects']):
            self.game_over = True
            return

        # 1. Di chuyển ngang
        old_rects = deepcopy(self.figure['rects'])
        for i in range(4): self.figure['rects'][i].x += dx
        if not self.check_borders(self.figure['rects']):
            self.figure['rects'] = old_rects

        # 2. Xoay bằng ma trận xoay
        if rotate:
            center = self.figure['rects'][0]
            old_rects = deepcopy(self.figure['rects'])
            for i in range(4):
                x = self.figure['rects'][i].y - center.y
                y = self.figure['rects'][i].x - center.x
                self.figure['rects'][i].x = center.x - x
                self.figure['rects'][i].y = center.y + y
            if not self.check_borders(self.figure['rects']):
                self.figure['rects'] = old_rects

        # 3. Thả rơi mềm (Softdrop)
        if dy > 0:
            old_rects = deepcopy(self.figure['rects'])
            for i in range(4): self.figure['rects'][i].y += dy
            if not self.check_borders(self.figure['rects']):
                self.figure['rects'] = old_rects 
            else:
                self.score += 1 

        # 4. Rơi lập tức (Hard drop)
        if hard_drop:
            distance_count = -1
            while self.check_borders(self.figure['rects']):
                for i in range(4): self.figure['rects'][i].y += 1
                distance_count += 1

            for i in range(4): self.figure['rects'][i].y -= 1
            self.anim_count = self.anim_limit
            self.score += distance_count * 2

        # 5. Rơi tự do & Xử lý chạm đáy/khóa gạch
        self.anim_count += self.anim_speed
        if self.anim_count >= self.anim_limit:
            self.anim_count = 0
            old_rects = deepcopy(self.figure['rects'])
    
            for i in range(4): self.figure['rects'][i].y += 1
            if not self.check_borders(self.figure['rects']):
                self.figure['rects'] = deepcopy(old_rects)
                
                # Lưu các khối hợp lệ (y >= 0) vào ma trận lưới để cố định
                for i in range(4):
                    if old_rects[i].y >= 0:
                        self.field[old_rects[i].y][old_rects[i].x] = self.figure['color']
                
                # Kiểm tra Game Over nếu gạch bị kẹt trên nóc sân
                for i in range(4):
                    if old_rects[i].y < 0:
                        self.game_over = True
                        return  
                
                # Cập nhật khối gạch mới và dọn dẹp hàng
                self.figure = self.next_figure
                self.next_figure = self.get_new_figure()
                self.anim_limit = 2000
                self.clear_lines()

    def clear_lines(self):
        """
        Quét ma trận sân chơi, xóa các hàng đã được lấp đầy, dồn mảng xuống 
        và cập nhật điểm thưởng dựa trên số lượng hàng bị phá hủy.
        """
        line, lines = H - 1, 0
        for row in range(H - 1, -1, -1):
            count = sum(1 for i in range(W) if self.field[row][i])
            self.field[line] = self.field[row]
            if count < W: line -= 1
            else: lines += 1
            
        if lines > 0: clear_sound.play()
                
        # Hệ số điểm (Combo càng cao, điểm thưởng càng lớn)
        self.score += {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}[lines]

    def draw(self, screen):
        """
        Kết xuất toàn bộ giao diện trò chơi lên cửa sổ hiển thị.

        Args:
            screen (pygame.Surface): Bề mặt đích nơi hệ thống sẽ vẽ giao diện.
        """
        # Sân chơi mờ (Glassmorphism)
        game_surf = pygame.Surface((W * TILE, H * TILE), pygame.SRCALPHA)
        game_surf.fill((10, 10, 15, 150)) 
        
        for x in range(W):
            for y in range(H):
                pygame.draw.rect(game_surf, (255, 255, 255, 30), (x * TILE, y * TILE, TILE, TILE), 1)

        # Gạch cố định
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(game_surf, col, (x * TILE, y * TILE, TILE-1, TILE-1))

        screen.blit(game_surf, (self.x_offset, 80))

        # Bóng mờ (Ghost Piece)
        ghost = deepcopy(self.figure['rects'])
        while self.check_borders(ghost):
            for i in range(4): ghost[i].y += 1
        for i in range(4): ghost[i].y -= 1
        
        for i in range(4):
            gx = self.x_offset + ghost[i].x * TILE
            gy = 80 + ghost[i].y * TILE
            pygame.draw.rect(screen, (120, 120, 130), (gx, gy, TILE-1, TILE-1))

        # Gạch đang điều khiển
        for i in range(4):
            fx = self.x_offset + self.figure['rects'][i].x * TILE
            fy = 80 + self.figure['rects'][i].y * TILE
            pygame.draw.rect(screen, self.figure['color'], (fx, fy, TILE-1, TILE-1))

        # Khối gạch tiếp theo (Next Tetromino)
        next_box_w, next_box_l = 5, 4 
        next_surf = pygame.Surface((next_box_w * TILE, next_box_l * TILE))
        next_surf.fill((20, 20, 25))
        pygame.draw.rect(next_surf, (100, 100, 100), (0, 0, next_box_w * TILE, next_box_l * TILE), 2)
        
        raw_x = [p[0] for p in self.next_figure['raw_pos']]
        raw_y = [p[1] for p in self.next_figure['raw_pos']]
        min_x, max_x = min(raw_x), max(raw_x)
        min_y, max_y = min(raw_y), max(raw_y)
        w = max_x - min_x + 1
        h = max_y - min_y + 1
        
        offset_x = (next_box_w - w) / 2 - min_x
        offset_y = (next_box_l - h) / 2 - min_y
        
        for x, y in self.next_figure['raw_pos']:
            pygame.draw.rect(next_surf, self.next_figure['color'], 
                             ((x + offset_x) * TILE, (y + offset_y) * TILE, TILE-1, TILE-1))
        
        screen.blit(next_surf, (self.x_offset + W * TILE + 20, 80))

        # Văn bản UI
        font = pygame.font.SysFont('Arial', 28, bold=True)
        name_txt = font.render(f"{self.name}", True, (255, 255, 255))
        score_txt = font.render(f"Score: {self.score}", True, (255, 215, 0))
        next_txt = font.render("NEXT", True, (200, 200, 200))
        
        screen.blit(name_txt, (self.x_offset, 10))
        screen.blit(score_txt, (self.x_offset, 40))
        screen.blit(next_txt, (self.x_offset + W * TILE + 20, 50))

        if self.game_over:
            over_txt = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_txt, (self.x_offset + 80, 350))

def show_start_screen():
    """
    Hiển thị giao diện màn hình chờ chính (Main Menu).
    """
    font_title = pygame.font.SysFont('Arial', 100, bold=True)
    font_btn = pygame.font.SysFont('Arial', 35, bold=True)
    
    title_surf = font_title.render("TETRIS BATTLE", True, (65, 175, 222))
    title_rect = title_surf.get_rect(center=(RES[0] // 2, RES[1] // 2 - 120))
    
    btn_w, btn_h = 350, 70
    btn1_rect = pygame.Rect(0, 0, btn_w, btn_h)
    btn1_rect.center = (RES[0] // 2, RES[1] // 2 + 20)
    
    btn2_rect = pygame.Rect(0, 0, btn_w, btn_h)
    btn2_rect.center = (RES[0] // 2, RES[1] // 2 + 120)
    
    while True:
        sc.blit(bg_img, (0, 0)) 
        
        overlay = pygame.Surface(RES, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        sc.blit(overlay, (0, 0))
        sc.blit(title_surf, title_rect)
        
        mx, my = pygame.mouse.get_pos()
        
        color_btn1 = (65, 175, 222) if btn1_rect.collidepoint((mx, my)) else (30, 110, 150)
        color_btn2 = (239, 98, 77) if btn2_rect.collidepoint((mx, my)) else (160, 50, 40)
        
        pygame.draw.rect(sc, color_btn1, btn1_rect, border_radius=15)
        pygame.draw.rect(sc, color_btn2, btn2_rect, border_radius=15)
        
        opt1_surf = font_btn.render("SINGLE PLAYER", True, (255, 255, 255))
        opt2_surf = font_btn.render("MULTIPLAYER", True, (255, 255, 255))
        sc.blit(opt1_surf, opt1_surf.get_rect(center=btn1_rect.center))
        sc.blit(opt2_surf, opt2_surf.get_rect(center=btn2_rect.center))
        
        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if btn1_rect.collidepoint(event.pos):
                        return 1
                    if btn2_rect.collidepoint(event.pos):
                        return 2

# --- KHỞI CHẠY TRÒ CHƠI ---
num_players = show_start_screen()

if num_players == 1:
    p1 = Player(350, "PLAYER 1")
    p2 = None
else:
    p1 = Player(50, "PLAYER 1")
    p2 = Player(600, "PLAYER 2")

# --- KHỞI TẠO NÚT BẤM CHO MÀN HÌNH KẾT THÚC ---
btn_action_w, btn_action_h = 220, 60
btn_restart_rect = pygame.Rect(0, 0, btn_action_w, btn_action_h)
btn_restart_rect.center = (RES[0] // 2 - 130, RES[1] // 2 + 120)

btn_menu_rect = pygame.Rect(0, 0, btn_action_w, btn_action_h)
btn_menu_rect.center = (RES[0] // 2 + 130, RES[1] // 2 + 120)

# --- VÒNG LẶP GAME CHÍNH (MAIN LOOP) ---
while True:
    sc.fill((30, 30, 35))
    sc.blit(bg_img, (0, 0))
    dx1, dy1, rot1, drop1 = 0, 0, False, False
    dx2, dy2, rot2, drop2 = 0, 0, False, False

    game_ended = (num_players == 1 and p1.game_over) or (num_players == 2 and p1.game_over and p2.game_over)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            sys.exit()  
        
        # XỬ LÝ PHÍM BẤM
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or (num_players == 1 and event.key == pygame.K_LEFT): dx1 = -1
            if event.key == pygame.K_d or (num_players == 1 and event.key == pygame.K_RIGHT): dx1 = 1
            if event.key == pygame.K_w or (num_players == 1 and event.key == pygame.K_UP): rot1 = True
            if event.key == pygame.K_s or (num_players == 1 and event.key == pygame.K_DOWN): dy1 = 1
            if event.key == pygame.K_SPACE: drop1 = True
            
            if num_players == 2:
                if event.key == pygame.K_LEFT: dx2 = -1
                if event.key == pygame.K_RIGHT: dx2 = 1
                if event.key == pygame.K_UP: rot2 = True
                if event.key == pygame.K_DOWN: dy2 = 1
                if event.key == pygame.K_p: drop2 = True

            # Bấm phím tắt khi kết thúc
            if game_ended:
                if event.key == pygame.K_r: 
                    if num_players == 1:
                        p1 = Player(350, "PLAYER 1")
                    else:
                        p1 = Player(50, "PLAYER 1")
                        p2 = Player(600, "PLAYER 2")
                
                if event.key == pygame.K_m: 
                    num_players = show_start_screen()
                    if num_players == 1:
                        p1 = Player(350, "PLAYER 1")
                        p2 = None
                    else:
                        p1 = Player(50, "PLAYER 1")
                        p2 = Player(600, "PLAYER 2")

        # XỬ LÝ CLICK CHUỘT KHI KẾT THÚC
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_ended:
                if btn_restart_rect.collidepoint(event.pos):
                    if num_players == 1:
                        p1 = Player(350, "PLAYER 1")
                    else:
                        p1 = Player(50, "PLAYER 1")
                        p2 = Player(600, "PLAYER 2")
                
                if btn_menu_rect.collidepoint(event.pos):
                    num_players = show_start_screen()
                    if num_players == 1:
                        p1 = Player(350, "PLAYER 1")
                        p2 = None
                    else:
                        p1 = Player(50, "PLAYER 1")
                        p2 = Player(600, "PLAYER 2")

    p1.update(dx1, dy1, rot1, drop1)
    if num_players == 2:
        p2.update(dx2, dy2, rot2, drop2)
    
    p1.draw(sc)
    if num_players == 2:
        p2.draw(sc)

    # --- UI KẾT THÚC ---
    if game_ended:
        overlay = pygame.Surface(RES, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        sc.blit(overlay, (0, 0))

        if num_players == 2:
            if p1.score > p2.score:
                win_text, win_color = f"{p1.name} WINS!", (65, 175, 222)  
            elif p2.score > p1.score:
                win_text, win_color = f"{p2.name} WINS!", (239, 98, 77)  
            else:
                win_text, win_color = "IT'S A TIE!", (246, 208, 60)
            score_text = f"{p1.name}: {p1.score}   VS   {p2.name}: {p2.score}"
        else:
            win_text, win_color = "GAME OVER", (255, 50, 50)
            score_text = f"YOUR SCORE: {p1.score}"

        font_big = pygame.font.SysFont('Arial', 80, bold=True)
        txt_win_surface = font_big.render(win_text, True, win_color)
        win_rect = txt_win_surface.get_rect(center=(RES[0] // 2, RES[1] // 2 - 60))
        sc.blit(txt_win_surface, win_rect)

        font_small = pygame.font.SysFont('Arial', 40, bold=True)
        txt_score_surface = font_small.render(score_text, True, (255, 255, 255))
        score_rect = txt_score_surface.get_rect(center=(RES[0] // 2, RES[1] // 2 + 20))
        sc.blit(txt_score_surface, score_rect)

        # ---------------------------------------------------------
        # VẼ NÚT BẤM KẾT THÚC (HOVER EFFECT)
        mx, my = pygame.mouse.get_pos()
        font_btn_action = pygame.font.SysFont('Arial', 25, bold=True)
        
        # Đổi màu nếu rê chuột vào (Hover)
        color_restart = (42, 182, 66) if btn_restart_rect.collidepoint((mx, my)) else (30, 130, 45)
        color_menu = (239, 137, 39) if btn_menu_rect.collidepoint((mx, my)) else (190, 100, 20)

        # Vẽ hình chữ nhật bo tròn
        pygame.draw.rect(sc, color_restart, btn_restart_rect, border_radius=10)
        pygame.draw.rect(sc, color_menu, btn_menu_rect, border_radius=10)

        # Vẽ chữ lên nút
        txt_restart = font_btn_action.render("RESTART (R)", True, (255, 255, 255))
        txt_menu = font_btn_action.render("MENU (M)", True, (255, 255, 255))

        sc.blit(txt_restart, txt_restart.get_rect(center=btn_restart_rect.center))
        sc.blit(txt_menu, txt_menu.get_rect(center=btn_menu_rect.center))
        # ---------------------------------------------------------

    pygame.display.flip()
    clock.tick(FPS)
