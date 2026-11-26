"""공통 설정: 색, 크기, 경로 등은 여기서만 정의하고 다른 파일에서 가져다 쓴다."""

CELL_SIZE = 24                 # 칸 한 변의 픽셀 수
DEFAULT_SIZE = 21              # 기본 미로 크기
MIN_SIZE, MAX_SIZE = 11, 41
DEFAULT_SPEED_MS = 30          # 애니메이션 기본 간격 (밀리초)

DATA_DIR = "data"
MAZE_DIR = "data/mazes"
RECORD_FILE = "data/records.csv"

COLORS = {
    "wall": "#1B2433",     # 벽
    "road": "#FFFFFF",     # 길
    "visited": "#A3C0DF",  # 방문한 칸
    "frontier": "#F2D492", # 대기 중인 칸
    "path": "#E09F1F",     # 최종 경로
    "start": "#2E8B57",    # 출발점
    "goal": "#C0392B",     # 도착점
}
