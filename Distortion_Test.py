import subprocess
import sys

def sungsoo_wihan_package_downloader(package):
    try:
        __import__(package)
        print("이 게임은 pygame-ce 기반입니다. pygame을 지우고 pygame-ce로 주입합니다.")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame-ce", "numpy", "scipy"])
    except ImportError:
        print("파이게임CE가 설치되어있지 않군요! 파이게임CE를 주입합니다.")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pygame-ce", "numpy", "scipy"]
        )
        print("파이게임CE 설치 완료!")
    finally:
        print("파이게임CE가 설치되어 있군요! 잘했네~")

"""
Pygame CE - 공간 왜곡 효과 성능 데모
필요한 패키지: pygame-ce, numpy, scipy
설치: pip install pygame-ce numpy scipy
"""

sungsoo_wihan_package_downloader("pygame")

import pygame
import numpy as np
from scipy.ndimage import map_coordinates
import sys
import math

# Pygame CE 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame CE - 공간 왜곡 효과 데모 (클릭으로 효과 생성)")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (40, 40, 40)
PURPLE = (138, 43, 226)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)

# FPS 설정
clock = pygame.time.Clock()
FPS = 60


class SpatialDistortionEffect(pygame.sprite.Sprite):
    """공간 왜곡 효과 클래스 - numpy와 scipy를 활용한 픽셀 직접 조작"""

    def __init__(self, pos, max_radius, lifetime, intensity, groups):
        super().__init__(groups)

        self.pos = pygame.math.Vector2(pos)
        self.max_radius = max_radius
        self.lifetime = lifetime
        self.age = 0
        self.intensity = intensity

        # 효과가 그려질 전체 영역
        size = int(max_radius * 2)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.pos

        # 최종 왜곡 이미지를 담을 Surface
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        # 왜곡 계산을 위한 좌표 그리드 생성 (초기화 시 한 번만)
        y_coords, x_coords = np.meshgrid(
            np.arange(size), np.arange(size), indexing="ij"
        )

        # 중심점으로부터의 상대 좌표
        center = size / 2
        self.rel_x = x_coords - center
        self.rel_y = y_coords - center

        # 각 픽셀의 중심으로부터의 거리와 각도
        self.distance = np.sqrt(self.rel_x**2 + self.rel_y**2)
        self.angle = np.arctan2(self.rel_y, self.rel_x)

        # 애니메이션 속도
        self.anim_speed = 7.0

    def update(self, dt, background_surface):
        """왜곡 효과 업데이트"""
        self.age += dt
        if self.age >= self.lifetime:
            self.kill()
            return

        try:
            # 진행률 (0.0 -> 1.0)
            progress = self.age / self.lifetime

            # 시간에 따라 변화하는 왜곡 강도
            wave_intensity = (
                self.intensity
                * (1 - progress**0.5)
                * (np.sin(progress * np.pi * 6) * 0.5 + 1)
            )

            # 왜곡 공식: 거리와 시간에 따른 파동 효과
            wave = (
                np.sin(self.distance * 0.08 - self.age * self.anim_speed)
                * wave_intensity
            )
            spiral = self.age * 3.0  # 회전 효과

            angle_offset = np.pi

            # 왜곡된 좌표 계산
            displaced_x = self.rel_x + wave * np.cos(self.angle + spiral + angle_offset)
            displaced_y = self.rel_y + wave * np.sin(self.angle + spiral + angle_offset)

            # 원래 좌표계로 변환
            center = self.rect.width / 2
            map_x = displaced_x + center
            map_y = displaced_y + center

            # 배경을 numpy 배열로 변환 (pixels3d는 참조를 반환하므로 주의)[119][122]
            source_array = pygame.surfarray.array3d(background_surface)

            # 채널별로 픽셀 매핑 (order=1은 선형 보간)[118][121]
            coords = np.array([map_x, map_y])
            distorted_r = map_coordinates(
                source_array[:, :, 0], coords, order=1, mode="wrap"
            )
            distorted_g = map_coordinates(
                source_array[:, :, 1], coords, order=1, mode="wrap"
            )
            distorted_b = map_coordinates(
                source_array[:, :, 2], coords, order=1, mode="wrap"
            )

            # 채널 합치기
            distorted_array = np.stack((distorted_r, distorted_g, distorted_b), axis=-1)

            # 알파 마스크: 중심부는 불투명, 가장자리로 갈수록 투명
            alpha_mask = np.clip(255 * (1.0 - self.distance / self.max_radius), 0, 255)
            alpha_mask *= (1 - progress**2) * 1  # 시간에 따라 페이드아웃

            # 알파 채널 추가
            distorted_array = distorted_array.astype(np.uint8)
            alpha_channel = alpha_mask.astype(np.uint8)

            # Surface 생성 (축 순서 주의: numpy는 (width, height), pygame은 (height, width))
            distorted_surface = pygame.surfarray.make_surface(distorted_array)

            # 알파 채널을 별도로 설정
            alpha_surface = pygame.surfarray.make_surface(
                np.dstack([alpha_channel] * 3)
            )
            self.image = distorted_surface.copy()
            self.image.set_alpha(int(np.mean(alpha_mask)))

        except Exception as e:
            # 에러 발생 시 효과 제거
            print(f"Effect error: {e}")
            self.kill()


