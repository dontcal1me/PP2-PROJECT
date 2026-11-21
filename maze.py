# maze.py
# 담당: 이승식
# 설명: 미로 한 개의 데이터와 기본 동작 (좌표는 (row, col) tuple)
# 12주차 과제에서 구현한 Maze 클래스의 메서드들을 README 5.2장 명세에 맞춰 완성하고, to_dict()와 from_dict() 메서드를 추가함

from datetime import datetime


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.2장 명세에 맞춘 Maze 클래스 메서드 구현
# 사용자    : 이승식
# 날짜      : 2026-11-21
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class Maze:
    """미로 한 개의 데이터와 기본 동작"""
    ROAD = 0
    WALL = 1
    DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]   # 상, 우, 하, 좌

    def __init__(self, rows, cols, grid=None, start=(1, 1), goal=None,
                 name="untitled", seed=None):
        """rows x cols 크기의 미로를 만든다. grid가 없으면 전부 벽으로 채운다"""
        self.rows = rows
        self.cols = cols
        self.grid = grid if grid is not None else [[Maze.WALL] * cols for _ in range(rows)]
        self.start = start
        self.goal = goal if goal is not None else (rows - 2, cols - 2)
        self.name = name
        self.seed = seed
        self.created_at = None   # 불러온 미로면 저장 시각, 새 미로면 None

    def in_range(self, pos):
        """pos가 미로 안쪽이면 True"""
        row, col = pos
        return 0 <= row < self.rows and 0 <= col < self.cols

    def is_wall(self, pos):
        """pos가 벽이면 True. 범위 밖도 벽으로 취급"""
        if not self.in_range(pos):
            return True
        row, col = pos
        return self.grid[row][col] == Maze.WALL

    def is_border(self, pos):
        """pos가 미로의 바깥 테두리 칸이면 True"""
        row, col = pos
        return row == 0 or col == 0 or row == self.rows - 1 or col == self.cols - 1

    def neighbors(self, pos):
        """pos에서 이동할 수 있는 상하좌우 칸의 list. DIRECTIONS 순서를 지킨다"""
        row, col = pos
        result = []
        for dr, dc in Maze.DIRECTIONS:
            next_pos = (row + dr, col + dc)
            if not self.is_wall(next_pos):
                result.append(next_pos)
        return result

    def toggle_wall(self, pos):
        """벽이면 길로, 길이면 벽으로 바꾼다. 출발점, 도착점, 테두리는 바꾸지 않는다.
        바꿨으면 True, 바꾸지 않았으면 False 반환"""
        if not self.in_range(pos) or self.is_border(pos):
            return False
        if pos == self.start or pos == self.goal:
            return False
        row, col = pos
        if self.grid[row][col] == Maze.WALL:
            self.grid[row][col] = Maze.ROAD
        else:
            self.grid[row][col] = Maze.WALL
        return True

    def set_start(self, pos):
        """출발점 변경. 벽이거나 범위 밖이면 바꾸지 않고 False 반환"""
        pos = tuple(pos)
        if self.is_wall(pos) or pos == self.goal:
            return False
        self.start = pos
        return True

    def set_goal(self, pos):
        """도착점 변경. 벽이거나 범위 밖이면 바꾸지 않고 False 반환"""
        pos = tuple(pos)
        if self.is_wall(pos) or pos == self.start:
            return False
        self.goal = pos
        return True

    def to_dict(self):
        """json 저장용 dict로 변환 (7장 형식)"""
        created_at = self.created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "name": self.name,
            "rows": self.rows,
            "cols": self.cols,
            "seed": self.seed,
            "start": list(self.start),
            "goal": list(self.goal),
            "grid": [row[:] for row in self.grid],   # 원본이 바뀌지 않도록 복사
            "created_at": created_at,
        }

    @classmethod
    def from_dict(cls, data):
        """to_dict()로 만든 dict에서 Maze 객체를 만든다. start, goal은 tuple로 바꾼다"""
        maze = cls(
            rows=data["rows"],
            cols=data["cols"],
            grid=[list(row) for row in data["grid"]],
            start=tuple(data["start"]),
            goal=tuple(data["goal"]),
            name=data.get("name", "untitled"),
            seed=data.get("seed"),
        )
        maze.created_at = data.get("created_at")
        return maze
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    grid = [[1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]]
    m = Maze(5, 5, grid=grid, start=(1, 1), goal=(3, 1), name="test")

    for row in m.grid:
        print("".join("#" if c == Maze.WALL else " " for c in row))

    print("in_range (0,0):", m.in_range((0, 0)))          # True
    print("in_range (5,0):", m.in_range((5, 0)))          # False
    print("is_wall (0,0):", m.is_wall((0, 0)))            # True
    print("is_wall (-1,2):", m.is_wall((-1, 2)))          # True (범위 밖)
    print("neighbors (1,2):", m.neighbors((1, 2)))        # [(1, 3), (1, 1)]
    print("neighbors (1,3):", m.neighbors((1, 3)))        # [(2, 3), (1, 2)]

    print("toggle 테두리:", m.toggle_wall((0, 2)))        # False
    print("toggle 출발점:", m.toggle_wall((1, 1)))        # False
    print("toggle (2,1):", m.toggle_wall((2, 1)), m.grid[2][1])   # True 0
    m.toggle_wall((2, 1))                                  # 원래대로

    print("set_start 벽:", m.set_start((0, 0)))           # False
    print("set_start (1,3):", m.set_start((1, 3)), m.start)      # True (1, 3)
    print("set_goal 범위 밖:", m.set_goal((9, 9)))        # False

    d = m.to_dict()
    m2 = Maze.from_dict(d)
    print("from_dict start:", m2.start, type(m2.start))   # (1, 3) tuple
    print("grid 같음:", m2.grid == m.grid)                # True
    print("기본 goal:", Maze(21, 21).goal)                # (19, 19)
