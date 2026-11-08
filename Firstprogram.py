from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from typing import Final

Point = tuple[int, int]
Direction = tuple[int, int]


@dataclass(frozen=True)
class GameConfig:
    grid_size: int = 20
    cell_size: int = 20
    start_speed_ms: int = 150
    initial_snake: tuple[Point, ...] = ((5, 10), (4, 10), (3, 10))
    initial_direction: Direction = (1, 0)


class SnakeGameState:
    """Pure game logic for snake movement, food placement, and scoring."""

    def __init__(self, config: GameConfig | None = None) -> None:
        self.config = config or GameConfig()
        self.reset()

    def reset(self) -> None:
        self.direction: Direction = self.config.initial_direction
        self.next_direction: Direction = self.config.initial_direction
        self.snake: list[Point] = list(self.config.initial_snake)
        self.food: Point = self.generate_food()
        self.score: int = 0
        self.game_over: bool = False

    def generate_food(self) -> Point:
        available_positions = [
            (x, y)
            for x in range(self.config.grid_size)
            for y in range(self.config.grid_size)
            if (x, y) not in self.snake
        ]
        if not available_positions:
            return (0, 0)
        return random.choice(available_positions)

    def set_direction(self, new_direction: Direction) -> None:
        if self.game_over:
            return

        if self.direction != (0, 0) and new_direction == (-self.direction[0], -self.direction[1]):
            return

        self.next_direction = new_direction

    def update(self) -> None:
        if self.game_over:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= self.config.grid_size
            or new_head[1] < 0
            or new_head[1] >= self.config.grid_size
            or new_head in self.snake[:-1]
        ):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.food = self.generate_food()
        else:
            self.snake.pop()


class SnakeGame:
    """Tkinter UI layer that renders the game state and handles input."""

    DIRECTION_MAP: Final[dict[str, Direction]] = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
        "w": (0, -1),
        "s": (0, 1),
        "a": (-1, 0),
        "d": (1, 0),
    }

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake Game")
        self.root.config(bg="#f3f4f6")
        self.root.resizable(False, False)

        self.state = SnakeGameState()
        self.width = self.state.config.grid_size * self.state.config.cell_size
        self.height = self.state.config.grid_size * self.state.config.cell_size

        self.canvas = tk.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#111827",
            highlightthickness=0,
        )
        self.canvas.pack(padx=10, pady=10)

        self.score_var = tk.StringVar(value="Score: 0")
        self.score_label = tk.Label(
            root,
            textvariable=self.score_var,
            font=("Arial", 14, "bold"),
            bg="#f3f4f6",
            fg="#111827",
        )
        self.score_label.pack(pady=(0, 10))

        self.instructions = tk.Label(
            root,
            text="Arrow keys or WASD to move",
            font=("Arial", 10),
            bg="#f3f4f6",
            fg="#374151",
        )
        self.instructions.pack(pady=(0, 10))

        self.root.bind("<KeyPress>", self.handle_key)
        self.reset_game()

    def reset_game(self) -> None:
        self.state.reset()
        self.score_var.set("Score: 0")
        self.draw()
        self.root.after(self.state.config.start_speed_ms, self.update)

    def handle_key(self, event: tk.Event) -> None:
        key_name = (event.keysym or "").lower()

        if self.state.game_over and key_name in {"r", "return"}:
            self.reset_game()
            return

        if key_name in self.DIRECTION_MAP:
            self.state.set_direction(self.DIRECTION_MAP[key_name])

    def update(self) -> None:
        if self.state.game_over:
            self.draw()
            return

        self.state.update()
        self.score_var.set(f"Score: {self.state.score}")
        self.draw()

        tick_ms = max(60, self.state.config.start_speed_ms - (self.state.score // 10) * 5)
        self.root.after(tick_ms, self.update)

    def draw(self) -> None:
        self.canvas.delete("all")

        for row in range(self.state.config.grid_size):
            for col in range(self.state.config.grid_size):
                x1 = col * self.state.config.cell_size
                y1 = row * self.state.config.cell_size
                x2 = x1 + self.state.config.cell_size
                y2 = y1 + self.state.config.cell_size
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#1f2937",
                    outline="#374151",
                    width=1,
                )

        food_x = self.state.food[0] * self.state.config.cell_size
        food_y = self.state.food[1] * self.state.config.cell_size
        self.canvas.create_oval(
            food_x + 4,
            food_y + 4,
            food_x + self.state.config.cell_size - 4,
            food_y + self.state.config.cell_size - 4,
            fill="#ef4444",
            outline="#b91c1c",
            width=2,
        )

        for index, segment in enumerate(self.state.snake):
            x = segment[0] * self.state.config.cell_size
            y = segment[1] * self.state.config.cell_size
            color = "#22c55e" if index == 0 else "#16a34a"
            self.canvas.create_rectangle(
                x + 1,
                y + 1,
                x + self.state.config.cell_size - 1,
                y + self.state.config.cell_size - 1,
                fill=color,
                outline="#14532d",
                width=2,
            )

        if self.state.game_over:
            self.canvas.create_text(
                self.width / 2,
                self.height / 2,
                text="Game Over\nPress R to restart",
                fill="#f8fafc",
                font=("Arial", 18, "bold"),
                justify="center",
            )


__all__ = ["GameConfig", "SnakeGameState", "SnakeGame"]


if __name__ == "__main__":
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()
 