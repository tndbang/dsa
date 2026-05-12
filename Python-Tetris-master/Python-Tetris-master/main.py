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
pygame.display.set_caption("2-Player Tetris")
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
    {'pos': [(0, 0), (-1, 0), (1, 0), (-2, 0)], 'color': CYAN},     # I (Cao 1 ô)
    {'pos': [(0, 0), (-1, 0), (0, -1), (-1, -1)], 'color': BLUE},    # O (Vuông 2x2)
    {'pos': [(0, 0), (-1, 0), (0, -1), (1, -1)], 'color': ORANGE}, # S (Cao 2 ô)
    {'pos': [(0, 0), (1, 0), (0, -1), (-1, -1)], 'color': YELLOW}, # Z (Cao 2 ô)  
    {'pos': [(0, 0), (-1, 0), (1, 0), (-1, -1)], 'color': GREEN},  # J (Cao 2 ô)
    {'pos': [(0, 0), (-1, 0), (1, 0), (1, -1)], 'color': PURLE},   # L (Cao 2 ô)
    {'pos': [(0, 0), (-1, 0), (1, 0), (0, -1)], 'color': RED}      # T (Cao 2 ô)
]

class Player:
    def __init__(self, x_offset, name):
        """ Hàm khởi tạo """
        self.x_offset = x_offset
        self.name = name
        self.field = [[0 for _ in range(W)] for _ in range(H)]
        self.score = 0
        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
        self.game_over = False
        self.next_figure = self.get_new_figure()
        self.figure = self.get_new_figure()

    
    def get_new_figure(self):
        """ Hàm tạo ngẫu nhiên một hình """
        fig = choice(FIGURES_DATA)
        return {
            'rects': [pygame.Rect(x + W // 2, y - 1, 1, 1) for x, y in fig['pos']],
            'color': fig['color'],
            'raw_pos': fig['pos'] 
        }
    
    def check_borders(self, rects):
        """ Hàm kiểm tra có tràn viền hay không """
        for i in range(4):
            if rects[i].x < 0 or rects[i].x > W - 1: return False
            if rects[i].y > H - 1 or (rects[i].y >= 0 and self.field[rects[i].y][rects[i].x]):
                return False
        return True

    def update(self, dx, dy, rotate, hard_drop):
        """ Hàm cập nhật vị trí các block """
        if self.game_over: return

        if not self.check_borders(self.figure['rects']):
            self.game_over = True
            return

        # 1. Di chuyển ngang
        old_rects = deepcopy(self.figure['rects'])
        for i in range(4): self.figure['rects'][i].x += dx
        if not self.check_borders(self.figure['rects']):
            self.figure['rects'] = old_rects

        # 2. Xoay
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

        # 3. Softdrop
        if dy > 0:
            old_rects = deepcopy(self.figure['rects'])
            for i in range(4): self.figure['rects'][i].y += dy
            if not self.check_borders(self.figure['rects']):
                self.figure['rects'] = old_rects 
            else:
                self.score += 1 

        # 4. Hard drop (Rơi ngay)
        if hard_drop:
            distance_count = -1
            while self.check_borders(self.figure['rects']):
                for i in range(4): self.figure['rects'][i].y += 1
                distance_count += 1

            for i in range(4): self.figure['rects'][i].y -= 1
            self.anim_count = self.anim_limit
            self.score += distance_count * 2

        # 5. Rơi tự do & Xử lý chạm đáy/gạch
        self.anim_count += self.anim_speed
        if self.anim_count >= self.anim_limit:
            self.anim_count = 0
            old_rects = deepcopy(self.figure['rects'])
    
            for i in range(4): self.figure['rects'][i].y += 1
            if not self.check_borders(self.figure['rects']):
                self.figure['rects'] = deepcopy(old_rects)
                
                # 5.1. Lưu các phần hợp lệ (y >= 0) vào ma trận lưới để hiển thị
                for i in range(4):
                    if old_rects[i].y >= 0:
                        self.field[old_rects[i].y][old_rects[i].x] = self.figure['color']
                
                # 5.2. kiểm tra thua 
                for i in range(4):
                    if old_rects[i].y < 0:
                        self.game_over = True
                        return  
                
                # 5.3. Gọi hình mới nếu chưa thua
                self.figure = self.next_figure
                self.next_figure = self.get_new_figure()
                self.anim_limit = 2000
                self.clear_lines()

    def clear_lines(self):
        """ Hàm kiểm tra và xóa những dòng ăn điểm """
        line, lines = H - 1, 0
        for row in range(H - 1, -1, -1):
            count = sum(1 for i in range(W) if self.field[row][i])
            self.field[line] = self.field[row]
            if count < W: line -= 1
            else: lines += 1
            
        # Nhạc clear dòng
        if lines > 0: clear_sound.play()
                
        # Điểm cộng
        self.score += {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}[lines]

    def draw(self, screen):
        """ Hàm vẽ """
        # --- VẼ SÂN CHƠI CHÍNH ---
        # vẽ nền trong suốt
        game_surf = pygame.Surface((W * TILE, H * TILE), pygame.SRCALPHA)
        game_surf.fill((10, 10, 15, 150)) 
        
        for x in range(W):
            for y in range(H):
                pygame.draw.rect(game_surf, (255, 255, 255, 30), (x * TILE, y * TILE, TILE, TILE), 1)

        # Vẽ các khối đã cố định trong ma trận
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(game_surf, col, (x * TILE, y * TILE, TILE-1, TILE-1))

        # Dán game_surf lên screen TRƯỚC
        screen.blit(game_surf, (self.x_offset, 80))

        # --- VẼ BÓNG MỜ (Ghost) VÀ GẠCH ĐANG RƠI TRỰC TIẾP LÊN MÀN HÌNH CHÍNH ---
        # 1. Tính toán và vẽ Ghost
        ghost = deepcopy(self.figure['rects'])
        while self.check_borders(ghost):
            for i in range(4): ghost[i].y += 1
        for i in range(4): ghost[i].y -= 1
        
        for i in range(4):
            gx = self.x_offset + ghost[i].x * TILE
            gy = 80 + ghost[i].y * TILE
            pygame.draw.rect(screen, (120, 120, 130), (gx, gy, TILE-1, TILE-1))

        # 2. Vẽ gạch đang điều khiển (Figure)
        for i in range(4):
            fx = self.x_offset + self.figure['rects'][i].x * TILE
            fy = 80 + self.figure['rects'][i].y * TILE
            pygame.draw.rect(screen, self.figure['color'], (fx, fy, TILE-1, TILE-1))

        # --- VẼ KHỐI TIẾP THEO (NEXT) ---
        next_box_w, next_box_l = 5, 4 
        next_surf = pygame.Surface((next_box_w * TILE, next_box_l * TILE))
        next_surf.fill((20, 20, 25))
        pygame.draw.rect(next_surf, (100, 100, 100), (0, 0, next_box_w * TILE, next_box_l * TILE), 2)
        
        # 1. Tìm chiều rộng và chiều cao thực tế của khối gạch
        raw_x = [p[0] for p in self.next_figure['raw_pos']]
        raw_y = [p[1] for p in self.next_figure['raw_pos']]
        min_x, max_x = min(raw_x), max(raw_x)
        min_y, max_y = min(raw_y), max(raw_y)
        
        w = max_x - min_x + 1
        h = max_y - min_y + 1
        
        # 2. Tự động tính toán khoảng cách để căn giữa tuyệt đối vào khung 4x4
        offset_x = (next_box_w - w) / 2 - min_x
        offset_y = (next_box_l - h) / 2 - min_y
        
        # 3. Vẽ lên khung
        for x, y in self.next_figure['raw_pos']:
            pygame.draw.rect(next_surf, self.next_figure['color'], 
                             ((x + offset_x) * TILE, (y + offset_y) * TILE, TILE-1, TILE-1))
        
        screen.blit(next_surf, (self.x_offset + W * TILE + 20, 80))

        #--- VẼ CHỮ (NAME, SCORE, NEXT LABEL) ---
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

# --- KHỞI TẠO 2 NGƯỜI CHƠI ---
p1 = Player(50, "PLAYER 1")    # Bên trái
p2 = Player(600, "PLAYER 2")   # Bên phải

# --- VÒNG LẶP GAME CHÍNH ---
while True:
    sc.fill((30, 30, 35))
    sc.blit(bg_img, (0, 0))
    dx1, dy1, rot1, drop1 = 0, 0, False, False
    dx2, dy2, rot2, drop2 = 0, 0, False, False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit() 
            sys.exit()  
        
        if event.type == pygame.KEYDOWN:
            # P1 Controls (Mũi tên)
            if event.key == pygame.K_a: dx1 = -1
            if event.key == pygame.K_d: dx1 = 1
            if event.key == pygame.K_w: rot1 = True
            if event.key == pygame.K_s: dy1 = 1
            if event.key == pygame.K_SPACE: drop1 = True
            
            # P2 Controls (WASD)
            if event.key == pygame.K_LEFT: dx2 = -1
            if event.key == pygame.K_RIGHT: dx2 = 1
            if event.key == pygame.K_UP: rot2 = True
            if event.key == pygame.K_DOWN: dy2 = 1
            if event.key == pygame.K_p: drop2 = True

            # RESTART
            if event.key == pygame.K_r:
                # Chỉ cho phép Restart khi CẢ 2 người đều đã thua
                if p1.game_over and p2.game_over:
                    # Reset lại toàn bộ sân chơi, điểm số, gạch...
                    p1 = Player(50, "PLAYER 1")
                    p2 = Player(600, "PLAYER 2")
            # =====================================

    # Cập nhật logic
    p1.update(dx1, dy1, rot1, drop1)
    p2.update(dx2, dy2, rot2, drop2)
    
    # Vẽ lên màn hình
    p1.draw(sc)
    p2.draw(sc)

    if p1.game_over and p2.game_over:
        # 1. Tạo một lớp phủ màu đen mờ để làm tối sân chơi phía sau
        overlay = pygame.Surface(RES, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200)) 
        sc.blit(overlay, (0, 0))

        # 2. So sánh điểm để tìm người thắng
        if p1.score > p2.score:
            win_text = f"{p1.name} WINS!"
            win_color = (65, 175, 222)  
        elif p2.score > p1.score:
            win_text = f"{p2.name} WINS!"
            win_color = (239, 98, 77)  
        else:
            win_text = "IT'S A TIE!"   
            win_color = (246, 208, 60)  

        # 3. Vẽ chữ Chiến thắng thật to ở chính giữa màn hình
        font_big = pygame.font.SysFont('Arial', 80, bold=True)
        txt_win_surface = font_big.render(win_text, True, win_color)
        # Tự động căn giữa
        win_rect = txt_win_surface.get_rect(center=(RES[0] // 2, RES[1] // 2 - 30))
        sc.blit(txt_win_surface, win_rect)

        # 4. In lại số điểm của cả 2 để so sánh
        font_small = pygame.font.SysFont('Arial', 40, bold=True)
        score_text = f"{p1.name}: {p1.score}   VS   {p2.name}: {p2.score}"
        txt_score_surface = font_small.render(score_text, True, (255, 255, 255))
        score_rect = txt_score_surface.get_rect(center=(RES[0] // 2, RES[1] // 2 + 50))
        sc.blit(txt_score_surface, score_rect)

        # 5. RESTART
        font_restart = pygame.font.SysFont('Arial', 30, bold=True)

        # Tạo chữ chớp nháy (tùy chọn màu)
        restart_text = font_restart.render("PRESS 'R' TO RESTART", True, (200, 255, 200))
        restart_rect = restart_text.get_rect(center=(RES[0] // 2, RES[1] // 2 + 120))
        sc.blit(restart_text, restart_rect)

    # ==========================================

    pygame.display.flip()
    clock.tick(FPS)
