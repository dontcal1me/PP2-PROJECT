# gui/app.py
# 담당: 윤종하
# 설명: 메인 창(MazeApp). 모든 부품을 만들고 버튼과 기능을 연결한다
# 12주차 후반: 기본 창과 연결 뼈대 (기록 조회 창, 그래프는 13~14주차)

import tkinter as tk
from tkinter import messagebox, simpledialog

from core.config import CELL_SIZE, DEFAULT_SIZE, DEFAULT_SPEED_MS
from core.maze import Maze
from core.finder import BFSFinder, DFSFinder
from core.file_manager import FileManager
from gui.maze_canvas import MazeCanvas

# 팀원 파일이 아직 완성되지 않았어도 창이 뜨도록 한다.
# 완성되어 main에 올라오면 자동으로 진짜 클래스를 쓴다.
try:
    from core.generator import MazeGenerator          # 이승식
except ImportError:
    MazeGenerator = None

try:
    from gui.control_panel import ControlPanel   # 추민경
except ImportError:
    ControlPanel = None


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.1장 명세에 맞춘 MazeApp 기본 창, 팀원 파일 완성 전 임시 패널/임시 미로
# 프롬프트  : "리드미를 읽고 12주차 후반 윤종하 코드를 컴퓨터공학과 1학년 대학생 수준으로 작성해줘"
# 사용자    : 윤종하
# 날짜      : 2026-11-25
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
def make_sample_maze(size=DEFAULT_SIZE):
    """generator.py가 완성되기 전에 테스트용으로 쓰는 지그재그 미로"""
    maze = Maze(size, size, name="sample")
    # 테두리를 뺀 안쪽을 모두 길로 만든다
    for row in range(1, size - 1):
        for col in range(1, size - 1):
            maze.grid[row][col] = Maze.ROAD
    # 4칸마다 세로 벽을 세우고, 아래/위를 번갈아 한 칸씩 뚫는다
    count = 0
    for col in range(2, size - 2, 4):
        for row in range(1, size - 1):
            maze.grid[row][col] = Maze.WALL
        if count % 2 == 0:
            maze.grid[size - 2][col] = Maze.ROAD   # 아래쪽 구멍
        else:
            maze.grid[1][col] = Maze.ROAD          # 위쪽 구멍
        count += 1
    return maze


class TempPanel(tk.Frame):
    """ControlPanel(추민경)이 완성되기 전까지 쓰는 임시 패널. 같은 이름의 메서드만 흉내 낸다"""

    def __init__(self, master, callbacks):
        """버튼 몇 개와 결과/상태 글자를 만든다"""
        super().__init__(master)
        self.callbacks = callbacks

        tk.Label(self, text="[임시 패널]").pack(pady=5)
        tk.Button(self, text="미로 생성", width=14,
                  command=callbacks["generate"]).pack(pady=2)
        tk.Button(self, text="BFS 탐색", width=14,
                  command=lambda: callbacks["search"]("BFS")).pack(pady=2)
        tk.Button(self, text="DFS 탐색", width=14,
                  command=lambda: callbacks["search"]("DFS")).pack(pady=2)
        tk.Button(self, text="둘 다 비교", width=14,
                  command=callbacks["compare"]).pack(pady=2)
        tk.Button(self, text="미로 저장", width=14,
                  command=callbacks["save"]).pack(pady=2)
        tk.Button(self, text="미로 불러오기", width=14,
                  command=callbacks["load"]).pack(pady=2)
        tk.Button(self, text="기록 보기", width=14,
                  command=callbacks["records"]).pack(pady=2)

        self.result_label = tk.Label(self, text="", justify="left")
        self.result_label.pack(pady=10)
        self.status_label = tk.Label(self, text="상태: 준비")
        self.status_label.pack(side="bottom", pady=5)

    def get_size(self):
        """임시 패널은 입력칸이 없으므로 기본 크기를 돌려준다"""
        return (DEFAULT_SIZE, DEFAULT_SIZE)

    def get_seed(self):
        """임시 패널은 시드 입력이 없으므로 None"""
        return None

    def get_speed(self):
        """기본 애니메이션 간격"""
        return DEFAULT_SPEED_MS

    def show_result(self, result):
        """SearchResult 하나를 글자로 표시"""
        text = (f"{result.algorithm}\n"
                f"방문: {result.visited_count}\n"
                f"경로: {result.path_length}\n"
                f"시간: {result.elapsed_ms:.2f} ms")
        self.result_label.config(text=text)

    def show_compare(self, bfs_result, dfs_result):
        """두 결과를 나란히 표시"""
        text = (f"       BFS   DFS\n"
                f"방문  {bfs_result.visited_count:4}  {dfs_result.visited_count:4}\n"
                f"경로  {bfs_result.path_length:4}  {dfs_result.path_length:4}")
        self.result_label.config(text=text)

    def set_status(self, text):
        """상태 글자 변경"""
        self.status_label.config(text="상태: " + text)


