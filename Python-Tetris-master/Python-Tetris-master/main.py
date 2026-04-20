import pygame
from copy import deepcopy
from random import choice, randrange

# ==========================================
# CẤU HÌNH CƠ BẢN & KHỞI TẠO CỬA SỔ
# ==========================================
W, H = 10, 20
TILE = 36
GAME_RES = W * TILE, H * TILE
RES = 600, 752
FPS = 60

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

# ==========================================
# KHỞI TẠO BẢNG CHƠI VÀ DỮ LIỆU KHỐI (TETROMINO)
# ==========================================
grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

CYAN = '#41AFDE'
BLUE = '#1165B5'
ORANGE = '#F38927'
YELLOW = '#F6D03C'
GREEN = '#42B642'
PURLE = '#B451AC'
RED = '#EF624D'

figures_settings = [
    {'pos': [(-1, 0), (-2, 0), (0, 0), (1, 0)], 'color': CYAN},    
    {'pos': [(0, -1), (-1, -1), (-1, 0), (0, 0)], 'color': BLUE}, 
    {'pos': [(-1, 0), (-1, 1), (0, 0), (0, -1)], 'color': ORANGE},
    {'pos': [(0, 0), (-1, 0), (0, 1), (-1, -1)], 'color': YELLOW},  
    {'pos': [(0, 0), (0, -1), (0, 1), (-1, -1)], 'color': GREEN},  
    {'pos': [(0, 0), (0, -1), (0, 1), (1, -1)], 'color': PURLE},   
    {'pos': [(0, 0), (0, -1), (0, 1), (-1, 0)], 'color': RED}      
]

figures = [{'rect' : [pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig['pos']], 'color' : fig['color']} for fig in figures_settings]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

# ==========================================
# KHỞI TẠO BIẾN ANIMATION & ASSETS (HÌNH/CHỮ)
# ==========================================
anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load('img/bg.jpg').convert()
bg = pygame.transform.scale(bg, RES)

game_bg = pygame.image.load('img/bg2.jpg').convert()
game_bg = pygame.transform.scale(game_bg, GAME_RES)

main_font = pygame.font.Font('font/font.ttf', 52)
font = pygame.font.Font('font/font.ttf', 36)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_score = font.render('score:', True, pygame.Color('green'))
title_record = font.render('record:', True, pygame.Color('purple'))

# ==========================================
# KHỞI TẠO MÀU SẮC, ĐIỂM SỐ & TRẠNG THÁI GAME
# ==========================================
figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

# ==========================================
# CÁC HÀM TIỆN ÍCH (LƯU TRỮ VÀ KIỂM TRA LOGIC)
# ==========================================
def check_borders():
    if figure['rect'][i].x < 0 or figure['rect'][i].x > W - 1:
        return False
    elif figure['rect'][i].y > H - 1 or field[figure['rect'][i].y][figure['rect'][i].x]:
        return False
    return True

def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')
            return '0'

def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))

# ==========================================
# VÒNG LẶP TRÒ CHƠI CHÍNH
# ==========================================
while True:
    record = get_record()
    dx, rotate = 0, False
    
    # 1. Vẽ nền màn hình
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (16, 16))
    game_sc.blit(game_bg, (0, 0))
    
    # Delay nhỏ khi ăn điểm để tạo hiệu ứng
    for i in range(lines):
        pygame.time.wait(200)
        
    # 2. Xử lý thao tác người dùng
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
                
    # 3. Cập nhật vị trí khối (Theo trục X)
    figure_old = deepcopy(figure)
    for i in range(4):
        figure['rect'][i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
            
    # 4. Xử lý rơi tự do và chạm đáy (Theo trục Y)
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure['rect'][i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old['rect'][i].y][figure_old['rect'][i].x] = figure_old['color']

                figure = next_figure
                next_figure = deepcopy(choice(figures))
                anim_limit = 2000
                break
                
    # 5. Xử lý thao tác xoay khối
    center = figure['rect'][0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure['rect'][i].y - center.y
            y = figure['rect'][i].x - center.x
            figure['rect'][i].x = center.x - x
            figure['rect'][i].y = center.y + y
            if not check_borders():
                figure = deepcopy(figure_old)
                break
                
    # 6. Kiểm tra hàng đầy, xóa hàng và cộng điểm
    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1
            
    score += scores[lines]
    
    # 7. Vẽ lưới và các khối gạch
    for i_rect in grid:
        pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1)

    for i in range(4):
        figure_rect.x = figure['rect'][i].x * TILE
        figure_rect.y = figure['rect'][i].y * TILE
        color = figure['color']
        pygame.draw.rect(game_sc, color, figure_rect)
        
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)
                
    # 8. Vẽ khu vực hiển thị khối gạch tiếp theo
    for i in range(4):
        figure_rect.x = next_figure['rect'][i].x * TILE + 304
        figure_rect.y = next_figure['rect'][i].y * TILE + 148
        color = next_figure['color']
        pygame.draw.rect(sc, color, figure_rect)
        
    # 9. Vẽ giao diện văn bản (Điểm, Kỷ lục)
    sc.blit(title_tetris, (388, -8))
    sc.blit(title_score, (428, 624))
    sc.blit(font.render(str(score), True, pygame.Color('white')), (440, 672))
    sc.blit(title_record, (420, 520))
    sc.blit(font.render(record, True, pygame.Color('gold')), (440, 568))
    
    # 10. Kiểm tra điều kiện thua game (Game Over)
    for i in range(W):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(W)] for i in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (16, 16))
                pygame.display.flip()
                clock.tick(200)

    # Cập nhật màn hình & Giới hạn FPS
    pygame.display.flip()
    clock.tick(FPS)
