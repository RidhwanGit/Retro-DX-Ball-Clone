from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
from collections import deque

# --- GLOBAL VARIABLES ---

# Game State
page = 'home'
pause = False
over = False
gg = False
score = 0
frame_counter = 0
stars = []

# Slider
x1, x2, x3, x4 = 270, 270, 330, 330
y1, y2, y3, y4 = 5, 15, 15, 5

# Ball
ball_x = 300
ball_y = 30
ball_radius = 7
ball_dx = 0.25
ball_dy = 0.25
ball_speed = 1.0
ball_trail = deque(maxlen=10)

# Level 1 Blocks
blocks1 = [(50 * i, 500, 50 * (i + 1), 520) for i in range(12)]
blocks2 = [(50 * i, 470, 50 * (i + 1), 490) for i in range(12)]
blocks3 = [(50 * i, 440, 50 * (i + 1), 460) for i in range(12)]
blocks4 = [(50 * i, 410, 50 * (i + 1), 430) for i in range(12)]
blocks = blocks1 + blocks2 + blocks3 + blocks4
active_blocks = [True] * len(blocks)

# Level 2 Blocks
blocks5 = [(50 * i, 500 - 20 * i, 50 * (i + 1), 520 - 20 * i) for i in range(12)]
blocks6 = [(50 * i, 470 - 20 * (i + 1), 50 * (i + 1), 490 - 20 * (i + 1)) for i in range(11)]
blocks7 = [(50 * i, 440 - 20 * (i + 2), 50 * (i + 1), 460 - 20 * (i + 2)) for i in range(10)]
blocks8 = [(50 * i, 410 - 20 * (i + 3), 50 * (i + 1), 430 - 20 * (i + 3)) for i in range(9)]
blocksfor2 = blocks5 + blocks6 + blocks7 + blocks8
active_blocksfor2 = [True] * len(blocksfor2)

# Power-ups
p_speed1, p_speed2, p_speed3, p_speed4 = 0, 0, 0, 0
bpu1, bpu2, bpu3, bpu4 = False, False, False, False

# --- GRAPHICS ALGORITHMS ---

