# generator.py
# 담당: 이승식
# 설명: DFS(반복형 백트래킹)로 무작위 미로를 만든다 (README 5.2장 명세)

import random

from core.maze import Maze
from core.config import MIN_SIZE, MAX_SIZE


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.2장 명세에 맞춘 MazeGenerator 구현
# 사용자    : 이승식 
# 날짜      : 2026-11-26
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class MazeGenerator:
    """DFS(반복형 백트래킹)로 미로를 생성"""

    # 2칸씩 이동하는 방향: 상, 우, 하, 좌
    JUMPS = [(-2, 0), (0, 2), (2, 0), (0, -2)]

    def __init__(self, seed=None):
        self.seed = seed

    def check_size(self, rows, cols):
        """크기가 올바른지 검사한다. 잘못되면 ValueError를 발생시킨다"""
        if rows % 2 == 0 or cols % 2 == 0:
            raise ValueError("미로 크기는 홀수여야 합니다.")
        if rows < MIN_SIZE or rows > MAX_SIZE or cols < MIN_SIZE or cols > MAX_SIZE:
            raise ValueError(f"미로 크기는 {MIN_SIZE} 이상 {MAX_SIZE} 이하여야 합니다.")

    def find_unvisited(self, maze, pos):
        """pos에서 2칸 떨어진 칸 중 미로 안쪽이면서 아직 벽인 칸들의 list"""
        row, col = pos
        result = []
        for dr, dc in MazeGenerator.JUMPS:
            next_row = row + dr
            next_col = col + dc
            # 테두리(0번, 마지막 줄)는 항상 벽으로 남겨야 하므로 안쪽만 본다
            if 1 <= next_row <= maze.rows - 2 and 1 <= next_col <= maze.cols - 2:
                if maze.grid[next_row][next_col] == Maze.WALL:
                    result.append((next_row, next_col))
        return result

    def generate(self, rows, cols, seed=None):
        """rows x cols 크기의 Maze를 만들어 반환.
        rows, cols가 짝수이거나 범위를 벗어나면 ValueError.
        seed가 같으면 항상 같은 미로가 나와야 한다."""
        self.check_size(rows, cols)

        # seed를 안 주면 생성기를 만들 때 받은 seed를 쓴다
        if seed is None:
            seed = self.seed

        # 1. 모든 칸이 벽인 미로를 만든다
        maze = Maze(rows, cols, seed=seed)

        # 2. 이 미로 전용 난수 생성기 (random.seed()는 다른 코드에도 영향을 주므로 쓰지 않는다)
        rng = random.Random(seed)

        # 3. 출발 칸을 길로 만들고 스택에 넣는다
        start = (1, 1)
        maze.grid[1][1] = Maze.ROAD
        stack = [start]

        # 7. 스택이 빌 때까지 반복
        while len(stack) > 0:
            current = stack[-1]                       # 스택 맨 위 칸
            candidates = self.find_unvisited(maze, current)   # 4. 갈 수 있는 칸 찾기

            if len(candidates) > 0:
                # 5. 하나를 무작위로 골라 사이 칸과 그 칸을 길로 만든다
                next_pos = rng.choice(candidates)
                middle_row = (current[0] + next_pos[0]) // 2
                middle_col = (current[1] + next_pos[1]) // 2
                maze.grid[middle_row][middle_col] = Maze.ROAD
                maze.grid[next_pos[0]][next_pos[1]] = Maze.ROAD
                stack.append(next_pos)
            else:
                # 6. 더 갈 곳이 없으면 되돌아간다
                stack.pop()

        maze.start = start
        maze.goal = (rows - 2, cols - 2)
        return maze
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m core.generator
    gen = MazeGenerator()
    m = gen.generate(11, 11, seed=1)
    for row in m.grid:
        print("".join("#" if c == 1 else " " for c in row))
    print(m.neighbors((1, 1)))
    print(m.to_dict()["start"])

    # 같은 seed면 같은 미로인지 확인
    a = gen.generate(21, 21, seed=7)
    b = gen.generate(21, 21, seed=7)
    print("같은 seed 같은 미로:", a.grid == b.grid)        # True

    # 잘못된 크기는 ValueError
    try:
        gen.generate(10, 11)
    except ValueError as e:
        print("짝수 크기 오류:", e)