class Boss(pygame.sprite.Sprite):
    """보스 객체"""

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PURPLE, (40, 40), 40)
        pygame.draw.circle(self.image, CYAN, (40, 40), 30, 3)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.math.Vector2(pos)
        self.angle = 0

    def update(self, dt):
        # 보스가 천천히 회전
        self.angle += dt * 50
        self.pos.x = SCREEN_WIDTH // 2 + math.sin(self.angle * 0.02) * 100
        self.rect.center = self.pos


class Platform(pygame.sprite.Sprite):
    """플랫폼 객체"""

    def __init__(self, pos, size, color, groups):
        super().__init__(groups)
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)


class Particle(pygame.sprite.Sprite):
    """배경 장식용 파티클"""

    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.Surface((3, 3))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()

        self.pos = pygame.math.Vector2(
            np.random.randint(0, SCREEN_WIDTH), np.random.randint(0, SCREEN_HEIGHT)
        )
        self.vel = pygame.math.Vector2(
            np.random.uniform(-20, 20), np.random.uniform(-20, 20)
        )
        self.rect.center = self.pos

    def update(self, dt):
        self.pos += self.vel * dt

        # 화면 경계에서 반사
        if self.pos.x <= 0 or self.pos.x >= SCREEN_WIDTH:
            self.vel.x *= -1
        if self.pos.y <= 0 or self.pos.y >= SCREEN_HEIGHT:
            self.vel.y *= -1

        self.rect.center = self.pos

class Camera:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.zoom = 1.1
        self.speed = 1.25
        self.timer = 0.0
        self.bouncing = True
        self.cycle_duration = 0.25

    def update(self, dt):
        if self.bouncing:
            self.timer += dt * self.speed
            progress = (self.timer % self.cycle_duration) / self.cycle_duration
            self.zoom = 1.1 - 0.1 * progress

    def apply(self, surf):
        w, h = self.screen_size
        sw, sh = int(w * self.zoom), int(h * self.zoom)
        surf_zoomed = pygame.transform.smoothscale(surf, (sw, sh))
        l, t = (sw - w) // 2, (sh - h) // 2
        subs = surf_zoomed.subsurface((l, t, w, h)).copy()
        return subs


def draw_grid(surface):
    """배경 그리드 그리기"""
    grid_size = 40
    for x in range(0, SCREEN_WIDTH, grid_size):
        pygame.draw.line(surface, DARK_GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, grid_size):
        pygame.draw.line(surface, DARK_GRAY, (0, y), (SCREEN_WIDTH, y), 1)

