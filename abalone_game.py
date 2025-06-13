import pygame
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
BOARD_CENTER_X = WINDOW_WIDTH // 2
BOARD_CENTER_Y = WINDOW_HEIGHT // 2
HEX_RADIUS = 25
HEX_SPACING = HEX_RADIUS * 1.8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

# Marble colors
PLAYER1_COLOR = BLACK
PLAYER2_COLOR = WHITE
EMPTY_COLOR = LIGHT_GRAY
SELECTED_COLOR = YELLOW
VALID_MOVE_COLOR = GREEN

# Board colours to match the reference image
BOARD_BORDER_COLOR = (60, 40, 20)    # dark brown for edges
BOARD_FILL_COLOR   = (139, 69, 19)   # saddle brown
HOLE_COLOR         = (205, 133, 63)  # light brown for holes
MARBLE_SHADOW_COLOR = (20, 20, 20)

class HexPosition:
    def __init__(self, q, r):
        self.q = q  # Column
        self.r = r  # Row
        self.s = -q - r  # Third coordinate for cube coordinates
    
    def __eq__(self, other):
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __str__(self):
        return f"({self.q}, {self.r})"

class AbaloneGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Abalone")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.board = {}
        self.current_player = 1  # 1 for black, 2 for white
        self.selected_marbles = []
        self.valid_moves = []
        self.scores = {1: 0, 2: 0}  # Marbles pushed off
        self.game_over = False
        self.winner = None
        
        # Initialize board
        self.init_board()
        
        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def init_board(self):
        """Initialize the Abalone board with starting positions"""
        # Create empty board positions
        for r in range(-4, 5):
            for q in range(max(-4, -4-r), min(5, 5-r)):
                pos = HexPosition(q, r)
                self.board[pos] = 0
        
        # Player 1 (Black) - top
        player1_positions = [
            (-4, 4), (-3, 4), (-2, 4), (-1, 4), (0, 4),
            (-3, 3), (-2, 3), (-1, 3), (0, 3), (1, 3),
            (-2, 2), (-1, 2), (0, 2)
        ]
        # Player 2 (White) - bottom
        player2_positions = [
            (0, -2), (1, -2), (2, -2),
            (-1, -3), (0, -3), (1, -3), (2, -3), (3, -3),
            (0, -4), (1, -4), (2, -4), (3, -4), (4, -4)
        ]
        
        for q, r in player1_positions:
            pos = HexPosition(q, r)
            if pos in self.board:
                self.board[pos] = 1
        
        for q, r in player2_positions:
            pos = HexPosition(q, r)
            if pos in self.board:
                self.board[pos] = 2
    
    def hex_to_pixel(self, hex_pos):
        """Convert hex coordinates to pixel coordinates"""
        x = HEX_SPACING * (3/2 * hex_pos.q)
        y = HEX_SPACING * (math.sqrt(3)/2 * hex_pos.q + math.sqrt(3) * hex_pos.r)
        return (BOARD_CENTER_X + x, BOARD_CENTER_Y - y)
    
    def pixel_to_hex(self, x, y):
        """Convert pixel coordinates to hex coordinates"""
        x = (x - BOARD_CENTER_X) / HEX_SPACING
        y = (BOARD_CENTER_Y - y) / HEX_SPACING
        
        q = 2/3 * x
        r = (-1/3 * x + math.sqrt(3)/3 * y)
        return self.hex_round(q, r)
    
    def hex_round(self, q, r):
        """Round fractional hex coordinates to nearest hex"""
        s = -q - r
        
        rq, rr, rs = round(q), round(r), round(s)
        q_diff, r_diff, s_diff = abs(rq-q), abs(rr-r), abs(rs-s)
        
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        
        return HexPosition(rq, rr)
    
    def get_neighbors(self, hex_pos):
        directions = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
        return [HexPosition(hex_pos.q+dq, hex_pos.r+dr)
                for dq, dr in directions
                if HexPosition(hex_pos.q+dq, hex_pos.r+dr) in self.board]
    
    def get_direction(self, from_pos, to_pos):
        return (to_pos.q - from_pos.q, to_pos.r - from_pos.r)
    
    def is_valid_selection(self, positions):
        if not positions:
            return False
        for pos in positions:
            if self.board[pos] != self.current_player:
                return False
        if len(positions) == 1:
            return True
        if len(positions) > 3:
            return False
        if len(positions) == 2:
            return True
        # len == 3
        p1, p2, p3 = positions
        return self.get_direction(p1,p2) == self.get_direction(p2,p3)
    
    def get_valid_moves(self, selected_positions):
        if not selected_positions:
            return []
        moves = []
        directions = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
        for direction in directions:
            if self.can_move_in_direction(selected_positions, direction):
                dests = [HexPosition(p.q+direction[0], p.r+direction[1])
                         for p in selected_positions]
                moves.append(dests)
        return moves
    
    def can_move_in_direction(self, positions, direction):
        dq, dr = direction
        if len(positions) == 1:
            new_pos = HexPosition(positions[0].q + dq, positions[0].r + dr)
            return self.can_move_to_position(positions, [new_pos])
        # multiple marbles
        p1, p2 = positions[0], positions[1]
        marble_direction = self.get_direction(p1, p2)
        is_inline = marble_direction == direction or marble_direction == (-direction[0], -direction[1])
        if is_inline:
            return self.can_push_in_direction(positions, direction)
        else:
            dests = [HexPosition(p.q + dq, p.r + dr) for p in positions]
            return self.can_sidestep_to_positions(dests)
    
    def can_sidestep_to_positions(self, destinations):
        for pos in destinations:
            if pos not in self.board or self.board[pos] != 0:
                return False
        return True
    
    def can_push_in_direction(self, positions, direction):
        dq, dr = direction
        # find front marble
        if direction in [(1,0),(1,-1),(0,-1)]:
            front_pos = max(positions, key=lambda p: (p.q, p.r))
        else:
            front_pos = min(positions, key=lambda p: (p.q, p.r))
        next_pos = HexPosition(front_pos.q+dq, front_pos.r+dr)
        if next_pos not in self.board:
            return False
        if self.board[next_pos] == 0:
            return True
        if self.board[next_pos] == self.current_player:
            return False
        # opponent chain
        opponent_marbles = []
        check_pos = next_pos
        while check_pos in self.board and self.board[check_pos] == (3 - self.current_player):
            opponent_marbles.append(check_pos)
            check_pos = HexPosition(check_pos.q+dq, check_pos.r+dr)
        if len(opponent_marbles) >= len(positions):
            return False
        if check_pos not in self.board:
            return True
        return self.board[check_pos] == 0
    
    def can_move_to_position(self, from_positions, to_positions):
        if len(to_positions) != 1:
            return False
        to_pos = to_positions[0]
        if to_pos not in self.board:
            return False
        if self.board[to_pos] == 0:
            return True
        if self.board[to_pos] == self.current_player:
            return False
        direction = self.get_direction(from_positions[0], to_pos)
        behind_pos = HexPosition(to_pos.q+direction[0], to_pos.r+direction[1])
        if behind_pos not in self.board:
            return True
        return self.board[behind_pos] == 0
    
    def make_move(self, from_positions, to_positions):
        if not to_positions:
            return False
        original = {pos: self.board[pos] for pos in from_positions}
        for pos in from_positions:
            self.board[pos] = 0
        direction = None
        if len(from_positions) == len(to_positions):
            direction = self.get_direction(from_positions[0], to_positions[0])
        # push chain
        for to_pos in to_positions:
            if to_pos in self.board and original.get(to_pos, None) is not None:
                continue
            if to_pos in self.board and self.board[to_pos] != 0:
                pushed = HexPosition(to_pos.q+direction[0], to_pos.r+direction[1])
                if pushed not in self.board:
                    self.scores[self.current_player] += 1
                else:
                    self.board[pushed] = self.board[to_pos]
        # place moving marbles
        for to_pos in to_positions:
            if to_pos in self.board:
                self.board[to_pos] = self.current_player
        # check win
        if self.scores[self.current_player] >= 6:
            self.game_over = True
            self.winner = self.current_player
        self.current_player = 3 - self.current_player
        return True
    
    def handle_click(self, pos):
        if self.game_over:
            return
        hex_pos = self.pixel_to_hex(pos[0], pos[1])
        if hex_pos not in self.board:
            return
        if self.board[hex_pos] == self.current_player:
            if hex_pos in self.selected_marbles:
                self.selected_marbles.remove(hex_pos)
            else:
                test = self.selected_marbles + [hex_pos]
                if self.is_valid_selection(test):
                    self.selected_marbles.append(hex_pos)
                else:
                    self.selected_marbles = [hex_pos]
            self.valid_moves = self.get_valid_moves(self.selected_marbles)
        elif self.selected_marbles:
            for move in self.valid_moves:
                if hex_pos in move:
                    if self.make_move(self.selected_marbles, move):
                        self.selected_marbles = []
                        self.valid_moves = []
                    break
    
    def draw_hexagon(self, surface, center, radius, color, border_color=None, border_width=2):
        points = []
        for i in range(6):
            angle = math.pi/3 * i - math.pi/6
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        pygame.draw.polygon(surface, color, points)
        if border_color:
            pygame.draw.polygon(surface, border_color, points, border_width)

    def draw_board(self):
        # outline and fill
        border_radius = HEX_SPACING * 8.5
        self.draw_hexagon(self.screen, (BOARD_CENTER_X, BOARD_CENTER_Y),
                        border_radius, BOARD_BORDER_COLOR)
        fill_radius = HEX_SPACING * 8
        self.draw_hexagon(self.screen, (BOARD_CENTER_X, BOARD_CENTER_Y),
                        fill_radius, BOARD_FILL_COLOR)

        # holes and marbles
        for hex_pos in self.board:
            pixel = self.hex_to_pixel(hex_pos)
            # hole
            pygame.draw.circle(self.screen, HOLE_COLOR,
                            (int(pixel[0]), int(pixel[1])), HEX_RADIUS-3)
            # shadow
            val = self.board[hex_pos]
            if val != 0:
                pygame.draw.circle(self.screen, MARBLE_SHADOW_COLOR,
                                (int(pixel[0]+2), int(pixel[1]+2)),
                                HEX_RADIUS-7)
            # marble
            if val != 0:
                color = PLAYER1_COLOR if val == 1 else PLAYER2_COLOR
                if hex_pos in self.selected_marbles:
                    pygame.draw.circle(self.screen, SELECTED_COLOR,
                                    (int(pixel[0]), int(pixel[1])),
                                    HEX_RADIUS-2)
                pygame.draw.circle(self.screen, color,
                                (int(pixel[0]), int(pixel[1])),
                                HEX_RADIUS-6)
                pygame.draw.circle(self.screen, BLACK,
                                (int(pixel[0]), int(pixel[1])),
                                HEX_RADIUS-6, 2)

        # valid moves
        for move in self.valid_moves:
            for dest in move:
                if dest in self.board:
                    p = self.hex_to_pixel(dest)
                    pygame.draw.circle(self.screen, VALID_MOVE_COLOR,
                                    (int(p[0]), int(p[1])), 8)
    
    def draw_ui(self):
        # scores (use small font)
        score_text = self.small_font.render(f"Black: {self.scores[1]}  White: {self.scores[2]}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        # current player (use small font)
        player_text = self.small_font.render(
            f"Current Player: {'Black' if self.current_player==1 else 'White'}", True, BLACK)
        self.screen.blit(player_text, (10, 40))
        # game over
        if self.game_over:
            winner_text = self.font.render(
                f"Game Over! {'Black' if self.winner==1 else 'White'} Wins!", True, RED)
            rect = winner_text.get_rect(center=(WINDOW_WIDTH//2, 100))
            self.screen.blit(winner_text, rect)
        # instructions (top right, smaller font, now in black)
        instr = [
            "Click marbles to select (up to 3 in a line)",
            "Click green circles to move",
            "Push 6 opponent marbles off to win!"
        ]
        padding = 20
        for i, line in enumerate(instr):
            txt = self.small_font.render(line, True, BLACK)
            text_rect = txt.get_rect(topright=(WINDOW_WIDTH - padding, padding + i * 22))
            self.screen.blit(txt, text_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.__init__()
            self.screen.fill(GRAY)  # Set background to grey
            self.draw_board()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = AbaloneGame()
    game.run()