class MazeApp(tk.Tk):
    """메인 창. 미로, 생성기, 파일 관리자, 캔버스, 패널을 만들고 서로 연결한다"""

    def __init__(self):
        """창을 만들고 부품을 배치한 뒤 첫 미로를 보여준다"""
        super().__init__()
        self.title("경로 탐색 알고리즘 학습 시각화 프로그램")

        self.maze = None
        self.file_manager = FileManager()
        if MazeGenerator is not None:
            self.generator = MazeGenerator()
        else:
            self.generator = None

        # 탐색 알고리즘은 이름으로 찾아 쓸 수 있게 dict에 넣어 둔다
        self.finders = {"BFS": BFSFinder(), "DFS": DFSFinder()}

        # 왼쪽: 미로 캔버스
        self.canvas = MazeCanvas(self, cell_size=CELL_SIZE)
        self.canvas.on_change = self.on_maze_changed
        self.canvas.pack(side="left", padx=10, pady=10)

        # 오른쪽: 조작 패널
        callbacks = {
            "generate": self.on_generate,
            "search": self.on_search,       # 인자: "BFS" 또는 "DFS"
            "compare": self.on_compare,
            "edit_mode": self.on_edit_mode, # 인자: "wall", "start", "goal"
            "save": self.on_save,
            "load": self.on_load,
            "records": self.on_records,
            "graph": self.on_graph,
        }
        if ControlPanel is not None:
            self.panel = ControlPanel(self, callbacks=callbacks)
        else:
            self.panel = TempPanel(self, callbacks=callbacks)
        self.panel.pack(side="right", fill="y", padx=10, pady=10)

        # 처음 켰을 때 미로 하나를 보여준다
        self.on_generate()

    def show_maze(self, maze):
        """새 미로를 저장하고 화면에 그린다"""
        self.canvas.stop_animation()
        self.maze = maze
        self.canvas.draw_maze(maze)

    # ---------- 버튼에 연결되는 함수들 ----------

    def on_generate(self):
        """[미로 생성] 패널의 크기와 시드로 새 미로를 만든다"""
        if self.generator is None:
            self.show_maze(make_sample_maze())
            self.panel.set_status("generator.py 완성 전이라 예시 미로를 표시합니다")
            return

        size = self.panel.get_size()
        if size is None:                 # 잘못된 크기 (패널이 이미 알림)
            return
        rows, cols = size
        seed = self.panel.get_seed()

        try:
            maze = self.generator.generate(rows, cols, seed)
        except ValueError as e:
            messagebox.showerror("미로 생성 실패", str(e))
            return

        maze.name = f"maze_{rows}x{cols}"
        if seed is not None:
            maze.name += f"_{seed}"
        self.show_maze(maze)
        self.panel.set_status(f"{rows} x {cols} 미로를 만들었습니다")

    def run_search(self, algorithm):
        """algorithm("BFS"/"DFS")으로 탐색하고 기록 파일에 저장한 뒤 결과를 돌려준다"""
        result = self.finders[algorithm].find(self.maze)
        try:
            self.file_manager.append_record(result, self.maze)
        except OSError as e:             # 엑셀로 csv를 열어 둔 경우 등
            messagebox.showwarning("기록 저장 실패", str(e))
        return result

    def on_search(self, algorithm):
        """[BFS 탐색] / [DFS 탐색] 버튼"""
        if self.maze is None:
            messagebox.showinfo("알림", "먼저 미로를 만들어 주세요.")
            return

        self.canvas.stop_animation()     # 이전 애니메이션이 있으면 멈춘다
        self.canvas.clear_search()

        result = self.run_search(algorithm)
        self.panel.show_result(result)
        self.panel.set_status(f"{algorithm} 탐색 중...")
        self.canvas.animate(result, self.panel.get_speed(),
                            on_done=lambda: self.panel.set_status(f"{algorithm} 탐색 완료"))

        if result.path_length == -1:
            self.panel.set_status("도착점까지 가는 길이 없습니다")

    def on_compare(self):
        """[둘 다 비교] BFS와 DFS를 모두 돌리고 결과를 나란히 보여준다"""
        if self.maze is None:
            messagebox.showinfo("알림", "먼저 미로를 만들어 주세요.")
            return

        self.canvas.stop_animation()
        self.canvas.clear_search()

        bfs_result = self.run_search("BFS")
        dfs_result = self.run_search("DFS")
        self.panel.show_compare(bfs_result, dfs_result)
        self.panel.set_status("BFS와 DFS를 비교했습니다")

        # 화면에는 BFS를 먼저 보여주고, 끝나면 DFS를 이어서 보여준다
        speed = self.panel.get_speed()

        def show_dfs():
            """BFS 애니메이션이 끝나면 화면을 지우고 DFS 애니메이션을 시작"""
            self.canvas.clear_search()
            self.canvas.animate(dfs_result, speed)

        self.canvas.animate(bfs_result, speed, on_done=show_dfs)

    def on_edit_mode(self, mode):
        """편집 모드 라디오 버튼: "wall", "start", "goal" """
        self.canvas.set_edit_mode(mode)
        names = {"wall": "벽", "start": "출발점", "goal": "도착점"}
        self.panel.set_status(f"편집 모드: {names.get(mode, mode)}")

    def on_maze_changed(self):
        """캔버스에서 마우스로 미로를 고쳤을 때 캔버스가 불러 준다"""
        self.panel.set_status("미로가 수정되었습니다")

    def on_save(self):
        """[미로 저장] 이름을 입력받아 json으로 저장"""
        if self.maze is None:
            messagebox.showinfo("알림", "저장할 미로가 없습니다.")
            return

        name = simpledialog.askstring("미로 저장", "저장할 이름:",
                                      initialvalue=self.maze.name, parent=self)
        if not name:                     # 취소하거나 빈 칸
            return

        if name in self.file_manager.list_mazes():
            if not messagebox.askyesno("덮어쓰기", f"'{name}'이(가) 이미 있습니다. 덮어쓸까요?"):
                return

        try:
            self.maze.name = name
            path = self.file_manager.save_maze(self.maze, name)
        except (ValueError, OSError) as e:
            messagebox.showerror("저장 실패", str(e))
            return
        self.panel.set_status(f"저장 완료: {path}")

    def on_load(self):
        """[미로 불러오기] 저장된 이름 목록을 보여주고 하나를 불러온다"""
        names = self.file_manager.list_mazes()
        if len(names) == 0:
            messagebox.showinfo("알림", "저장된 미로가 없습니다.")
            return

        name = simpledialog.askstring("미로 불러오기",
                                      "불러올 이름을 입력하세요:\n" + "\n".join(names),
                                      parent=self)
        if not name:
            return

        try:
            maze = self.file_manager.load_maze(name)
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("불러오기 실패", str(e))
            return
        self.show_maze(maze)
        self.panel.set_status(f"불러옴: {name}")

    def on_records(self):
        """[기록 보기] 기록 조회 창은 13주차에 RecordWindow로 만든다. 지금은 개수만 알려준다"""
        records = self.file_manager.load_records()
        messagebox.showinfo("실행 기록", f"저장된 기록: {len(records)}개\n(기록 조회 창은 13주차 예정)")

    def on_graph(self):
        """[그래프] 14주차에 StatsViewer로 만든다"""
        messagebox.showinfo("알림", "통계 그래프는 14주차에 추가됩니다.")
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.app
    MazeApp().mainloop()