camera = Camera((SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    """메인 게임 루프"""

    # 스프라이트 그룹
    all_sprites = pygame.sprite.Group()
    effects_group = pygame.sprite.Group()
    background_particles = pygame.sprite.Group()

    # 보스 생성
    boss = Boss((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), all_sprites)

    # 플랫폼 생성
    platforms = [
        Platform((100, 500), (200, 20), RED, all_sprites),
        Platform((400, 400), (150, 20), CYAN, all_sprites),
        Platform((700, 550), (180, 20), YELLOW, all_sprites),
        Platform((900, 300), (200, 20), PURPLE, all_sprites),
    ]

    # 배경 파티클 생성
    for _ in range(30):
        Particle(background_particles)

    # 폰트 설정
    font = pygame.font.Font(None, 36)
    info_font = pygame.font.Font(None, 24)

    # 게임 변수
    running = True
    effect_count = 0

    while running:
        dt = clock.tick(FPS) / 1000.0  # delta time (초 단위)

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # 스페이스바: 보스 위치에 효과 생성
                if event.key == pygame.K_SPACE:
                    SpatialDistortionEffect(
                        boss.rect.center, 150, 2.5, 25, effects_group
                    )
                    effect_count += 1

            # 마우스 클릭: 클릭 위치에 효과 생성
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 좌클릭
                    SpatialDistortionEffect(event.pos, 120, 2.0, 20, effects_group)
                    effect_count += 1
                elif event.button == 3:  # 우클릭 (큰 효과)
                    SpatialDistortionEffect(event.pos, 200, 3.0, 35, effects_group)
                    effect_count += 1

        # 업데이트
        all_sprites.update(dt)
        background_particles.update(dt)

        # 화면 그리기
        screen.fill(BLACK)
        draw_grid(screen)

        cam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        cam_surface.fill(BLACK)
        draw_grid(cam_surface)

        # 배경 파티클
        background_particles.draw(screen)

        # 일반 객체들
        all_sprites.draw(screen)

        # 왜곡 효과 업데이트 및 그리기
        for effect in effects_group:
            # 효과 영역의 배경 캡처
            try:
                # 화면 경계 확인
                capture_rect = effect.rect.clip(screen.get_rect())
                if capture_rect.width > 0 and capture_rect.height > 0:
                    background_capture = screen.subsurface(capture_rect).copy()
                    effect.update(dt, background_capture)
                    screen.blit(effect.image, effect.rect)
                else:
                    effect.kill()
            except ValueError:
                effect.kill()

        # FPS 및 정보 표시
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, WHITE)
        screen.blit(fps_text, (10, 10))

        active_effects = len(effects_group)
        effect_text = info_font.render(f"활성 효과: {active_effects}", True, CYAN)
        screen.blit(effect_text, (10, 50))

        total_text = info_font.render(f"생성된 총 효과: {effect_count}", True, YELLOW)
        screen.blit(total_text, (10, 75))

        # 사용 안내
        info_lines = [
            "좌클릭: 중간 크기 효과 생성",
            "우클릭: 큰 효과 생성",
            "스페이스: 보스 위치에 효과",
            "ESC: 종료",
        ]
        for i, line in enumerate(info_lines):
            info = info_font.render(line, True, WHITE)
            screen.blit(info, (10, SCREEN_HEIGHT - 110 + i * 25))
        
        # ... (각종 draw, blit) ...
        camera.update(dt)
        result = camera.apply(cam_surface)
        screen.blit(result, (0,0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    print("=" * 60)
    print("Pygame CE - 공간 왜곡 효과 성능 데모")
    print("=" * 60)
    print("필요한 패키지: pygame-ce, numpy, scipy")
    print("설치: pip install pygame-ce numpy scipy")
    print("=" * 60)
    main()