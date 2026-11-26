# file_manager.py
# 담당: 윤종하 (12주차 전반 구현은 윤종하가 대행)
# 설명: 미로 json 저장/불러오기, 실행 기록 csv 관리

import os
import json
import csv
from datetime import datetime

from core.maze import Maze
from core.config import MAZE_DIR, RECORD_FILE

RECORD_HEADER = ["datetime", "maze_name", "rows", "cols", "algorithm",
                 "visited_count", "path_length", "elapsed_ms"]


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.4장 명세에 맞춘 FileManager의 미로 저장/불러오기 구현
# 사용자    : 윤종하
# 날짜      : 2026-11-21
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class FileManager:
    """미로 json 저장/불러오기, 실행 기록 csv 관리"""

    def __init__(self):
        """미로 저장 폴더가 없으면 만든다"""
        os.makedirs(MAZE_DIR, exist_ok=True)

    def _maze_path(self, name):
        """미로 이름으로 json 파일 경로를 만든다. 경로 구분자가 섞인 이름은 거부"""
        if not name or name != os.path.basename(name) or name in (".", ".."):
            raise ValueError(f"잘못된 미로 이름: {name!r}")
        return os.path.join(MAZE_DIR, name + ".json")

    def save_maze(self, maze, name):
        """maze를 MAZE_DIR/<name>.json으로 저장하고 저장한 경로를 반환"""
        path = self._maze_path(name)
        os.makedirs(MAZE_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(maze.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    def load_maze(self, name):
        """MAZE_DIR/<name>.json을 읽어 Maze 객체로 반환. 없으면 FileNotFoundError"""
        path = self._maze_path(name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"저장된 미로가 없습니다: {name}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Maze.from_dict(data)

    def list_mazes(self):
        """저장된 미로 이름(확장자 제외) list. 이름순 정렬"""
        if not os.path.isdir(MAZE_DIR):
            return []
        return sorted(os.path.splitext(f)[0]
                      for f in os.listdir(MAZE_DIR) if f.endswith(".json"))

# ===== [AI 사용 끝] =====

    # ===== [AI 사용] =====
    # AI 종류   : Claude (Anthropic)
    # 사용 목적 : README 5.4장 명세에 맞춘 실행 기록 csv 저장/읽기 (12주차 후반)
    # 프롬프트  : "리드미를 읽고 12주차 후반 윤종하 코드를 컴퓨터공학과 1학년 대학생 수준으로 작성해줘"
    # 사용자    : 윤종하
    # 날짜      : 2026-11-25
    # 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
    # =====================
    def append_record(self, result, maze):
        """SearchResult 하나를 records.csv에 한 줄 추가. 파일이 없으면 헤더부터 작성"""
        # data 폴더가 없으면 만든다
        folder = os.path.dirname(RECORD_FILE)
        os.makedirs(folder, exist_ok=True)

        # 파일이 없거나 비어 있을 때만 헤더를 쓴다 (헤더가 여러 번 들어가지 않게)
        need_header = False
        if not os.path.exists(RECORD_FILE):
            need_header = True
        elif os.path.getsize(RECORD_FILE) == 0:
            need_header = True

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, maze.name, maze.rows, maze.cols, result.algorithm,
               result.visited_count, result.path_length,
               round(result.elapsed_ms, 2)]

        # "a" = 이어쓰기, newline="" = 빈 줄 방지, utf-8-sig = 엑셀 한글 깨짐 방지
        with open(RECORD_FILE, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if need_header:
                writer.writerow(RECORD_HEADER)
            writer.writerow(row)

    def load_records(self):
        """records.csv를 읽어 dict의 list로 반환. 파일이 없으면 []"""
        if not os.path.exists(RECORD_FILE):
            return []

        records = []
        with open(RECORD_FILE, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)   # 첫 줄(헤더)을 key로 쓰는 dict를 한 줄씩 준다
            for row in reader:
                # csv에서 읽은 값은 모두 글자(str)이므로 숫자 칸은 숫자로 바꾼다
                try:
                    row["rows"] = int(row["rows"])
                    row["cols"] = int(row["cols"])
                    row["visited_count"] = int(row["visited_count"])
                    row["path_length"] = int(row["path_length"])
                    row["elapsed_ms"] = float(row["elapsed_ms"])
                except (ValueError, TypeError, KeyError):
                    continue             # 엑셀 등에서 망가진 줄은 건너뛴다
                records.append(row)
        return records
    # ===== [AI 사용 끝] =====


if __name__ == "__main__":
    fm = FileManager()
    m = Maze(5, 5, name="test", seed=7)
    m.grid[1][1] = m.grid[1][2] = m.grid[1][3] = Maze.ROAD
    m.grid[2][3] = m.grid[3][3] = Maze.ROAD
    m.goal = (3, 3)

    print(fm.save_maze(m, "test"))
    loaded = fm.load_maze("test")
    print("start:", loaded.start, type(loaded.start))       # (1, 1) tuple
    print("goal:", loaded.goal, type(loaded.goal))          # (3, 3) tuple
    print("grid 같음:", loaded.grid == m.grid)              # True
    print("seed/name:", loaded.seed, loaded.name)           # 7 test
    print("목록:", fm.list_mazes())

    try:
        fm.load_maze("없는미로")
    except FileNotFoundError as e:
        print("FileNotFoundError:", e)

    # 실행 기록 테스트 (12주차 후반)
    had_records = os.path.exists(RECORD_FILE)               # 원래 기록 파일이 있었는지

    class Fake:
        algorithm = "BFS"; visited_count = 10; path_length = 4; elapsed_ms = 0.123
    fm.append_record(Fake(), m)
    fm.append_record(Fake(), m)
    records = fm.load_records()
    print("마지막 기록:", records[-1])                       # elapsed_ms 0.12
    with open(RECORD_FILE, encoding="utf-8-sig") as f:
        header_count = f.read().count("datetime,maze_name")
    print("헤더 개수:", header_count)                         # 1

    os.remove(os.path.join(MAZE_DIR, "test.json"))          # 테스트 파일 정리
    if not had_records:
        os.remove(RECORD_FILE)                              # 테스트로 만든 기록 파일 정리
