# core/stats.py
# 담당: 윤종하 (류지언 코딩 대행)
# 설명: 실행 기록(records.csv)을 matplotlib 막대 그래프로 보여준다 (14주차)

from tkinter import messagebox

import matplotlib.pyplot as plt

# 그래프의 한글 제목이 네모로 깨지지 않게 한다
plt.rcParams["font.family"] = "Malgun Gothic"   # Windows 기본 한글 글꼴
plt.rcParams["axes.unicode_minus"] = False       # 마이너스 기호 깨짐 방지


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.4장 명세에 맞춘 StatsViewer 막대 그래프 구현 (14주차)
# 프롬프트  : "리드미를 읽고 14주차 윤종하 코드를 컴퓨터공학과 1학년 대학생 수준으로 작성해줘"
# 사용자    : 윤종하
# 날짜      : 2026-11-27
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class StatsViewer:
    """기록을 matplotlib 막대 그래프로 보여준다"""

    ALGORITHMS = ["BFS", "DFS"]                  # 그래프에 표시할 알고리즘 순서
    BAR_COLORS = ["#A3C0DF", "#E09F1F"]          # BFS는 파랑, DFS는 주황

    def average(self, records, algorithm, key):
        """records 중 algorithm의 key 값 평균. 값이 하나도 없으면 0"""
        total = 0
        count = 0
        for record in records:
            if record["algorithm"] != algorithm:
                continue
            value = record[key]
            # 경로를 못 찾은 기록(path_length = -1)은 평균에서 뺀다
            if key == "path_length" and value < 0:
                continue
            total += value
            count += 1

        if count == 0:
            return 0
        return total / count

    def show_comparison(self, records):
        """알고리즘별 평균 방문 칸 수와 평균 경로 길이를 막대 그래프 2개로 표시.
        records가 비어 있으면 messagebox로 안내"""
        if not records:
            messagebox.showinfo("알림", "실행 기록이 없습니다.\n먼저 BFS 또는 DFS 탐색을 실행해 주세요.")
            return

        # 1. 알고리즘별 평균 구하기
        visited_avgs = []
        path_avgs = []
        for algorithm in self.ALGORITHMS:
            visited_avgs.append(self.average(records, algorithm, "visited_count"))
            path_avgs.append(self.average(records, algorithm, "path_length"))

        # 2. 그래프 2개를 옆으로 나란히 만든다 (1행 2열)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
        fig.suptitle(f"BFS / DFS 비교 (기록 {len(records)}개)")

        self.draw_bar(ax1, visited_avgs, "평균 방문 칸 수", "칸 수")
        self.draw_bar(ax2, path_avgs, "평균 경로 길이", "이동 횟수")

        plt.tight_layout()
        plt.show()

    def draw_bar(self, ax, values, title, ylabel):
        """ax 한 칸에 BFS, DFS 막대를 그리고 막대 위에 숫자를 적는다"""
        bars = ax.bar(self.ALGORITHMS, values, color=self.BAR_COLORS)
        ax.set_title(title)
        ax.set_ylabel(ylabel)

        # 막대 위에 평균값을 소수 첫째 자리까지 표시
        for bar, value in zip(bars, values):
            x = bar.get_x() + bar.get_width() / 2   # 막대 가운데
            ax.text(x, value, f"{value:.1f}", ha="center", va="bottom")
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    # 프로젝트 폴더에서 실행: python -m core.stats
    viewer = StatsViewer()
    fake_records = [
        {"algorithm": "BFS", "visited_count": 180, "path_length": 64},
        {"algorithm": "BFS", "visited_count": 200, "path_length": 70},
        {"algorithm": "DFS", "visited_count": 100, "path_length": 88},
        {"algorithm": "DFS", "visited_count": 120, "path_length": -1},   # 경로 없음
    ]
    print(viewer.average(fake_records, "BFS", "visited_count"))   # 190.0
    print(viewer.average(fake_records, "DFS", "path_length"))     # 88.0 (-1은 제외)
    print(viewer.average([], "BFS", "visited_count"))             # 0
    viewer.show_comparison(fake_records)                          # 그래프 창이 뜬다
