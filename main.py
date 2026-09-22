import pygame

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

import math
import random

import pgzrun

# ------------------------------------------------------------
# Константы (настройки игры)
# ------------------------------------------------------------
TITLE = "Tap-tap"

BACKGROUND_COLOR = (20, 30, 40)

TEXT_COLOR = (220, 220, 220)
SECONDARY_TEXT_COLOR = (200, 200, 200)
HINT_TEXT_COLOR = (180, 180, 200)
HELP_TEXT_COLOR = (160, 160, 180)

WIDTH = 800
HEIGHT = 600

MIN_SPEED = 1.0
MAX_SPEED = 3.0

MIN_CIRCLES = 3
MAX_CIRCLES = 7

GAME_DURATION = 60


class Circle:
    def __init__(self) -> None:
        self.radius = random.randint(15, 35)
        self.color = tuple(random.randint(100, 255) for _ in range(3))

        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = random.randint(self.radius, HEIGHT - self.radius)

        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        angle = random.uniform(0, 2 * math.pi)

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

        self.is_popping = False
        self.pop_progress = 0.0
        self.pop_speed = 0.2

    def __str__(self) -> str:
        return f"Circle: ({self.x}, {self.y}), r={self.radius}, color={self.color}"

    def move(self, multiplier: float, dt: float) -> None:
        if not self.is_popping:
            self.x += self.dx * multiplier * dt * 60
            self.y += self.dy * multiplier * dt * 60

        # Check if the circle collides with screen borders
        if self.x - self.radius < 0:
            self.dx = -self.dx
            self.x = self.radius

        elif self.x + self.radius > WIDTH:
            self.dx = -self.dx
            self.x = WIDTH - self.radius

        if self.y - self.radius < 0:
            self.dy = -self.dy
            self.y = self.radius

        elif self.y + self.radius > HEIGHT:
            self.dy = -self.dy
            self.y = HEIGHT - self.radius

    def update(self, dt: float) -> bool:
        if not self.is_popping:
            return False

        self.pop_progress += self.pop_speed * dt * 60
        return self.pop_progress >= 1

    def is_clicked(self, pos: tuple[float, float]) -> bool:
        mouse_x, mouse_y = pos
        return (
            math.sqrt((mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2) <= self.radius
        )

    def draw(self):
        if not self.is_popping:
            screen.draw.filled_circle((self.x, self.y), self.radius, self.color)
            screen.draw.circle((self.x, self.y), self.radius, (255, 255, 255))
            return

        current_radius = int(self.radius * (1 - self.pop_progress))
        current_radius = max(current_radius, 1)

        screen.draw.filled_circle((self.x, self.y), current_radius, self.color)


class Game:
    def __init__(self) -> None:
        self.setup_game()

    def setup_game(self) -> None:
        start_count = random.randint(MIN_CIRCLES, MAX_CIRCLES)
        self.circles = [self.spawn_circle() for _ in range(start_count)]
        self.score = 0
        self.speed_multiplier = 1.0
        self.time_left = GAME_DURATION
        self.game_over = False

    def spawn_circle(self) -> Circle:
        return Circle()

    def handle_click(self, pos: tuple[float, float]) -> None:
        if self.game_over:
            return

        for c in self.circles:
            if not c.is_popping and c.is_clicked(pos):
                c.is_popping = True
                sounds.pop.play()
                self.score += 1
                self.speed_multiplier = 1 + math.sqrt(self.score) * 0.3
                break

    def update(self, dt: float):
        if self.game_over:
            return

        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            return

        temp = []
        for c in self.circles:
            if c.update(dt):
                temp.append(self.spawn_circle())
            else:
                temp.append(c)
        self.circles = temp

        for c in self.circles:
            c.move(self.speed_multiplier, dt)

    def draw(self):
        screen.fill(BACKGROUND_COLOR)

        if self.game_over:
            screen.draw.text(
                f"Игра окончена! Счёт: {self.score}",
                center=(WIDTH // 2, HEIGHT // 2),
                fontsize=50,
                color=TEXT_COLOR,
            )
            screen.draw.text(
                "R - новая игра | ESC - выход",
                center=(WIDTH // 2, HEIGHT // 2 + 60),
                fontsize=24,
                color=HELP_TEXT_COLOR,
            )
            return

        for circle in self.circles:
            circle.draw()

        screen.draw.text(
            f"Счет: {self.score}",
            topleft=(20, 20),
            fontsize=30,
            color=TEXT_COLOR,
        )

        screen.draw.text(
            f"Скорость: x{self.speed_multiplier:.1f}",
            topright=(WIDTH - 20, 20),
            fontsize=30,
            color=SECONDARY_TEXT_COLOR,
        )

        screen.draw.text(
            "Нажимай левой кнопкой мыши на шарики, чтобы лопать их",
            center=(WIDTH // 2, HEIGHT - 40),
            fontsize=24,
            color=HINT_TEXT_COLOR,
        )

        screen.draw.text(
            "R - новая игра | ESC - выход",
            center=(WIDTH // 2, HEIGHT - 15),
            fontsize=20,
            color=HELP_TEXT_COLOR,
        )

        screen.draw.text(
            f"Время: {int(self.time_left)}",
            midtop=(WIDTH // 2, 20),
            fontsize=30,
            color=TEXT_COLOR,
        )


# ------------------------------------------------------------
# Pygame Zero hooks (функции, которые вызывает движок)
# ------------------------------------------------------------
game = Game()


def update(dt):
    """Pygame Zero вызывает эту функцию каждый кадр."""
    game.update(dt)


def draw():
    """Pygame Zero вызывает эту функцию для отрисовки кадра."""
    game.draw()


def on_mouse_down(pos, button):
    """
    Pygame Zero вызывает эту функцию при клике мышью.

    pos — координаты клика (x, y)
    button — кнопка мыши
    """
    if button == mouse.LEFT:
        game.handle_click(pos)


def on_key_down(key):
    """
    Pygame Zero вызывает эту функцию при нажатии клавиши.

    R — перезапуск
    ESC — выход из игры
    """
    if key == keys.R:
        game.setup_game()
    elif key == keys.ESCAPE:
        exit()


pgzrun.go()
