import pygame
from copy import deepcopy
from random import choice

# --- CẤU HÌNH ---
W, H = 10, 20
TILE = 30 
FPS = 60
RES = 1100, 750  # Tăng chiều rộng để đủ chỗ cho 2 thanh "Next"

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()

CYAN = '#41AFDE'
BLUE = '#1165B5'
ORANGE = '#F38927'
YELLOW = '#F6D03C'
GREEN = '#42B642'
PURLE = '#B451AC'
RED = '#EF624D'

# --- DỮ LIỆU KHỐI ---
FIGURES_DATA = [
    {'pos': [(-1, 0), (-2, 0), (0, 0), (1, 0)], 'color': CYAN},    #I
    {'pos': [(0, -1), (-1, -1), (-1, 0), (0, 0)], 'color': BLUE},  #O
    {'pos': [(-1, 0), (-1, 1), (0, 0), (0, -1)], 'color': ORANGE}, #S
    {'pos': [(0, 0), (-1, 0), (0, 1), (-1, -1)], 'color': YELLOW}, #Z  
    {'pos': [(0, 0), (0, -1), (0, 1), (-1, -1)], 'color': GREEN},  #J
    {'pos': [(0, 0), (0, -1), (0, 1), (1, -1)], 'color': PURLE},   #L
    {'pos': [(0, 0), (1, 0), (-1, 0), (0, -1)], 'color': RED}      # T
]

class Player:
    def __init__(self, x_offset, name):
        self.x_offset = x_offset
        self.name = name
        self.field = [[0 for _ in range(W)] for _ in range(H)]
        self.score = 0
        self.anim_count, self.anim_speed, self.anim_limit = 0, 60, 2000
        self.figure = self.get_new_figure()
        self.next_figure = self.get_new_figure()
        self.game_over = False

    def get_new_figure(self):
        fig = choice(FIGURES_DATA)
        return {
            'rects': [pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig['pos']],
            'color': fig['color'],
            'raw_pos': fig['pos'] # Lưu lại để vẽ preview
        }

    def check_borders(self, rects):
        for i in range(4):
            if rects[i].x < 0 or rects[i].x > W - 1: return False
            if rects[i].y > H - 1 or (rects[i].y >= 0 and self.field[rects[i].y][rects[i].x]):
                return False
        return True

    def update(self, dx, rotate, hard_drop):
        if self.game_over: return

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

        # 3. Hard drop (Rơi ngay)
        if hard_drop:
            while self.check_borders(self.figure['rects']):
                for i in range(4): self.figure['rects'][i].y += 1
            for i in range(4): self.figure['rects'][i].y -= 1
            self.anim_count = self.anim_limit

        # 4. Rơi tự do
        self.anim_count += self.anim_speed
        if self.anim_count >= self.anim_limit:
            self.anim_count = 0
            old_rects = deepcopy(self.figure['rects'])
            for i in range(4): self.figure['rects'][i].y += 1
            if not self.check_borders(self.figure['rects']):
                for i in range(4):
                    if old_rects[i].y < 0:
                        self.game_over = True
                        return
                    self.field[old_rects[i].y][old_rects[i].x] = self.figure['color']
                self.figure = self.next_figure
                self.next_figure = self.get_new_figure()
                self.anim_limit = 2000
                self.clear_lines()

    def clear_lines(self):
        line, lines = H - 1, 0
        for row in range(H - 1, -1, -1):
            count = sum(1 for i in range(W) if self.field[row][i])
            self.field[line] = self.field[row]
            if count < W: line -= 1
            else: lines += 1
        self.score += {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}[lines]

    def draw(self, screen):
        # --- VẼ SÂN CHƠI CHÍNH ---
        game_surf = pygame.Surface((W * TILE, H * TILE))
        game_surf.fill((10, 10, 15))
        for x in range(W):
            for y in range(H):
                pygame.draw.rect(game_surf, (40, 40, 45), (x * TILE, y * TILE, TILE, TILE), 1)

        # Vẽ bóng mờ (Ghost)
        ghost = deepcopy(self.figure['rects'])
        while self.check_borders(ghost):
            for i in range(4): ghost[i].y += 1
        for i in range(4): ghost[i].y -= 1
        for i in range(4):
            pygame.draw.rect(game_surf, (45, 45, 50), (ghost[i].x * TILE, ghost[i].y * TILE, TILE-1, TILE-1))

        # Vẽ các khối đã cố định
        for y, row in enumerate(self.field):
            for x, col in enumerate(row):
                if col:
                    pygame.draw.rect(game_surf, col, (x * TILE, y * TILE, TILE-1, TILE-1))

        # Vẽ khối đang điều khiển
        for i in range(4):
            pygame.draw.rect(game_surf, self.figure['color'], (self.figure['rects'][i].x * TILE, self.figure['rects'][i].y * TILE, TILE-1, TILE-1))

        screen.blit(game_surf, (self.x_offset, 80))

        # --- VẼ KHỐI TIẾP THEO (NEXT) ---
        next_surf = pygame.Surface((4 * TILE, 4 * TILE))
        next_surf.fill((20, 20, 25))
        pygame.draw.rect(next_surf, (100, 100, 100), (0, 0, 4 * TILE, 4 * TILE), 2)
        
        for x, y in self.next_figure['raw_pos']:
            # Căn giữa khối trong ô Next (thêm offset 1.5)
            pygame.draw.rect(next_surf, self.next_figure['color'], ((x + 1.5) * TILE, (y + 1.5) * TILE, TILE-1, TILE-1))
        
        screen.blit(next_surf, (self.x_offset + W * TILE + 20, 80))

        # --- VẼ CHỮ (NAME, SCORE, NEXT LABEL) ---
        font = pygame.font.SysFont('Arial', 28, bold=True)
        name_txt = font.render(f"{self.name}", True, (255, 255, 255))
        score_txt = font.render(f"Score: {self.score}", True, (255, 215, 0))
        next_txt = font.render("NEXT", True, (200, 200, 200))
        
        screen.blit(name_txt, (self.x_offset, 10))
        screen.blit(score_txt, (self.x_offset, 40))
        screen.blit(next_txt, (self.x_offset + W * TILE + 20, 50))

        if self.game_over:
            over_txt = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(over_txt, (self.x_offset + 40, 350))

