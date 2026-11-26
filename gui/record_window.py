# gui/record_window.py
# 담당: 윤종하 (류지언 코딩 대행)
# 설명: records.csv 실행 기록을 표(ttk.Treeview)로 보여주는 새 창
# 13주차: RecordWindow 구현

import tkinter as tk
from tkinter import ttk


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.4장 명세에 맞춘 RecordWindow(기록 조회 창) 구현
# 프롬프트  : "리드미를 읽고 13주차 윤종하 코딩을 대학생 컴퓨터공학과 1학년 학생의 수준으로 코딩해줘"
# 사용자    : 윤종하
# 날짜      : 2026-11-26
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class RecordWindow(tk.Toplevel):
    """records.csv 내용을 표(ttk.Treeview)로 보여주는 새 창"""

    # (csv의 key, 표 제목, 칸 너비) 순서대로 표에 표시한다
    COLUMNS = [
        ("datetime", "실행 시각", 140),
        ("maze_name", "미로 이름", 120),
        ("rows", "행", 40),
        ("cols", "열", 40),
        ("algorithm", "알고리즘", 70),
        ("visited_count", "방문 칸", 70),
        ("path_length", "경로 길이", 70),
        ("elapsed_ms", "시간(ms)", 70),
    ]

    def __init__(self, master, records):
        """records: FileManager.load_records()의 결과"""
        super().__init__(master)
        self.title("실행 기록")
        self.geometry("680x400")

        self.make_table()
        self.make_bottom(len(records))
        self.fill_table(records)

    def make_table(self):
        """표와 세로 스크롤바를 만든다"""
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 칸 이름(key)만 모아서 Treeview에 넘긴다
        keys = []
        for key, title, width in RecordWindow.COLUMNS:
            keys.append(key)

        # show="headings": 맨 왼쪽의 빈 트리 칸을 숨기고 표 모양으로만 보여준다
        self.table = ttk.Treeview(frame, columns=keys, show="headings")
        for key, title, width in RecordWindow.COLUMNS:
            self.table.heading(key, text=title)
            self.table.column(key, width=width, anchor="center")

        # 기록이 많으면 아래로 내려 볼 수 있도록 스크롤바를 붙인다
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.table.yview)
        self.table.config(yscrollcommand=scrollbar.set)

        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def make_bottom(self, count):
        """아래쪽: 기록 개수 글자와 닫기 버튼"""
        frame = tk.Frame(self)
        frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(frame, text=f"전체 기록: {count}개").pack(side="left")
        tk.Button(frame, text="닫기", width=8, command=self.destroy).pack(side="right")

    def fill_table(self, records):
        """기록을 최신 것이 위로 오도록 표에 한 줄씩 넣는다"""
        if len(records) == 0:
            # 기록이 없으면 안내 문구를 한 줄 넣는다
            empty_row = ["기록이 없습니다"] + [""] * (len(RecordWindow.COLUMNS) - 1)
            self.table.insert("", "end", values=empty_row)
            return

        # records는 오래된 것부터 들어 있으므로 뒤에서부터 넣는다
        for i in range(len(records) - 1, -1, -1):
            record = records[i]
            values = []
            for key, title, width in RecordWindow.COLUMNS:
                value = record.get(key, "")
                if key == "path_length" and value == -1:
                    value = "없음"            # 길이 없는 미로
                elif key == "elapsed_ms":
                    value = f"{value:.2f}"    # 소수 둘째 자리까지
                values.append(value)
            self.table.insert("", "end", values=values)
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m gui.record_window
    root = tk.Tk()
    root.title("RecordWindow 테스트")

    fake_records = [
        {"datetime": "2026-11-20 14:31:02", "maze_name": "sample_21", "rows": 21, "cols": 21,
         "algorithm": "BFS", "visited_count": 187, "path_length": 64, "elapsed_ms": 0.42},
        {"datetime": "2026-11-20 14:31:10", "maze_name": "sample_21", "rows": 21, "cols": 21,
         "algorithm": "DFS", "visited_count": 102, "path_length": 88, "elapsed_ms": 0.21},
        {"datetime": "2026-11-20 14:32:00", "maze_name": "막힌미로", "rows": 11, "cols": 11,
         "algorithm": "BFS", "visited_count": 15, "path_length": -1, "elapsed_ms": 0.05},
    ]

    tk.Button(root, text="기록 3개 창 열기",
              command=lambda: RecordWindow(root, fake_records)).pack(padx=20, pady=5)
    tk.Button(root, text="빈 기록 창 열기",
              command=lambda: RecordWindow(root, [])).pack(padx=20, pady=5)
    root.mainloop()