def find_zone(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    if abs(dx) > abs(dy):
        if dx >= 0 and dy >= 0: return 0
        elif dx < 0 and dy >= 0: return 3
        elif dx < 0 and dy < 0: return 4
        else: return 7
    else:
        if dx >= 0 and dy >= 0: return 1
        elif dx < 0 and dy >= 0: return 2
        elif dx < 0 and dy < 0: return 5
        else: return 6

def convert_to_zone0(zone, x, y):
    if zone == 0: return x, y
    elif zone == 1: return y, x
    elif zone == 2: return y, -x
    elif zone == 3: return -x, y
    elif zone == 4: return -x, -y
    elif zone == 5: return -y, -x
    elif zone == 6: return -y, x
    elif zone == 7: return x, -y

def convert_back_from_zone0(zone, x, y):
    if zone == 0: return x, y
    elif zone == 1: return y, x
    elif zone == 2: return -y, x
    elif zone == 3: return -x, y
    elif zone == 4: return -x, -y
    elif zone == 5: return -y, -x
    elif zone == 6: return y, -x
    elif zone == 7: return x, -y

def draw_points(x, y):
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def midpoint_line(x0, y0, x1, y1):
    zone = find_zone(x0, y0, x1, y1)
    zx0, zy0 = convert_to_zone0(zone, x0, y0)
    zx1, zy1 = convert_to_zone0(zone, x1, y1)
    dx = zx1 - zx0
    dy = zy1 - zy0
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    y = zy0
    for x in range(zx0, zx1 + 1):
        ox, oy = convert_back_from_zone0(zone, x, y)
        draw_points(ox, oy)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE

def draw_line(x0, y0, x1, y1):
    midpoint_line(x0, y0, x1, y1)

def draw_circle_points(x, y, cx, cy):
    glVertex2f(x + cx, y + cy)
    glVertex2f(y + cx, x + cy)
    glVertex2f(y + cx, -x + cy)
    glVertex2f(x + cx, -y + cy)
    glVertex2f(-x + cx, -y + cy)
    glVertex2f(-y + cx, -x + cy)
    glVertex2f(-y + cx, x + cy)
    glVertex2f(-x + cx, y + cy)

def midpoint_circle(radius, cx, cy):
    d = 1 - radius
    x = 0
    y = radius
    draw_circle_points(x, y, cx, cy)
    while x < y:
        if d < 0:
            d += 2 * x + 3
            x += 1
        else:
            d += 2 * (x - y) + 5
            x += 1
            y -= 1
        draw_circle_points(x, y, cx, cy)

def draw_circle(radius, cx, cy):
    glBegin(GL_POINTS)
    midpoint_circle(radius, cx, cy)
    glEnd()

def draw_filled_rect(x, y, width, height):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

# --- RETRO HOME PAGE & TEXT FUNCTIONS ---

def draw_retro_text(text_to_draw, x_start, y_start, size=5, centered=False):
    FONT = {
        'A': [0x7e, 0x09, 0x09, 0x09, 0x7e], 'B': [0x7f, 0x49, 0x49, 0x49, 0x36],
        'C': [0x3e, 0x41, 0x41, 0x41, 0x22], 'D': [0x7f, 0x41, 0x41, 0x22, 0x1c],
        'E': [0x7f, 0x49, 0x49, 0x49, 0x41], 'F': [0x7f, 0x09, 0x09, 0x01, 0x01],
        'G': [0x3e, 0x41, 0x41, 0x51, 0x32], 'H': [0x7f, 0x08, 0x08, 0x08, 0x7f],
        'I': [0x00, 0x41, 0x7f, 0x41, 0x00], 'J': [0x20, 0x40, 0x41, 0x3f, 0x01],
        'K': [0x7f, 0x08, 0x14, 0x22, 0x41], 'L': [0x7f, 0x40, 0x40, 0x40, 0x40],
        'M': [0x7f, 0x02, 0x0c, 0x02, 0x7f], 'N': [0x7f, 0x04, 0x08, 0x10, 0x7f],
        'O': [0x3e, 0x41, 0x41, 0x41, 0x3e], 'P': [0x7f, 0x09, 0x09, 0x09, 0x06],
        'Q': [0x3e, 0x41, 0x51, 0x21, 0x5e], 'R': [0x7f, 0x09, 0x19, 0x29, 0x46],
        'S': [0x46, 0x49, 0x49, 0x49, 0x31], 'T': [0x01, 0x01, 0x7f, 0x01, 0x01],
        'U': [0x3f, 0x40, 0x40, 0x40, 0x3f], 'V': [0x1f, 0x20, 0x40, 0x20, 0x1f],
        'W': [0x3f, 0x40, 0x38, 0x40, 0x3f], 'X': [0x63, 0x14, 0x08, 0x14, 0x63],
        'Y': [0x07, 0x08, 0x70, 0x08, 0x07], 'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
        '1': [0x00, 0x42, 0x7f, 0x40, 0x00], '2': [0x42, 0x61, 0x51, 0x49, 0x46],
        '3': [0x21, 0x41, 0x45, 0x4b, 0x31], '4': [0x18, 0x14, 0x12, 0x7f, 0x10],
        '5': [0x27, 0x45, 0x45, 0x45, 0x39], '6': [0x3c, 0x4a, 0x49, 0x49, 0x30],
        '7': [0x01, 0x71, 0x09, 0x05, 0x03], '8': [0x36, 0x49, 0x49, 0x49, 0x36],
        '9': [0x06, 0x49, 0x49, 0x29, 0x1e], '0': [0x3e, 0x51, 0x49, 0x45, 0x3e],
        ' ': [0x00, 0x00, 0x00, 0x00, 0x00]
    }
    char_width = 5 * size
    char_height = 7 * size
    if centered:
        text_width = len(text_to_draw) * char_width + (len(text_to_draw) - 1) * size
        x_start = (600 - text_width) // 2
    for i, char in enumerate(text_to_draw.upper()):
        if char in FONT:
            char_map = FONT[char]
            for col, bits in enumerate(char_map):
                for row in range(char_height):
                    if (bits >> row) & 1:
                        draw_filled_rect(x_start + i * (char_width + size) + col * size, y_start + (char_height - row * size), size, size)

def draw_and_update_starfield():
    global stars, pause
    if not pause:
        for star in stars:
            star[1] -= star[2]
            if star[1] < 0:
                star[1] = 600
                star[0] = random.randint(0, 599)
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(2)
    glBegin(GL_POINTS)
    for star in stars:
        if random.random() > 0.05:
            glVertex2f(star[0], star[1])
    glEnd()

def homepage_info():
    global frame_counter
    colors = [(0.0, 1.0, 1.0), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0)]
    current_color = colors[(frame_counter // 20) % len(colors)]
    glColor3f(current_color[0], current_color[1], current_color[2])
    draw_retro_text("DX BALL", 0, 480, 10, centered=True)

    if (frame_counter // 30) % 2 == 0:
        glColor3f(0.0, 1.0, 0.5)
        draw_retro_text("SELECT A LEVEL", 0, 380, 5, centered=True)

    button_width = 150
    button_x_start = (600 - button_width) // 2
    
    glColor3f(0.0, 0.3, 0.8)
    draw_filled_rect(button_x_start, 300, button_width, 40)
    glColor3f(0.9, 0.9, 0.9)
    draw_retro_text("LEVEL 1", 0, 310, 4, centered=True)

    glColor3f(0.0, 0.3, 0.8)
    draw_filled_rect(button_x_start, 230, button_width, 40)
    glColor3f(0.9, 0.9, 0.9)
    draw_retro_text("LEVEL 2", 0, 240, 4, centered=True)

    glColor3f(1.0, 0.0, 0.0)
    draw_line(550, 590, 590, 550)
    draw_line(550, 550, 590, 590)

# --- VISUAL UPGRADE FUNCTIONS FOR GAME LEVELS ---

def draw_cyber_grid():
    glColor4f(0.0, 1.0, 1.0, 0.1)
    glLineWidth(1.0)
    glBegin(GL_LINES)
    for i in range(0, 601, 20):
        glVertex2f(i, 0); glVertex2f(i, 600)
        glVertex2f(0, i); glVertex2f(600, i)
    glEnd()

def draw_enhanced_slider():
    glColor3f(0.0, 1.0, 0.5)
    draw_filled_rect(x1, y1, x4 - x1, y2 - y1)
    glColor3f(1.0, 1.0, 1.0)
    draw_filled_rect(x1 + 2, y2 - 4, x4 - x1 - 4, 2)

def draw_comet_ball():
    for i, pos in enumerate(ball_trail):
        alpha = (i + 1) / (len(ball_trail) + 1)
        glColor4f(1.0, 0.5, 0.31, alpha * 0.5)
        draw_circle(ball_radius * (alpha * 0.8), pos[0], pos[1])
    glColor3f(1.0, 0.5, 0.31)
    draw_circle(ball_radius, ball_x, ball_y)

def draw_3d_block(block, color):
    x0, y0, x1, y1 = block
    width, height = x1 - x0, y1 - y0
    glColor3f(color[0], color[1], color[2])
    draw_filled_rect(x0, y0, width, height)
    glColor3f(color[0] * 1.5, color[1] * 1.5, color[2] * 1.5)
    glBegin(GL_QUADS)
    glVertex2f(x0, y1); glVertex2f(x0 + 3, y1 - 3); glVertex2f(x1 - 3, y1 - 3); glVertex2f(x1, y1)
    glVertex2f(x0, y0); glVertex2f(x0 + 3, y0 + 3); glVertex2f(x0 + 3, y1 - 3); glVertex2f(x0, y1)
    glEnd()
    glColor3f(color[0] * 0.5, color[1] * 0.5, color[2] * 0.5)
    glBegin(GL_QUADS)
    glVertex2f(x0 + 3, y0 + 3); glVertex2f(x1, y0 + 3); glVertex2f(x1, y0); glVertex2f(x0, y0)
    glVertex2f(x1 - 3, y0 + 3); glVertex2f(x1, y0 + 3); glVertex2f(x1, y1); glVertex2f(x1 - 3, y1 - 3)
    glEnd()

# --- NEW STYLIZED ICONS ---

def draw_powerup_icon(x_start, y_start, x_end, speed_offset, type):
    """Draws a specific powerup icon based on type."""
    x_mid = (x_start + x_end) // 2
    y_pos = y_start + speed_offset
    s = 4 # Pixel size for icons

    if type == 'speed_up': # Yellow >>
        glColor3f(1.0, 1.0, 0.0)
        draw_filled_rect(x_mid - s*3, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid - s*2, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid - s*1, y_pos - s*2, s, s)
        draw_filled_rect(x_mid + s*1, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid + s*2, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid + s*3, y_pos - s*2, s, s)
    elif type == 'slow_down': # Blue turtle shell
        glColor3f(0.2, 0.6, 1.0)
        draw_filled_rect(x_mid - s*3, y_pos - s*3, s*6, s)
        draw_filled_rect(x_mid - s*2, y_pos - s*2, s*4, s*3)
        draw_filled_rect(x_mid - s, y_pos, s*2, s)
    elif type == 'slider_smaller': # Red ><
        glColor3f(1.0, 0.2, 0.2)
        draw_filled_rect(x_mid - s*3, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid - s*2, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid - s*1, y_pos - s*2, s, s)
        draw_filled_rect(x_mid + s*2, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid + s*1, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid, y_pos - s*2, s, s)
    elif type == 'slider_bigger': # Green <>
        glColor3f(0.2, 1.0, 0.2)
        draw_filled_rect(x_mid + s*2, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid + s*1, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid, y_pos - s*2, s, s)
        draw_filled_rect(x_mid - s*3, y_pos - s*4, s, s*5)
        draw_filled_rect(x_mid - s*2, y_pos - s*3, s, s*3)
        draw_filled_rect(x_mid - s*1, y_pos - s*2, s, s)

def draw_stylized_game_ui():
    """Draws the new, cooler UI buttons."""
    # Restart Button (Circular Arrow)
    glColor3f(0.0, 1.0, 1.0)
    glLineWidth(3.0)
    draw_circle(15, 35, 570)
    glBegin(GL_TRIANGLES)
    glVertex2f(35, 590); glVertex2f(25, 585); glVertex2f(45, 585)
    glEnd()

    # Exit Button (Thick X)
    glColor3f(1.0, 0.2, 0.2)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex2f(560, 580); glVertex2f(580, 560)
    glVertex2f(560, 560); glVertex2f(580, 580)
    glEnd()
    
    # Pause/Play Button
    glColor3f(1.0, 1.0, 0.0)
    if pause: # Play Icon (Solid Triangle)
        glBegin(GL_TRIANGLES)
        glVertex2f(290, 555); glVertex2f(290, 585); glVertex2f(315, 570)
        glEnd()
    else: # Pause Icon (Solid Bars)
        draw_filled_rect(290, 555, 8, 30)
        draw_filled_rect(305, 555, 8, 30)

# --- GAME LOGIC AND INPUT HANDLERS ---

def reset_game_state():
    global x1, x2, x3, x4, ball_x, ball_y, over, gg, active_blocks, active_blocksfor2
    global bpu1, bpu2, bpu3, bpu4, p_speed1, p_speed2, p_speed3, p_speed4, ball_speed
    x1, x2, x3, x4 = 270, 270, 330, 330
    ball_x, ball_y = 300, 30
    over, gg = False, False
    ball_speed = 1.0
    ball_trail.clear()
    active_blocks = [True] * len(blocks)
    active_blocksfor2 = [True] * len(blocksfor2)
    bpu1, bpu2, bpu3, bpu4 = False, False, False, False
    p_speed1, p_speed2, p_speed3, p_speed4 = 0, 0, 0, 0

def handle_mouse(button, state, x, y):
    global page, pause
    y = 600 - y
    if page == 'home':
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            button_width = 150
            button_x_start = (600 - button_width) // 2
            if button_x_start <= x <= button_x_start + button_width and 300 <= y <= 340:
                page = 'level-1'; reset_game_state()
            elif button_x_start <= x <= button_x_start + button_width and 230 <= y <= 270:
                page = 'level-2'; reset_game_state()
            elif 550 <= x <= 600 and 550 <= y <= 600:
                glutLeaveMainLoop()
    elif page in ['level-1', 'level-2']:
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if 555 <= x <= 585 and 555 <= y <= 585: glutLeaveMainLoop()
            elif 280 <= x <= 320 and 550 <= y <= 590: pause = not pause
            elif 20 <= x <= 50 and 555 <= y <= 585: reset_game_state()

def KeyboardListener(key, x, y):
    global x1, x2, x3, x4
    value = 20
    if not over and not pause:
        if key == b'd' and x3 < 600:
            x1 += value; x2 += value; x3 += value; x4 += value
        elif key == b'a' and x1 > 0:
            x1 -= value; x2 -= value; x3 -= value; x4 -= value

def move_ball():
    global ball_x, ball_y, ball_dx, ball_dy, over, gg
    if pause or over: return
    ball_trail.append((ball_x, ball_y))
    ball_x += ball_dx * 2 * ball_speed
    ball_y += ball_dy * 2 * ball_speed
    if ball_x - ball_radius <= 0 or ball_x + ball_radius >= 600: ball_dx *= -1
    if ball_y + ball_radius >= 600: ball_dy *= -1
    if ball_y - ball_radius <= 0: over, gg = True, True
    if y1 <= ball_y - ball_radius <= y2 and x1 <= ball_x <= x4:
        ball_dy *= -1
    check_collision_with_blocks()

def get_collision_type(ball_x, ball_y, block):
    block_left, block_bottom, block_right, block_top = block
    closest_x = max(block_left, min(ball_x, block_right))
    closest_y = max(block_bottom, min(ball_y, block_top))
    dist_x = ball_x - closest_x
    dist_y = ball_y - closest_y
    if abs(dist_x) < abs(dist_y): return "VERTICAL"
    elif abs(dist_y) < abs(dist_x): return "HORIZONTAL"
    else: return "CORNER"

def check_collision_with_blocks():
    global ball_dx, ball_dy, score, bpu1, bpu2, bpu3, bpu4
    current_blocks = blocks if page == 'level-1' else blocksfor2
    current_active_blocks = active_blocks if page == 'level-1' else active_blocksfor2
    for i in range(len(current_blocks)):
        if current_active_blocks[i]:
            block = current_blocks[i]
            if (ball_x + ball_radius > block[0] and ball_x - ball_radius < block[2] and
                ball_y + ball_radius > block[1] and ball_y - ball_radius < block[3]):
                collision = get_collision_type(ball_x, ball_y, block)
                if collision == "VERTICAL": ball_dy *= -1
                elif collision == "HORIZONTAL": ball_dx *= -1
                else: ball_dx *= -1; ball_dy *= -1
                current_active_blocks[i] = False
                score += 10
                if page == 'level-1':
                    if i == 6: bpu1 = True
                    elif i == 19: bpu2 = True
                    elif i == 31: bpu3 = True
                    elif i == 44: bpu4 = True

def powerup_animation(value):
    global p_speed1, p_speed2, p_speed3, p_speed4, ball_speed, x1, x2, x3, x4, bpu1, bpu2, bpu3, bpu4
    if not pause:
        if bpu1:
            p_speed1 -= 4
            if blocks1[6][1] + p_speed1 < y2 and x1 < blocks1[6][0] < x3: ball_speed *= 1.5; bpu1 = False
        if bpu2:
            p_speed2 -= 4
            if blocks2[7][1] + p_speed2 < y2 and x1 < blocks2[7][0] < x3: ball_speed /= 1.5; bpu2 = False
        if bpu3:
            p_speed3 -= 4
            if blocks3[7][1] + p_speed3 < y2 and x1 < blocks3[7][0] < x3: x1, x2, x3, x4 = x1 + 20, x2 + 20, x3 - 20, x4 - 20; bpu3 = False
        if bpu4:
            p_speed4 -= 4
            if blocks4[8][1] + p_speed4 < y2 and x1 < blocks4[8][0] < x3: x1, x2, x3, x4 = x1 - 20, x2 - 20, x3 + 20, x4 + 20; bpu4 = False
    glutTimerFunc(20, powerup_animation, 0)

# --- UI AND SCREEN DRAWING FUNCTIONS ---

def game_over_text():
    glColor3f(1.0, 0.0, 0.0)
    draw_retro_text("GAME OVER", 0, 260, 10, centered=True)

def iterate():
    glViewport(0, 0, 600, 600)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, 600, 0.0, 600, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global frame_counter
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()

    if page == 'home':
        glClearColor(0.0, 0.0, 0.1, 1.0)
        draw_and_update_starfield()
        homepage_info()
        frame_counter += 1
    
    elif page in ['level-1', 'level-2']:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        draw_cyber_grid()
        draw_stylized_game_ui()
        draw_enhanced_slider()
        draw_comet_ball()
        
        block_colors = [(1.0, 0.2, 0.2), (0.2, 1.0, 0.2), (0.2, 0.2, 1.0), (1.0, 1.0, 0.2)]
        current_blocks = blocks if page == 'level-1' else blocksfor2
        current_active_blocks = active_blocks if page == 'level-1' else active_blocksfor2
        
        for i in range(len(current_blocks)):
            if current_active_blocks[i]:
                row_index = i // 12 if page == 'level-1' else 0
                if page == 'level-2':
                    if i < len(blocks5): row_index = 0
                    elif i < len(blocks5) + len(blocks6): row_index = 1
                    elif i < len(blocks5) + len(blocks6) + len(blocks7): row_index = 2
                    else: row_index = 3
                draw_3d_block(current_blocks[i], block_colors[row_index % len(block_colors)])
        
        if page == 'level-1':
            if bpu1: draw_powerup_icon(blocks1[6][0], blocks1[6][1], blocks1[6][2], p_speed1, 'speed_up')
            if bpu2: draw_powerup_icon(blocks2[7][0], blocks2[7][1], blocks2[7][2], p_speed2, 'slow_down')
            if bpu3: draw_powerup_icon(blocks3[7][0], blocks3[7][1], blocks3[7][2], p_speed3, 'slider_smaller')
            if bpu4: draw_powerup_icon(blocks4[8][0], blocks4[8][1], blocks4[8][2], p_speed4, 'slider_bigger')
        
        if gg:
            game_over_text()
            
        move_ball()

    glutSwapBuffers()

def initialize_stars(num_stars=150):
    global stars
    for _ in range(num_stars):
        x = random.randint(0, 599)
        y = random.randint(0, 599)
        speed = random.choice([0.2, 0.3, 0.5]) 
        stars.append([x, y, speed])

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutInitWindowSize(600, 600)
    glutInitWindowPosition(100, 100)
    wind = glutCreateWindow(b"Retro DX Ball - Final")
    initialize_stars()
    glutDisplayFunc(showScreen)
    glutIdleFunc(showScreen)
    glutMouseFunc(handle_mouse)
    glutKeyboardFunc(KeyboardListener)
    glutTimerFunc(0, powerup_animation, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