# --- KHỞI TẠO ---
p1 = Player(50, "PLAYER 1")    # Bên trái
p2 = Player(600, "PLAYER 2")   # Bên phải

while True:
    sc.fill((30, 30, 35))
    dx1, rot1, drop1 = 0, False, False
    dx2, rot2, drop2 = 0, False, False

    for event in pygame.event.get():
        if event.type == pygame.QUIT: exit()
        if event.type == pygame.KEYDOWN:
            # P1 Controls (Arrows)
            if event.key == pygame.K_LEFT: dx1 = -1
            if event.key == pygame.K_RIGHT: dx1 = 1
            if event.key == pygame.K_UP: rot1 = True
            if event.key == pygame.K_DOWN: p1.anim_limit = 100
            if event.key == pygame.K_SPACE: drop1 = True
            # P2 Controls (WASD)
            if event.key == pygame.K_a: dx2 = -1
            if event.key == pygame.K_d: dx2 = 1
            if event.key == pygame.K_w: rot2 = True
            if event.key == pygame.K_s: p2.anim_limit = 100
            if event.key == pygame.K_q: drop2 = True
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN: p1.anim_limit = 2000
            if event.key == pygame.K_s: p2.anim_limit = 2000

    # Cập nhật logic & Vẽ
    p1.update(dx1, rot1, drop1)
    p2.update(dx2, rot2, drop2)
    p1.draw(sc)
    p2.draw(sc)

    pygame.display.flip()
    clock.tick(FPS)
