# gui/control_panel.py
# 담당: 추민경
# 설명: 오른쪽 조작 패널 (버튼, 입력칸, 결과 표시, 상태 표시줄)
# 12주차 후반: ControlPanel 전체 구현

import tkinter as tk
from tkinter import messagebox
from core.config import DEFAULT_SIZE, MIN_SIZE, MAX_SIZE, DEFAULT_SPEED_MS


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.3장, 8장 화면 구성에 맞춘 ControlPanel 구현
# 사용자    : 추민경
# 날짜      : 2026-11-25
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class ControlPanel(tk.Frame):
    """오른쪽 조작 패널. 버튼이 눌리면 app이 넘겨준 callbacks의 함수를 호출만 한다"""

    def __init__(self, master, callbacks):
        """패널 안의 버튼, 입력칸, 결과 표를 만든다"""
        super().__init__(master)
        self.callbacks = callbacks

        self.make_maze_frame()
        self.make_edit_frame()
        self.make_search_frame()
        self.make_result_frame()
        self.make_bottom_frame()

    # ---------- 화면 만들기 ----------

    def make_maze_frame(self):
        """[미로 설정] 크기, 시드 입력칸과 생성 버튼"""
        frame = tk.LabelFrame(self, text="미로 설정", padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text="크기:").grid(row=0, column=0, sticky="w")
        self.rows_entry = tk.Entry(frame, width=5)
        self.rows_entry.insert(0, str(DEFAULT_SIZE))
        self.rows_entry.grid(row=0, column=1)
        tk.Label(frame, text="x").grid(row=0, column=2)
        self.cols_entry = tk.Entry(frame, width=5)
        self.cols_entry.insert(0, str(DEFAULT_SIZE))
        self.cols_entry.grid(row=0, column=3)

        tk.Label(frame, text="시드:").grid(row=1, column=0, sticky="w")
        self.seed_entry = tk.Entry(frame, width=13)
        self.seed_entry.grid(row=1, column=1, columnspan=3, sticky="w")

        tk.Button(frame, text="미로 생성", width=18,
                  command=self.callbacks["generate"]).grid(row=2, column=0, columnspan=4, pady=5)

    def make_edit_frame(self):
        """[편집 모드] 벽 / 출발 / 도착 라디오 버튼"""
        frame = tk.LabelFrame(self, text="편집 모드", padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        self.mode_var = tk.StringVar(value="wall")
        modes = [("벽", "wall"), ("출발", "start"), ("도착", "goal")]
        for i in range(len(modes)):
            text, value = modes[i]
            tk.Radiobutton(frame, text=text, value=value, variable=self.mode_var,
                           command=self.on_mode_changed).grid(row=0, column=i, sticky="w")

    def make_search_frame(self):
        """[탐색] BFS, DFS, 비교 버튼과 속도 슬라이더"""
        frame = tk.LabelFrame(self, text="탐색", padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        tk.Button(frame, text="BFS", width=8,
                  command=lambda: self.callbacks["search"]("BFS")).grid(row=0, column=0, padx=2)
        tk.Button(frame, text="DFS", width=8,
                  command=lambda: self.callbacks["search"]("DFS")).grid(row=0, column=1, padx=2)
        tk.Button(frame, text="둘 다 비교", width=18,
                  command=self.callbacks["compare"]).grid(row=1, column=0, columnspan=2, pady=5)

        # 슬라이더 값 = 한 칸 칠하는 간격(ms). 작을수록 빠르다
        self.speed_scale = tk.Scale(frame, from_=5, to=200, orient="horizontal",
                                    label="간격(ms) 작을수록 빠름", length=160)
        self.speed_scale.set(DEFAULT_SPEED_MS)
        self.speed_scale.grid(row=2, column=0, columnspan=2)

    def make_result_frame(self):
        """[결과] 방문/경로/시간을 BFS, DFS 두 줄로 보여주는 작은 표"""
        frame = tk.LabelFrame(self, text="결과", padx=5, pady=5)
        frame.pack(fill="x", pady=5)

        tk.Label(frame, text="").grid(row=0, column=0)
        tk.Label(frame, text="BFS", width=8).grid(row=0, column=1)
        tk.Label(frame, text="DFS", width=8).grid(row=0, column=2)

        # result_labels["BFS"]["visited"] 처럼 꺼내 쓸 수 있게 dict로 저장
        self.result_labels = {"BFS": {}, "DFS": {}}
        items = [("방문", "visited"), ("경로", "path"), ("시간", "time")]
        for i in range(len(items)):
            text, key = items[i]
            tk.Label(frame, text=text).grid(row=i + 1, column=0, sticky="w")
            for j, algorithm in enumerate(["BFS", "DFS"]):
                label = tk.Label(frame, text="-", width=8)
                label.grid(row=i + 1, column=j + 1)
                self.result_labels[algorithm][key] = label

    def make_bottom_frame(self):
        """아래쪽: 저장, 불러오기, 기록, 그래프 버튼과 상태 표시줄"""
        frame = tk.Frame(self)
        frame.pack(side="bottom", fill="x", pady=5)

        tk.Button(frame, text="미로 저장", width=9,
                  command=self.callbacks["save"]).grid(row=0, column=0, padx=2, pady=2)
        tk.Button(frame, text="불러오기", width=9,
                  command=self.callbacks["load"]).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(frame, text="기록 보기", width=9,
                  command=self.callbacks["records"]).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(frame, text="그래프", width=9,
                  command=self.callbacks["graph"]).grid(row=1, column=1, padx=2, pady=2)

        self.status_label = tk.Label(frame, text="상태: 준비", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

    def on_mode_changed(self):
        """라디오 버튼이 바뀌면 app에 알려준다"""
        self.callbacks["edit_mode"](self.mode_var.get())

    # ---------- app이 부르는 메서드 (README 5.3장 이름 그대로) ----------

    def get_size(self):
        """입력된 (rows, cols) 반환. 잘못된 값이면 messagebox로 알리고 None"""
        try:
            rows = int(self.rows_entry.get())
            cols = int(self.cols_entry.get())
        except ValueError:
            messagebox.showerror("입력 오류", "크기에는 숫자만 입력하세요.")
            return None

        for n in (rows, cols):
            if n < MIN_SIZE or n > MAX_SIZE or n % 2 == 0:
                messagebox.showerror("입력 오류",
                                     f"크기는 {MIN_SIZE}~{MAX_SIZE} 사이의 홀수여야 합니다.")
                return None
        return (rows, cols)

    def get_seed(self):
        """입력된 시드(int) 반환. 비어 있으면 None"""
        text = self.seed_entry.get().strip()
        if text == "":
            return None
        try:
            return int(text)
        except ValueError:
            messagebox.showwarning("입력 오류", "시드는 정수만 됩니다. 시드 없이 만듭니다.")
            self.seed_entry.delete(0, tk.END)
            return None

    def get_speed(self):
        """슬라이더 값으로 애니메이션 간격(ms) 반환"""
        return int(self.speed_scale.get())

    def fill_column(self, algorithm, result):
        """결과 표에서 algorithm("BFS"/"DFS") 칸에 result 값을 채운다. result가 None이면 '-'"""
        labels = self.result_labels[algorithm]
        if result is None:
            labels["visited"].config(text="-")
            labels["path"].config(text="-")
            labels["time"].config(text="-")
            return

        labels["visited"].config(text=str(result.visited_count))
        if result.path_length == -1:
            labels["path"].config(text="없음")
        else:
            labels["path"].config(text=str(result.path_length))
        labels["time"].config(text=f"{result.elapsed_ms:.2f}ms")

    def show_result(self, result):
        """SearchResult 하나를 결과 칸에 표시"""
        if result.algorithm == "BFS":
            self.fill_column("BFS", result)
            self.fill_column("DFS", None)
        else:
            self.fill_column("BFS", None)
            self.fill_column("DFS", result)

    def show_compare(self, bfs_result, dfs_result):
        """두 결과를 나란히 표시"""
        self.fill_column("BFS", bfs_result)
        self.fill_column("DFS", dfs_result)

    def set_status(self, text):
        """아래 상태 표시줄 글자 변경"""
        self.status_label.config(text="상태: " + text)
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.control_panel
    root = tk.Tk()
    root.title("ControlPanel 테스트")

    def make_printer(name):
        """버튼이 눌리면 이름과 인자를 출력하는 가짜 함수를 만든다"""
        def printer(*args):
            print(name, args)
        return printer

    names = ["generate", "search", "compare", "edit_mode",
             "save", "load", "records", "graph"]
    callbacks = {}
    for name in names:
        callbacks[name] = make_printer(name)

    panel = ControlPanel(root, callbacks)
    panel.pack(padx=10, pady=10)

    # 결과 표시 확인용 가짜 결과
    class Fake:
        algorithm = "BFS"; visited_count = 187; path_length = 64; elapsed_ms = 0.42

    tk.Button(root, text="크기/시드/속도 출력",
              command=lambda: print(panel.get_size(), panel.get_seed(), panel.get_speed())).pack()
    tk.Button(root, text="결과 표시 테스트",
              command=lambda: panel.show_result(Fake())).pack()
    root.mainloop()
