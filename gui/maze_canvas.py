# gui/maze_canvas.py
# 담당: 추민경
# 설명: 미로 그리기, 마우스 편집, 탐색 애니메이션 (MazeCanvas)
# 12주차 전반: draw_maze() 구현
# 12주차 후반: 마우스 편집(set_edit_mode, 클릭/드래그), clear_search() 구현
# 13주차: 탐색 애니메이션(animate, stop_animation) 구현

import tkinter as tk
from core.config import COLORS, CELL_SIZE


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

        # 마우스 편집용 (12주차 후반)
        self.last_pos = None      # 드래그 중 마지막으로 고친 칸
        self.drag_value = None    # 드래그로 칠할 값 (Maze.WALL 또는 Maze.ROAD)
        self.bind("<Button-1>", self.on_click)      # 왼쪽 버튼 누름
        self.bind("<B1-Motion>", self.on_drag)      # 누른 채로 움직임

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

    # ===== [AI 사용] =====
    # AI 종류   : Claude (Anthropic)
    # 사용 목적 : README 5.3장 명세에 맞춘 마우스 편집, clear_search() 구현 (12주차 후반)
    # 사용자    : 추민경
    # 날짜      : 2026-11-25
    # 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
    # =====================
    def paint_cell(self, pos):
        """pos 한 칸만 원래 색으로 다시 칠한다 (다시 그리지 않고 색만 변경)"""
        row, col = pos
        self.itemconfig(self.rects[row][col], fill=self.cell_color(pos))

    def pixel_to_cell(self, x, y):
        """마우스 픽셀 좌표를 (row, col)로 바꾼다. 미로 밖이면 None"""
        row = y // self.cell_size
        col = x // self.cell_size
        pos = (row, col)
        if not self.maze.in_range(pos):
            return None
        return pos

    def set_edit_mode(self, mode):
        """마우스 클릭 시 동작 변경: "wall", "start", "goal" """
        if mode in ("wall", "start", "goal"):
            self.edit_mode = mode

    def on_click(self, event):
        """마우스 왼쪽 버튼을 눌렀을 때: 편집 모드에 따라 벽/출발점/도착점을 바꾼다"""
        if self.maze is None:
            return
        pos = self.pixel_to_cell(event.x, event.y)
        if pos is None:
            return

        # 탐색 결과 색이 남아 있으면 헷갈리므로 먼저 지운다
        self.stop_animation()
        self.clear_search()

        changed = False
        if self.edit_mode == "wall":
            changed = self.maze.toggle_wall(pos)
            if changed:
                row, col = pos
                # 드래그할 때는 처음 클릭해서 바뀐 값(벽 또는 길)으로 계속 칠한다
                self.drag_value = self.maze.grid[row][col]
                self.paint_cell(pos)
        elif self.edit_mode == "start":
            old = self.maze.start
            changed = self.maze.set_start(pos)
            if changed:
                self.paint_cell(old)      # 예전 출발점은 길 색으로
                self.paint_cell(pos)      # 새 출발점은 초록색으로
        elif self.edit_mode == "goal":
            old = self.maze.goal
            changed = self.maze.set_goal(pos)
            if changed:
                self.paint_cell(old)
                self.paint_cell(pos)

        self.last_pos = pos
        if changed and self.on_change is not None:
            self.on_change()

    def on_drag(self, event):
        """마우스를 누른 채로 움직일 때: 벽 모드에서만 지나가는 칸을 칠한다"""
        if self.maze is None or self.edit_mode != "wall":
            return
        if self.drag_value is None:       # 처음 클릭에서 아무것도 안 바뀐 경우
            return
        pos = self.pixel_to_cell(event.x, event.y)
        if pos is None or pos == self.last_pos:
            return                        # 같은 칸 안에서 움직이면 무시
        self.last_pos = pos

        row, col = pos
        # 이미 원하는 값이면 그대로 두고, 다를 때만 toggle_wall로 바꾼다
        if self.maze.grid[row][col] != self.drag_value:
            if self.maze.toggle_wall(pos):
                self.paint_cell(pos)
                if self.on_change is not None:
                    self.on_change()

    def clear_search(self):
        """방문 칸과 경로 색을 지우고 원래 미로 색으로 되돌린다"""
        if self.maze is None:
            return
        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                self.paint_cell((row, col))
    # ===== [AI 사용 끝] =====

    # ===== [AI 사용] =====
    # AI 종류   : Claude (Anthropic)
    # 사용 목적 : README 5.3장 명세에 맞춘 animate(), stop_animation() 구현 (13주차)
    # 사용자    : 윤종하 작성 → 추민경 전달
    # 날짜      : 2026-11-26
    # 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
    # =====================
    def paint_search(self, pos, color):
        """탐색 결과 색으로 한 칸을 칠한다. 출발점과 도착점은 원래 색을 그대로 둔다"""
        if pos == self.maze.start or pos == self.maze.goal:
            return
        row, col = pos
        self.itemconfig(self.rects[row][col], fill=color)

    def animate(self, result, delay_ms, on_done=None):
        """result.visit_order 순서대로 방문 색을 칠하고, 끝나면 result.path를 경로 색으로 칠한다.
        모두 끝나면 on_done()을 호출. time.sleep 대신 self.after 사용 (13주차)"""
        if self.maze is None:
            return
        self.stop_animation()            # 이전 애니메이션이 남아 있으면 먼저 멈춘다

        # 다음 칸을 칠할 때 다시 쓸 값들을 저장해 둔다
        self.anim_result = result
        self.anim_delay = delay_ms
        self.anim_on_done = on_done

        self.visit_step(0)               # 0번째 방문 칸부터 시작

    def visit_step(self, index):
        """visit_order의 index번째 칸을 방문 색으로 칠하고, 다음 칸을 예약한다"""
        visit_order = self.anim_result.visit_order
        if index >= len(visit_order):    # 방문 칸을 다 칠했으면 경로를 칠하고 끝낸다
            self.show_path()
            return

        self.paint_search(visit_order[index], COLORS["visited"])
        # delay_ms 뒤에 visit_step(index + 1)을 실행하도록 예약 (창이 멈추지 않는다)
        self.after_id = self.after(self.anim_delay, self.visit_step, index + 1)

    def show_path(self):
        """최종 경로를 한 번에 칠하고 on_done()을 호출한다.
        (경로를 한 칸씩 천천히 칠하면 탐색이 한 번 더 도는 것처럼 보여서 한 번에 칠한다)"""
        for pos in self.anim_result.path:
            self.paint_search(pos, COLORS["path"])

        self.after_id = None
        if self.anim_on_done is not None:
            self.anim_on_done()

    def stop_animation(self):
        """진행 중인 애니메이션을 멈춘다 (after_cancel) (13주차)"""
        if self.after_id is not None:
            self.after_cancel(self.after_id)   # 예약해 둔 다음 칸 칠하기를 취소
            self.after_id = None
    # ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.maze_canvas
    from core.maze import Maze
    root = tk.Tk()
    root.title("MazeCanvas 테스트")
    grid = [[1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]]
    m = Maze(7, 7, grid=grid, start=(1, 1), goal=(5, 5))
    c = MazeCanvas(root)
    c.pack()
    c.draw_maze(m)
    c.on_change = lambda: print("미로가 바뀜, start:", m.start, "goal:", m.goal)

    # 편집 모드 바꾸기 버튼 (ControlPanel 대신 테스트용)
    for mode in ("wall", "start", "goal"):
        tk.Button(root, text=mode, command=lambda md=mode: c.set_edit_mode(md)).pack(side="left")
    root.mainloop()
