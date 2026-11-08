import unittest

from Firstprogram import GameConfig, SnakeGameState


class SnakeGameStateTests(unittest.TestCase):
    def test_initial_game_state(self):
        state = SnakeGameState(GameConfig())
        self.assertEqual(state.snake, [(5, 10), (4, 10), (3, 10)])
        self.assertEqual(state.direction, (1, 0))
        self.assertFalse(state.game_over)
        self.assertEqual(state.score, 0)

    def test_food_collision_increases_score_and_length(self):
        state = SnakeGameState(GameConfig())
        state.food = (6, 10)
        state.update()

        self.assertEqual(state.snake[0], (6, 10))
        self.assertEqual(state.score, 10)
        self.assertEqual(len(state.snake), 4)

    def test_reverse_direction_is_blocked(self):
        state = SnakeGameState(GameConfig())
        state.set_direction((-1, 0))

        self.assertEqual(state.next_direction, (1, 0))

    def test_wall_collision_sets_game_over(self):
        state = SnakeGameState(GameConfig())
        state.snake = [(0, 5), (1, 5), (2, 5)]
        state.direction = (-1, 0)
        state.next_direction = (-1, 0)
        state.update()

        self.assertTrue(state.game_over)


if __name__ == "__main__":
    unittest.main()
