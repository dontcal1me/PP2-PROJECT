# gui/app.py
# 담당: 윤종하
# 설명: 메인 창(MazeApp). 모든 부품을 만들고 버튼과 기능을 연결한다
# 12주차 후반: 기본 창과 연결 뼈대
# 13주차: 기록 조회 창(RecordWindow) 연결, 탐색 결과 상태 메시지 정리 (그래프는 14주차)

import tkinter as tk
from tkinter import messagebox, simpledialog

from core.config import CELL_SIZE
from core.finder import BFSFinder, DFSFinder
from core.file_manager import FileManager
from core.generator import MazeGenerator
from gui.maze_canvas import MazeCanvas
from gui.control_panel import ControlPanel
from gui.record_window import RecordWindow


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.1장 명세에 맞춘 MazeApp 기본 창, 팀원 파일 완성 전 임시 패널/임시 미로
# 프롬프트  : "리드미를 읽고 12주차 후반 윤종하 코드를 컴퓨터공학과 1학년 대학생 수준으로 작성해줘"
# 사용자    : 윤종하
# 날짜      : 2026-11-25
# 13주차    : 2026-11-26 on_records()를 RecordWindow 연결로 변경, on_search()/on_compare() 상태 메시지 정리
#             (프롬프트: "리드미를 읽고 13주차 윤종하 코딩을 대학생 컴퓨터공학과 1학년 학생의 수준으로 코딩해줘")
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class MazeApp(tk.Tk):
    """메인 창. 미로, 생성기, 파일 관리자, 캔버스, 패널을 만들고 서로 연결한다"""

    def __init__(self):
        """창을 만들고 부품을 배치한 뒤 첫 미로를 보여준다"""
        super().__init__()
        self.title("경로 탐색 알고리즘 학습 시각화 프로그램")

        self.maze = None
        self.record_window = None        # 열려 있는 기록 조회 창 (없으면 None)
        self.file_manager = FileManager()
        self.generator = MazeGenerator()

        # 탐색 애니메이션이 끝났을 때 쓰려고 결과를 저장해 두는 변수
        self.last_result = None          # [BFS]/[DFS] 탐색 결과
        self.compare_dfs_result = None   # [둘 다 비교]에서 BFS 다음에 보여줄 DFS 결과
        self.compare_speed = 0           # [둘 다 비교] 애니메이션 속도

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
        self.panel = ControlPanel(self, callbacks=callbacks)
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
        self.last_result = result        # 애니메이션이 끝난 뒤 on_search_done()에서 쓴다
        self.panel.show_result(result)
        self.panel.set_status(f"{algorithm} 탐색 중...")
        self.canvas.animate(result, self.panel.get_speed(), on_done=self.on_search_done)

    def on_search_done(self):
        """탐색 애니메이션이 끝나면 캔버스가 불러 준다. 결과에 맞는 상태 메시지를 보여준다"""
        result = self.last_result
        if result.path_length == -1:
            self.panel.set_status(f"{result.algorithm}: 도착점까지 가는 길이 없습니다")
        else:
            self.panel.set_status(f"{result.algorithm} 탐색 완료 (경로 {result.path_length}칸)")

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

        # 화면에는 BFS를 먼저 보여주고, 끝나면 on_compare_bfs_done()에서 DFS를 이어서 보여준다
        self.compare_dfs_result = dfs_result
        self.compare_speed = self.panel.get_speed()
        self.panel.set_status("BFS 애니메이션 중...")
        self.canvas.animate(bfs_result, self.compare_speed, on_done=self.on_compare_bfs_done)

    def on_compare_bfs_done(self):
        """[둘 다 비교] BFS 애니메이션이 끝나면 화면을 지우고 DFS 애니메이션을 시작"""
        self.canvas.clear_search()
        self.panel.set_status("DFS 애니메이션 중...")
        self.canvas.animate(self.compare_dfs_result, self.compare_speed,
                            on_done=self.on_compare_done)

    def on_compare_done(self):
        """[둘 다 비교] DFS 애니메이션까지 끝나면 캔버스가 불러 준다"""
        self.panel.set_status("BFS와 DFS 비교 완료")

    def on_edit_mode(self, mode):
        """편집 모드 라디오 버튼: "wall", "start", "goal" """
        self.canvas.set_edit_mode(mode)
        names = {"wall": "벽", "start": "출발점", "goal": "도착점"}
        self.panel.set_status(f"편집 모드: {names[mode]}")

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
        """[기록 보기] records.csv를 읽어 기록 조회 창(RecordWindow)을 연다"""
        try:
            records = self.file_manager.load_records()
        except OSError as e:             # 엑셀로 csv를 열어 둔 경우 등
            messagebox.showerror("기록 읽기 실패", str(e))
            return

        # 이미 열린 창이 있으면 닫고 최신 기록으로 새로 연다 (창이 여러 개 쌓이지 않게)
        if self.record_window is not None and self.record_window.winfo_exists():
            self.record_window.destroy()
        self.record_window = RecordWindow(self, records)
        self.panel.set_status(f"실행 기록 {len(records)}개를 표시합니다")

    def on_graph(self):
        """[그래프] 14주차에 StatsViewer로 만든다"""
        messagebox.showinfo("알림", "통계 그래프는 14주차에 추가됩니다.")
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.app
    MazeApp().mainloop()
