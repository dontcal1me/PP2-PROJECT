# gui/maze_canvas.py
# 담당: 추민경
# 설명: 미로 그리기, 마우스 편집, 탐색 애니메이션 (MazeCanvas)
# 12주차 전반: draw_maze() 구현

import tkinter as tk
from config import COLORS, CELL_SIZE


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.3장 명세에 맞춘 draw_maze() 구현
# 사용자    : 추민경
# 날짜      : 2026-11-21
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class MazeCanvas(tk.Canvas):
    """미로를 그리고, 마우스 편집과 탐색 애니메이션을 담당"""

    def __init__(self, master, cell_size=CELL_SIZE):
        """캔버스를 만들고 그리기에 필요한 값들을 준비한다"""
        super().__init__(master, bg=COLORS["road"], highlightthickness=0)
        self.cell_size = cell_size
        self.maze = None
        self.rects = []           # rects[row][col] = 사각형 id
        self.edit_mode = "wall"   # "wall", "start", "goal"
        self.after_id = None      # 진행 중인 애니메이션 예약 id
        self.on_change = None     # 미로가 편집되면 호출할 함수 (app이 넣어줌)

    def cell_color(self, pos):
        """pos 칸의 원래 색을 돌려준다 (출발점 > 도착점 > 벽 > 길 순서로 확인)"""
        if pos == self.maze.start:
            return COLORS["start"]
        if pos == self.maze.goal:
            return COLORS["goal"]
        if self.maze.is_wall(pos):
            return COLORS["wall"]
        return COLORS["road"]

    def draw_maze(self, maze):
        """maze 전체를 새로 그린다. 칸마다 사각형 id를 self.rects에 저장"""
        self.maze = maze
        self.delete("all")        # 예전에 그린 사각형 모두 지우기
        self.rects = []

        size = self.cell_size
        self.config(width=maze.cols * size, height=maze.rows * size)

        for row in range(maze.rows):
            row_ids = []
            for col in range(maze.cols):
                x1 = col * size
                y1 = row * size
                rect_id = self.create_rectangle(
                    x1, y1, x1 + size, y1 + size,
                    fill=self.cell_color((row, col)),
                    outline="",   # 테두리 선 없이 칸만 칠하기
                )
                row_ids.append(rect_id)
            self.rects.append(row_ids)
# ===== [AI 사용 끝] =====

    def set_edit_mode(self, mode):
        """마우스 클릭 시 동작 변경: "wall", "start", "goal" (12주차 후반)"""
        pass

    def clear_search(self):
        """방문 칸과 경로 색을 지우고 원래 미로 색으로 되돌린다"""
        pass

    def animate(self, result, delay_ms, on_done=None):
        """result.visit_order 순서대로 방문 색을 칠하고, 끝나면 result.path를 경로 색으로 칠한다.
        모두 끝나면 on_done()을 호출. time.sleep 대신 self.after 사용"""
        pass

    def stop_animation(self):
        """진행 중인 애니메이션을 멈춘다 (after_cancel)"""
        pass


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.maze_canvas
    from maze import Maze
    root = tk.Tk()
    root.title("MazeCanvas 테스트")
    grid = [[1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]]
    m = Maze(5, 5, grid=grid, start=(1, 1), goal=(3, 1))
    c = MazeCanvas(root)
    c.pack()
    c.draw_maze(m)
    root.mainloop()