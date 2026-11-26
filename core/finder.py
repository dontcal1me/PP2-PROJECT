

"""길찾기 알고리즘: BFS(너비 우선), DFS(깊이 우선) 탐색"""
import time
from collections import deque


# ===== [AI 사용] =====
# AI 종류   : Claude (Anthropic)
# 사용 목적 : README 5.1장 명세에 맞춘 SearchResult, BFSFinder, DFSFinder 구현
# 프롬프트  : "리드미 파일을 읽고 finder 파일을 작성해줘"
# 사용자    : 윤종하
# 날짜      : 2026-11-21
# 수정 내용 : (직접 이해하고 수정한 부분이 있으면 여기에 적기)
# =====================
class SearchResult:
    """탐색 한 번의 결과를 담는 클래스"""

    def __init__(self, algorithm, visit_order, path, elapsed_ms):
        self.algorithm = algorithm        # "BFS" 또는 "DFS"
        self.visit_order = visit_order    # 방문한 순서대로 좌표 list
        self.path = path                  # 출발~도착 좌표 list, 못 찾으면 []
        self.elapsed_ms = elapsed_ms      # 탐색에 걸린 시간 (밀리초, float)

    @property
    def visited_count(self):
        """방문한 칸 수"""
        return len(self.visit_order)

    @property
    def path_length(self):
        """이동 횟수. 경로가 없으면 -1"""
        return len(self.path) - 1 if self.path else -1


class PathFinder:
    """탐색 알고리즘의 부모 클래스"""
    name = "BASE"

    def find(self, maze):
        """maze의 start에서 goal까지 탐색하고 SearchResult를 반환"""
        raise NotImplementedError

    def build_path(self, parent, goal):
        """parent dict를 거꾸로 따라가 경로 list를 만든다. 못 찾았으면 []"""
        if goal not in parent:
            return []
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        return path


class BFSFinder(PathFinder):
    """큐(deque)를 사용하는 너비 우선 탐색. 최단 경로 보장"""
    name = "BFS"

    def find(self, maze):
        """start에서 goal까지 BFS로 탐색한다"""
        start, goal = maze.start, maze.goal
        visit_order = []
        parent = {start: None}       # 큐에 넣을 때 기록하므로 중복 방문이 없다
        queue = deque([start])

        t0 = time.perf_counter()
        found = False
        while queue:
            current = queue.popleft()
            visit_order.append(current)
            if current == goal:
                found = True
                break
            for nxt in maze.neighbors(current):
                if nxt not in parent:
                    parent[nxt] = current
                    queue.append(nxt)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        path = self.build_path(parent, goal) if found else []
        return SearchResult(self.name, visit_order, path, elapsed_ms)


class DFSFinder(PathFinder):
    """스택(list)을 사용하는 깊이 우선 탐색"""
    name = "DFS"

    def find(self, maze):
        """start에서 goal까지 DFS로 탐색한다"""
        start, goal = maze.start, maze.goal
        visit_order = []
        parent = {}                  # 꺼내서 방문할 때 기록한다
        visited = set()
        stack = [(start, None)]      # (칸, 그 칸으로 온 이전 칸)

        t0 = time.perf_counter()
        found = False
        while stack:
            current, prev = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            parent[current] = prev
            visit_order.append(current)
            if current == goal:
                found = True
                break
            # 역순으로 넣어야 상, 우, 하, 좌 순서로 꺼낸다
            for nxt in reversed(maze.neighbors(current)):
                if nxt not in visited:
                    stack.append((nxt, current))
        elapsed_ms = (time.perf_counter() - t0) * 1000

        path = self.build_path(parent, goal) if found else []
        return SearchResult(self.name, visit_order, path, elapsed_ms)
# ===== [AI 사용 끝] =====


if __name__ == "__main__":
    from core.maze import Maze

    # 두 길이 있는 미로: 위쪽 길은 짧고, 아래쪽 길은 멀리 돌아간다
    grid = [[1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1]]
    m = Maze(5, 7, grid=grid, start=(1, 1), goal=(3, 5), name="test")

    for finder in (BFSFinder(), DFSFinder()):
        r = finder.find(m)
        print(r.algorithm, "방문:", r.visited_count, "경로 길이:", r.path_length,
              "시간(ms): %.2f" % r.elapsed_ms)
        print("  경로:", r.path)

    bfs_len = BFSFinder().find(m).path_length
    dfs_len = DFSFinder().find(m).path_length
    print("BFS <= DFS:", bfs_len <= dfs_len)                     # True

    # 경로가 없는 미로: 출발점과 도착점 사이를 벽으로 막는다
    blocked = Maze(5, 7, grid=[row[:] for row in grid], start=(1, 1), goal=(3, 5))
    for pos in [(1, 3), (3, 3)]:
        blocked.grid[pos[0]][pos[1]] = Maze.WALL
    for finder in (BFSFinder(), DFSFinder()):
        r = finder.find(blocked)
        print(r.algorithm, "막힌 미로 path:", r.path, "길이:", r.path_length)  # [] -1
