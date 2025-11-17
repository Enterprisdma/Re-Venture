import subprocess
import sys

def sungsoo_wihan_package_downloader(package):
    try:
        __import__(package)
    except ImportError:
        print('파이게임이 설치되어있지 않군요! 파이게임을 주입합니다.')
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print('파이게임 설치 완료!')
    finally:
        print('파이게임이 설치되어 있군요! 잘했네~')

sungsoo_wihan_package_downloader("pygame")

import pygame  # noqa: E402
import math
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SEC_CONST = 1000
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (150, 0, 200)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("RE:Venture")
clock = pygame.time.Clock()

# ═══════════════════════════════════════════════════
# CAMERA CLASS
# ═══════════════════════════════════════════════════

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.scrolling = 100
        self.bg = pygame.image.load("5km.png")
        self.bg_height = self.bg.get_height()
        self.active = False
        self.lock_player = False  # 플레이어 추적 플래그
        self.scroll_acceleration = 200  # 스크롤 가속도

        self.zoom = 1.0  # 기본 줌 레벨 (1.0 = 100%)
        self.target_zoom = 1.0
        self.zoom_velocity = 0
        self.zoom_spring = 90.0  # 스프링 강도
        self.zoom_damping = 0.8 # 감쇠 (0~1)
        self.timer = 0
        self.zoom_reset_timer = 0.4

        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw_bg(self, surface):
        bg_y = self.y % self.bg_height
        surface.blit(self.bg, (0, bg_y))
        surface.blit(self.bg, (0, bg_y - self.bg_height))

    def CameraChase(self, delta, player=None):
        if self.active:
            if self.lock_player and player:
                # DOWNWELL 스타일: 플레이어 추적
                player_screen_y = self.DrawAgain(player.y)
                threshold = SCREEN_HEIGHT * 0.5  # 화면 2/4 지점

                # 플레이어가 threshold보다 아래에 있으면 카메라 따라감
                if player_screen_y > threshold:
                    # 플레이어를 threshold 위치로 유지하도록 카메라 이동
                    target_camera_y = -(player.y - threshold)
                    self.y = target_camera_y
            self.y -= self.scrolling * delta

    def update_zoom(self, delta):
        # 목표 줌과의 차이
        zoom_diff = self.target_zoom - self.zoom

        # 스프링 힘
        spring_force = zoom_diff * self.zoom_spring * delta

        # 속도 업데이트
        self.zoom_velocity += spring_force

        # 감쇠 적용
        self.zoom_velocity *= self.zoom_damping

        # 줌 레벨 업데이트
        self.zoom += self.zoom_velocity * delta

        self.timer -= delta

        # 목표에 가까우면 정확히 맞춤
        if abs(zoom_diff) < 0.001 and abs(self.zoom_velocity) < 0.001:
            self.zoom = self.target_zoom
            self.zoom_velocity = 0

        # 타이머가 끝나면 줌 리셋
        if self.timer < 0:
            self.timer = 0
            self.target_zoom = 1.0
    
    def add_zoom_bounce(self, target_zoom, duration=0.4):
        """플랫폼 파괴 시 줌 효과"""
        self.target_zoom = target_zoom
        self.timer = duration
        

    def reset_zoom(self):
        self.target_zoom = 1.0
    
    def zooming(self, screen):
        if abs(self.zoom - 1.0) < 0.001:
            screen.blit(self.render_surface, (0, 0))
        else:
            scaled_width = int(SCREEN_WIDTH * self.zoom)
            scaled_height = int(SCREEN_HEIGHT * self.zoom)

            scaled_surface = pygame.transform.scale(
                self.render_surface, (scaled_width, scaled_height)
            )

            offset_x = (scaled_width - SCREEN_WIDTH) // 2
            offset_y = (scaled_height - SCREEN_HEIGHT) // 2

            screen.blit(scaled_surface, (-offset_x, -offset_y))


    def activate(self):
        self.active = True

    def DrawAgain(self, entity_y):
        return entity_y + self.y

# ═══════════════════════════════════════════════════
# PLATFORM CLASSES
# ═══════════════════════════════════════════════════

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GRAY
        self.IntGrid = 0

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.get_rect())

class BreakablePlatform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = GREEN
        self.IntGrid = 1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.get_rect())

# ═══════════════════════════════════════════════════
# ENEMY CLASSES
# ═══════════════════════════════════════════════════

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.enemy_type = enemy_type
        self.hp = 100
        self.max_hp = 100
        self.speed = 50
        self.color = PURPLE
        self.active = True
        self.velocity_x = 0
        self.velocity_y = 0
        self.Gravity = 800
        self.knockback_timer = 0  # 넉백 지속 시간

        if enemy_type == "fast":
            self.speed = 150
            self.hp = 50
            self.max_hp = 50
            self.color = CYAN
        elif enemy_type == "tank":
            self.speed = 30
            self.hp = 300
            self.max_hp = 300
            self.color = RED
            self.width = 32
            self.height = 32

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.active = False

    def apply_knockback(self, direction, force=300):
        """넉백 효과 적용"""
        self.velocity_x = direction * force
        self.velocity_y = -200  # 약간 위로 튕김
        self.knockback_timer = 0.3  # 0.3초 동안 넉백 상태

    def instant_kill(self):
        """즉사"""
        self.active = False

    def update(self, delta, player, platforms):
        # 넉백 타이머 감소
        if self.knockback_timer > 0:
            self.knockback_timer -= delta
            # 넉백 중에는 AI 이동 안 함
        else:
            # AI: Move towards player
            dx = player.x - self.x
            if abs(dx) > 10:
                direction = 1 if dx > 0 else -1
                self.velocity_x = self.speed * direction
            else:
                self.velocity_x = 0

        # Apply gravity
        self.velocity_y += self.Gravity * delta

        # Update position
        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta

        # Simple collision with platforms
        for platform in platforms:
            if self.get_rect().colliderect(platform.get_rect()):
                if self.velocity_y > 0:
                    self.y = platform.y - self.height
                    self.velocity_y = 0

        # Screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)
        pygame.draw.rect(surface, self.color, (self.x, screen_y, self.width, self.height))

        # HP bar
        hp_ratio = self.hp / self.max_hp
        hp_bar_width = self.width
        hp_bar_height = 4
        pygame.draw.rect(surface, RED, (self.x, screen_y - 8, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, GREEN, (self.x, screen_y - 8, hp_bar_width * hp_ratio, hp_bar_height))

class SpawnIndicator:
    def __init__(self, x, y, enemy_type):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.width = 32 if enemy_type == "tank" else 24
        self.height = 32 if enemy_type == "tank" else 24
        self.blink_timer = 0
        self.blink_count = 0
        self.blink_interval = 0.2
        self.show = True
        self.ready_to_spawn = False

    def update(self, delta):
        self.blink_timer += delta
        if self.blink_timer >= self.blink_interval:
            self.blink_timer = 0
            self.show = not self.show
            if self.show:
                self.blink_count += 1
            if self.blink_count >= 3:
                self.ready_to_spawn = True

    def draw(self, surface, camera):
        if self.show and not self.ready_to_spawn:
            screen_y = camera.DrawAgain(self.y)
            pygame.draw.rect(surface, YELLOW, (self.x, screen_y, self.width, self.height), 3)

class EnemySpawner:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_interval = 3.0
        self.enemies = []
        self.indicators = []

    def update(self, delta, camera_y):
        self.spawn_timer += delta

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.create_spawn_indicator(camera_y)

        # Update indicators
        for indicator in self.indicators[:]:
            indicator.update(delta)
            if indicator.ready_to_spawn:
                self.spawn_enemy_from_indicator(indicator)
                self.indicators.remove(indicator)

    def create_spawn_indicator(self, camera_y):
        # 카메라 기준 화면 내 랜덤 위치
        spawn_x = random.randint(50, SCREEN_WIDTH - 50)
        spawn_y = abs(camera_y) + random.randint(100, SCREEN_HEIGHT - 100)

        enemy_type = random.choice(["basic", "basic", "fast", "tank"])
        indicator = SpawnIndicator(spawn_x, spawn_y, enemy_type)
        self.indicators.append(indicator)

    def spawn_enemy_from_indicator(self, indicator):
        enemy = Enemy(indicator.x, indicator.y, indicator.enemy_type)
        self.enemies.append(enemy)

    def update_enemies(self, delta, player, platforms, entities):
        for enemy in self.enemies[:]:
            enemy.update(delta, player, platforms)

            # Check collision with player attacks
            for entity in entities:
                if hasattr(entity, 'get_rect') and entity.active:
                    if enemy.get_rect().colliderect(entity.get_rect()):
                        if isinstance(entity, (Bullet, AttackEffect)):
                            damage = 30 if isinstance(entity, Bullet) else 50
                            enemy.take_damage(damage)
                            if isinstance(entity, Bullet):
                                entity.active = False

            if not enemy.active:
                self.enemies.remove(enemy)

    def draw(self, surface, camera):
        # Draw spawn indicators
        for indicator in self.indicators:
            indicator.draw(surface, camera)
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface, camera)

# ═══════════════════════════════════════════════════
# ENTITY CLASSES (Bullets, Effects)
# ═══════════════════════════════════════════════════

class Bullet:
    def __init__(self, x, y, direction=None, angle=None, speed=600):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 8
        self.height = 4
        self.color = YELLOW
        self.active = True
        self.camera = None  # 카메라 참조 추가

        # 각도 또는 방향으로 속도 벡터 설정
        if angle is not None:
            self.angle = angle  # 각도 저장
            self.velocity_x = math.cos(angle) * speed
            self.velocity_y = math.sin(angle) * speed
        else:
            self.angle = 0 if direction > 0 else math.pi  # 방향을 각도로 변환
            self.velocity_x = direction * speed
            self.velocity_y = 0

    def update(self, delta):
        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta

        # 화면 좌표로 경계 체크
        if self.camera:
            screen_y = self.camera.DrawAgain(self.y)
            if self.x < -100 or self.x > SCREEN_WIDTH + 100 or screen_y < -100 or screen_y > SCREEN_HEIGHT + 100:
                self.active = False
        else:
            # 카메라 없으면 기존 방식
            if self.x < -100 or self.x > SCREEN_WIDTH + 100 or self.y < -500 or self.y > SCREEN_HEIGHT + 500:
                self.active = False

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)

        # 회전된 총알 그리기
        # 1. 원본 Surface 생성
        bullet_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, self.color, (0, 0, self.width, self.height))

        # 2. 각도를 degree로 변환하고 회전
        angle_deg = -math.degrees(self.angle)
        rotated_surface = pygame.transform.rotate(bullet_surface, angle_deg)

        # 3. 회전 후 중심점 정렬
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, screen_y + self.height // 2))

        # 4. 화면에 그리기
        surface.blit(rotated_surface, rotated_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class AttackEffect:
    def __init__(self, x, y, width, height, duration=0.1):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.duration = duration
        self.timer = 0
        self.color = ORANGE
        self.active = True

    def update(self, delta):
        self.timer += delta
        if self.timer >= self.duration:
            self.active = False

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)
        pygame.draw.rect(surface, self.color, (self.x, screen_y, self.width, self.height), 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Rocket:
    def __init__(self, x, y, angle, speed=500):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 12
        self.height = 6
        self.color = RED
        self.active = True
        self.camera = None
        self.angle = angle  # 각도 저장

        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed
        self.explosion_radius = 150

        # 트레일 생성을 위한 타이머
        self.trail_timer = 0
        self.trail_interval = 0.05  # 0.05초마다 트레일 생성

    def update(self, delta):
        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta

        # 트레일 생성 타이머
        self.trail_timer += delta
        trail = None
        if self.trail_timer >= self.trail_interval:
            self.trail_timer = 0
            trail = RocketTrail(self.x, self.y)  # 트레일 생성
            if self.camera:
                trail.camera = self.camera

        # 화면 경계 체크
        if self.camera:
            screen_y = self.camera.DrawAgain(self.y)
            if self.x < -100 or self.x > SCREEN_WIDTH + 100 or screen_y < -100 or screen_y > SCREEN_HEIGHT + 100:
                self.active = False
        else:
            if self.x < -100 or self.x > SCREEN_WIDTH + 100 or self.y < -500 or self.y > SCREEN_HEIGHT + 500:
                self.active = False

        return trail  # 생성된 트레일 반환 (없으면 None)

    def explode(self, entities):
        """폭발 생성"""
        explosion = Explosion(self.x, self.y, self.explosion_radius)
        explosion.camera = self.camera
        self.camera.add_zoom_bounce(1.5, 0.1)
        entities.append(explosion)
        self.active = False

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)

        # 회전된 로켓 그리기
        # 1. 원본 Surface 생성
        rocket_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(rocket_surface, self.color, (0, 0, self.width, self.height))
        # 로켓 꼬리 효과
        pygame.draw.circle(rocket_surface, ORANGE, (0, self.height // 2), 4)

        # 2. 각도를 degree로 변환하고 회전
        angle_deg = -math.degrees(self.angle)
        rotated_surface = pygame.transform.rotate(rocket_surface, angle_deg)

        # 3. 회전 후 중심점 정렬
        rotated_rect = rotated_surface.get_rect(center=(self.x + self.width // 2, screen_y + self.height // 2))

        # 4. 화면에 그리기
        surface.blit(rotated_surface, rotated_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class RocketTrail:
    """로켓이 남기는 원형 파동 효과"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.lifetime = 0.4
        self.age = 0
        self.active = True
        self.camera = None

    def update(self, delta):
        self.age += delta
        if self.age >= self.lifetime:
            self.active = False
            return

        # 시간에 따라 반지름 증가
        progress = self.age / self.lifetime
        self.radius = 5 + (self.max_radius - 5) * progress

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)

        # 페이드아웃 효과
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))

        # 알파를 지원하는 임시 Surface에 원 그리기
        size = int(self.radius * 2)
        temp_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color_with_alpha = (*ORANGE[:3], alpha)
        pygame.draw.circle(temp_surface, color_with_alpha,
                          (int(self.radius), int(self.radius)),
                          int(self.radius), 2)

        surface.blit(temp_surface,
                    (self.x - self.radius, screen_y - self.radius))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

class Explosion:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.lifetime = 0.3
        self.age = 0
        self.active = True
        self.camera = None
        self.knockback_strength = 1200

    def update(self, delta):
        self.age += delta
        if self.age >= self.lifetime:
            self.active = False

    def check_player_in_range(self, player):
        """플레이어가 폭발 범위 안에 있는지 체크"""
        if self.age > 0.05:  # 폭발 시작 후 약간의 딜레이
            return

        dx = player.x + player.width / 2 - self.x
        dy = player.y + player.height / 2 - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.radius:
            # Forcing 상태면 빠른 낙하
            if player.state == "Forcing":
                player.velocity_y = 1500
                player.state = "Normal"
            else:
                # 넉백 적용
                if distance > 0:
                    knockback_x = (dx / distance) * self.knockback_strength
                    knockback_y = (dy / distance) * self.knockback_strength
                    player.velocity_x = knockback_x
                    player.velocity_y = knockback_y

    def check_enemies_in_range(self, enemies):
        """범위 내 적들에게 데미지"""
        if self.age > 0.05:  # 폭발 시작 직후만
            return

        for enemy in enemies[:]:
            if not enemy.active:
                continue

            # 적의 중심점 계산
            enemy_center_x = enemy.x + enemy.width / 2
            enemy_center_y = enemy.y + enemy.height / 2

            # 폭발 중심과의 거리
            dx = enemy_center_x - self.x
            dy = enemy_center_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            # 범위 내라면 데미지
            if distance < self.radius:
                # 거리에 반비례하는 데미지 (가까울수록 강함)
                damage_ratio = 1 - (distance / self.radius)
                damage = int(100 * damage_ratio)  # 최대 100 데미지

                enemy.hp -= damage

                # 넉백 효과 적용 (폭발 중심에서 멀어지는 방향)
                if distance > 0:
                    knockback_strength = 500  # 폭발 넉백은 더 강하게
                    enemy.velocity_x = (dx / distance) * knockback_strength
                    enemy.velocity_y = (dy / distance) * knockback_strength * 0.5  # Y축은 약간 약하게
                    enemy.knockback_timer = 0.4  # 넉백 지속 시간

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)

        # 진행도에 따라 크기와 색상 변화
        progress = self.age / self.lifetime
        current_radius = int(self.radius * (0.5 + progress * 0.5))

        # 색상 변화 (빨강 -> 주황 -> 노랑)
        if progress < 0.3:
            color = RED
        elif progress < 0.6:
            color = ORANGE
        else:
            color = YELLOW

        # 반투명 원 여러 개로 폭발 표현
        for i in range(3):
            alpha_radius = current_radius - i * 15
            if alpha_radius > 0:
                pygame.draw.circle(surface, color, (int(self.x), int(screen_y)), alpha_radius, 3)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class BounceBullet(Bullet):
    def __init__(self, x, y, angle, speed=600):
        super().__init__(x, y, angle=angle, speed=speed)
        self.bounce_count = 0
        self.max_bounces = 3  # 3번 튕길 수 있음
        self.color = CYAN

    def check_platform_collision(self, platforms):
        """플랫폼과의 충돌 체크 및 튕김"""
        if self.bounce_count >= self.max_bounces:
            return

        bullet_rect = self.get_rect()
        for platform in platforms:
            platform_rect = platform.get_rect()
            if bullet_rect.colliderect(platform_rect):
                # 튕김 (y 속도 반전)
                self.velocity_y *= -1
                self.bounce_count += 1

                # 각도 재계산 (튕긴 후 방향)
                self.angle = math.atan2(self.velocity_y, self.velocity_x)

                # 위치 조정 (플랫폼 밖으로)
                if self.velocity_y < 0:
                    self.y = platform_rect.top - self.height
                else:
                    self.y = platform_rect.bottom

                # 최대 튕김 횟수 초과 시 비활성화
                if self.bounce_count >= self.max_bounces:
                    self.active = False
                return

class LaserBeam:
    def __init__(self, start_x, start_y, angle, max_length=2000, camera=None):
        self.start_x = start_x
        self.start_y = start_y
        self.angle = angle
        self.max_length = max_length
        self.camera = camera

        # 레이저 끝점 계산
        self.end_x = start_x + math.cos(angle) * max_length
        self.end_y = start_y + math.sin(angle) * max_length

        # 실제 충돌 지점 (raycast 결과)
        self.hit_x = self.end_x
        self.hit_y = self.end_y
        self.hit_something = False

        # 시각 효과
        self.lifetime = 0.1  # 0.1초 동안 표시
        self.age = 0
        self.active = True
        self.width = 4  # 레이저 두께
        self.color = YELLOW

    def raycast(self, enemies, platforms):
        """광선을 쏴서 첫 번째 충돌 지점 찾기"""
        closest_distance = self.max_length
        hit_point = (self.end_x, self.end_y)

        # 방향 벡터
        dir_x = math.cos(self.angle)
        dir_y = math.sin(self.angle)

        # 적과의 충돌 체크
        for enemy in enemies:
            if not enemy.active:
                continue

            # 레이와 사각형 교차 판정 (간단한 버전)
            distance = self.line_rect_intersection(
                self.start_x, self.start_y, self.end_x, self.end_y, enemy.get_rect()
            )

            if distance and distance < closest_distance:
                closest_distance = distance
                hit_point = (
                    self.start_x + dir_x * distance,
                    self.start_y + dir_y * distance,
                )
                # 적에게 데미지
                enemy.take_damage(40)
                self.hit_something = True

        # 플랫폼과의 충돌 체크
        for platform in platforms:
            distance = self.line_rect_intersection(
                self.start_x, self.start_y, self.end_x, self.end_y, platform.get_rect()
            )

            if distance and distance < closest_distance:
                closest_distance = distance
                hit_point = (
                    self.start_x + dir_x * distance,
                    self.start_y + dir_y * distance,
                )
                self.hit_something = True

        # 충돌 지점 설정
        self.hit_x, self.hit_y = hit_point

    def line_rect_intersection(self, x1, y1, x2, y2, rect):
        """선과 사각형의 교차 거리 계산"""
        # 간단한 구현: 사각형 4개 변과 교차 체크
        # 더 정확한 구현은 Liang-Barsky 알고리즘 사용

        # 광선 방향
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)

        if length == 0:
            return None

        # 정규화
        dx /= length
        dy /= length

        # 샘플링 방식 (단순하지만 효과적)
        steps = int(length)
        for i in range(steps):
            check_x = x1 + dx * i
            check_y = y1 + dy * i

            if rect.collidepoint(check_x, check_y):
                return i  # 거리 반환

        return None

    def update(self, delta):
        self.age += delta
        if self.age >= self.lifetime:
            self.active = False

    def draw(self, surface, camera):
        """레이저 선 그리기 (페이드아웃 효과)"""
        screen_start_y = camera.DrawAgain(self.start_y)
        screen_hit_y = camera.DrawAgain(self.hit_y)

        # 페이드아웃 계산
        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))

        # 알파 지원 Surface에 그리기
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # 메인 레이저 (밝은 색)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.line(
            temp_surface,
            color_with_alpha,
            (int(self.start_x), int(screen_start_y)),
            (int(self.hit_x), int(screen_hit_y)),
            self.width,
        )

        # 외곽 글로우 효과 (더 두껍고 반투명)
        glow_alpha = int(alpha * 0.3)
        glow_color = (*YELLOW[:3], glow_alpha)
        pygame.draw.line(
            temp_surface,
            glow_color,
            (int(self.start_x), int(screen_start_y)),
            (int(self.hit_x), int(screen_hit_y)),
            self.width + 6,
        )

        surface.blit(temp_surface, (0, 0))

        # 충돌 지점에 임팩트 이펙트
        if self.hit_something and self.age < 0.05:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.hit_x), int(screen_hit_y)),
                int(10 - self.age * 100),
                3,
            )

    def get_rect(self):
        # 엔티티 리스트 호환용
        return pygame.Rect(0, 0, 0, 0)

# ═══════════════════════════════════════════════════
# WEAPON SYSTEM
# ═══════════════════════════════════════════════════

class Weapon:
    def __init__(self, name, weapon_type, cooldown):
        self.name = name
        self.weapon_type = weapon_type
        self.cooldown = cooldown
        self.cooldown_timer = 0

        # 탄약 시스템 (-1은 무한 탄약)
        self.ammo = -1
        self.max_ammo = -1
        self.reload_time = 0
        self.is_reloading = False
        self.reload_timer = 0

    def can_use(self):
        return self.cooldown_timer <= 0 and not self.is_reloading

    def start_reload(self):
        if self.max_ammo > 0 and not self.is_reloading:
            self.is_reloading = True
            self.reload_timer = self.reload_time

    def use(self, player, entities):
        # 재장전 중이면 사용 불가
        if self.is_reloading:
            return

        # 탄약이 0이면 재장전 시작
        if self.ammo == 0:
            self.start_reload()
            return

        if self.can_use():
            self.execute_action(player, entities)
            self.cooldown_timer = self.cooldown

            # 탄약 소모 (무한 탄약이 아닐 경우)
            if self.ammo > 0:
                self.ammo -= 1
                if self.ammo == 0 and self.max_ammo > 0:
                    self.start_reload()

    def update(self, delta):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta

        # 재장전 처리
        if self.is_reloading:
            self.reload_timer -= delta
            if self.reload_timer <= 0:
                self.ammo = self.max_ammo
                self.is_reloading = False
                self.reload_timer = 0

    def execute_action(self, player, entities):
        pass

class Dagger(Weapon):
    def __init__(self):
        super().__init__("Dagger", "melee", 0.3)
        self.damage = 50
        self.range = 60

    def execute_action(self, player, entities):
        attack_x = player.x + player.width if player.facing_direction > 0 else player.x - self.range
        attack_y = player.y
        attack_effect = AttackEffect(attack_x, attack_y, self.range, player.height, 0.1)
        entities.append(attack_effect)

class Rifle(Weapon):
    def __init__(self):
        super().__init__("Rifle", "ranged", 0.25)
        self.damage = 30

    def execute_action(self, player, entities):
        bullet_x = player.x + player.width // 2
        bullet_y = player.y + player.height // 2

        # 마우스 위치로 각도 계산
        mouse_x, mouse_y = player.mouse_pos

        # 플레이어의 화면 좌표 계산
        if player.camera:
            player_screen_y = player.camera.DrawAgain(bullet_y)
        else:
            player_screen_y = bullet_y

        # 화면 좌표 기준으로 각도 계산
        dx = mouse_x - bullet_x
        dy = mouse_y - player_screen_y
        angle = math.atan2(dy, dx)

        bullet = LaserBeam(bullet_x, bullet_y, angle)
        bullet.needs_raycast = True
        bullet.camera = player.camera  # 카메라 참조 전달
        entities.append(bullet)

class BoostBoots(Weapon):
    def __init__(self):
        super().__init__("BoostBoots", "utility", 1.0)

    def execute_action(self, player, entities):
        player.start_dash()

class CircularSaw(Weapon):
    def __init__(self):
        super().__init__("CircularSaw", "charge", 0.8)
        self.charge_speed = 800

    def execute_action(self, player, entities):
        player.velocity_x = self.charge_speed * player.facing_direction
        player.is_charging = True
        player.charge_timer = 0.3

class HealthPotion(Weapon):
    def __init__(self):
        super().__init__("HealthPotion", "consumable", 0.0)  # 쿨다운 0초
        self.heal_amount = 2  # 2칸 회복

    def execute_action(self, player, entities):
        # 체력 회복
        player.hp = min(player.hp + self.heal_amount, player.max_hp)

        # 사용한 슬롯 찾아서 제거
        for i, weapon in enumerate(player.weapon_slots):
            if weapon is self:
                player.remove_weapon(i)
                break

class RocketLauncher(Weapon):
    def __init__(self):
        super().__init__("RocketLauncher", "ranged", 0.3)
        self.ammo = 1
        self.max_ammo = 1
        self.reload_time = 6.0

    def execute_action(self, player, entities):
        rocket_x = player.x + player.width // 2
        rocket_y = player.y + player.height // 2

        # 마우스 위치로 각도 계산
        mouse_x, mouse_y = player.mouse_pos

        # 플레이어의 화면 좌표 계산
        if player.camera:
            player_screen_y = player.camera.DrawAgain(rocket_y)
        else:
            player_screen_y = rocket_y

        # 화면 좌표 기준으로 각도 계산
        dx = mouse_x - rocket_x
        dy = mouse_y - player_screen_y
        angle = math.atan2(dy, dx)

        rocket = Rocket(rocket_x, rocket_y, angle)
        rocket.camera = player.camera
        entities.append(rocket)

class Shotgun(Weapon):
    def __init__(self):
        super().__init__("Shotgun", "ranged", 0.4)
        self.ammo = 2
        self.max_ammo = 2
        self.reload_time = 3.0
        self.pellet_count = 10
        self.spread_angle = 0.5  # 라디안 (약 28.6도)

    def execute_action(self, player, entities):
        bullet_x = player.x + player.width // 2
        bullet_y = player.y + player.height // 2

        # 마우스 위치로 각도 계산
        mouse_x, mouse_y = player.mouse_pos

        # 플레이어의 화면 좌표 계산
        if player.camera:
            player_screen_y = player.camera.DrawAgain(bullet_y)
        else:
            player_screen_y = bullet_y

        # 화면 좌표 기준으로 중심 각도 계산
        dx = mouse_x - bullet_x
        dy = mouse_y - player_screen_y
        center_angle = math.atan2(dy, dx)

        # 10발의 총알을 스프레드로 발사
        for _ in range(self.pellet_count):
            angle = center_angle + random.uniform(-self.spread_angle, self.spread_angle)
            bullet = LaserBeam(bullet_x, bullet_y, angle)
            bullet.needs_raycast = True
            bullet.camera = player.camera
            entities.append(bullet)

class Revolver(Weapon):
    def __init__(self):
        super().__init__("Revolver", "ranged", 0.6)
        self.ammo = 6
        self.max_ammo = 6
        self.reload_time = 3.0

    def execute_action(self, player, entities):
        bullet_x = player.x + player.width // 2
        bullet_y = player.y + player.height // 2

        # 마우스 위치로 각도 계산
        mouse_x, mouse_y = player.mouse_pos

        # 플레이어의 화면 좌표 계산
        if player.camera:
            player_screen_y = player.camera.DrawAgain(bullet_y)
        else:
            player_screen_y = bullet_y

        # 화면 좌표 기준으로 각도 계산
        dx = mouse_x - bullet_x
        dy = mouse_y - player_screen_y
        angle = math.atan2(dy, dx)

        bullet = BounceBullet(bullet_x, bullet_y, angle=angle)
        bullet.camera = player.camera
        entities.append(bullet)

# ═══════════════════════════════════════════════════
# RADIAL WEAPON MENU
# ═══════════════════════════════════════════════════

class RadialWeaponMenu:
    def __init__(self):
        self.active = False
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.radius = 150
        self.font = pygame.font.Font(None, 32)
        self.selected_index = -1

    def activate(self, player_x, player_y):
        self.active = True
        self.center_x = player_x
        self.center_y = player_y

    def deactivate(self):
        self.active = False
        self.selected_index = -1

    def update(self, mouse_pos, weapons):
        if not self.active:
            return

        mx, my = mouse_pos
        dx = mx - self.center_x
        dy = my - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 30:
            angle = math.atan2(dy, dx)
            # Convert angle to 0-360 degrees
            angle_deg = (math.degrees(angle) + 360) % 360

            # Divide circle into 3 sections (120 degrees each)
            if 30 <= angle_deg < 150:  # Bottom right
                self.selected_index = 0
            elif 150 <= angle_deg < 270:  # Bottom left
                self.selected_index = 1
            else:  # Top
                self.selected_index = 2
        else:
            self.selected_index = -1

    def draw(self, surface, weapons, camera):
        if not self.active:
            return

        # Convert world position to screen position
        screen_y = camera.DrawAgain(self.center_y)

        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # Draw main circle
        pygame.draw.circle(surface, WHITE, (int(self.center_x), int(screen_y)), self.radius, 3)
        pygame.draw.circle(surface, WHITE, (int(self.center_x), int(screen_y)), 30, 2)

        # Draw weapon sections
        angles = [60, 180, 300]  # Positions for 3 weapons
        for i, angle in enumerate(angles):
            rad = math.radians(angle)
            x = self.center_x + math.cos(rad) * self.radius * 0.7
            y = screen_y + math.sin(rad) * self.radius * 0.7

            # Highlight selected
            color = YELLOW if i == self.selected_index else WHITE

            # Draw weapon slot circle
            pygame.draw.circle(surface, color, (int(x), int(y)), 40, 3)

            # Draw weapon name
            if i < len(weapons) and weapons[i]:
                weapon_text = self.font.render(weapons[i].name, True, color)
                text_rect = weapon_text.get_rect(center=(int(x), int(y)))
                surface.blit(weapon_text, text_rect)
            else:
                empty_text = self.font.render("Empty", True, GRAY)
                text_rect = empty_text.get_rect(center=(int(x), int(y)))
                surface.blit(empty_text, text_rect)

    def get_selection(self):
        return self.selected_index if self.selected_index >= 0 else None

# ═══════════════════════════════════════════════════
# PLAYER CLASS
# ═══════════════════════════════════════════════════

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = -150
        self.accel = 0
        self.width = 64
        self.height = 64
        self.normal_height = 64
        self.Gravity = 1200
        self.MAX_FALL_SPEED = 1500
        self.color = RED
        self.grounded = False
        self.bouncing = False
        self.state = "Normal"
        self.facing_direction = 1
        self.jump_key_held = False  # 점프 키 누르고 있는지 추적

        # Sliding
        self.is_sliding = False
        self.slide_timer = 0
        self.slide_duration = 0.4
        self.slide_speed = 500
        self.slide_cooldown_timer = 0
        self.slide_cooldown = 0.25

        # Dash
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 0.2
        self.dash_speed = 800

        # Charge
        self.is_charging = False
        self.charge_timer = 0

        # Weapons
        self.weapon_slots = [RocketLauncher(), Shotgun(), Revolver()]
        self.current_weapon_index = 0  # 현재 장착된 무기
        self.mouse_pos = (0, 0)  # 마우스 위치 저장
        self.camera = None  # 카메라 참조

        # Health (6칸 시스템)
        self.hp = 6
        self.max_hp = 6
        self.damage_cooldown = 0  # 무적 시간 (연속 데미지 방지)
        self.invincible_duration = 1.0  # 무적 지속시간 (초)

        # Dive system
        self.dive_cooldown = 0.0  # 현재 쿨다운 시간
        self.max_dive_cooldown = 2.5  # 쿨다운 지속시간 (초)
        self.can_dive = True  # 급강하 가능 여부

        # Combo system
        self.combo = 0  # 현재 콤보 수
        self.combo_timer = 0.0  # 콤보 유지 시간
        self.max_combo_time = 2.0  # 콤보 만료 시간 (초)

        # Hitstop system (시간 정지 효과)
        self.hitstop_timer = 0.0  # 히트스톱 지속 시간
        self.hitstop_duration = 0.4  # 히트스톱 효과 시간 (초)

        # Animation
        self.load_sprites()
        self.current_animation = "idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.07  # 프레임당 시간 (초) - 부드럽게
        self.is_moving = False  # 이동 중인지 플래그

    def load_sprites(self):
        """스프라이트 이미지 로드"""
        size = (self.width, self.height)
        self.sprites = {
            "idle": [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"Sprites/Player/LEEJAMMIN{i}.png"), size), True, False) for i in range(1, 5)],  # 1~4
            "falling": [pygame.transform.flip(pygame.transform.scale(pygame.image.load("Sprites/Player/LEEJAMMIN5.png"), size), True, False)],  # 5
            "jumping": [pygame.transform.flip(pygame.transform.scale(pygame.image.load("Sprites/Player/LEEJAMMIN6.png"), size), True, False)],  # 6
            "dagger": [pygame.transform.flip(pygame.transform.scale(pygame.image.load("Sprites/Player/LEEJAMMIN7.png"), size), True, False)],  # 7
            "rifle": [pygame.transform.flip(pygame.transform.scale(pygame.image.load("Sprites/Player/LEEJAMMIN8.png"), size), True, False)],  # 8
            "walking": [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"Sprites/Player/LEEJAMMIN{i}.png"), size), True, False) for i in range(9, 16)],  # 9~15
            "sliding": [pygame.transform.flip(pygame.transform.scale(pygame.image.load("Sprites/Player/LEEJAMMIN16.png"), size), True, False)]  # 16
        }

    def jump(self):
        if self.grounded and not self.is_sliding:
            self.velocity_y = -500
            self.grounded = False
            self.bouncing = False
            self.jump_key_held = True

    def Forcing(self, delta):
        if self.grounded:
            self.velocity_y = 0
            self.bouncing = True
            self.state = "Normal"
            self.slide_cooldown_timer = 0.5
            return
        if not self.grounded and self.can_dive:
            self.velocity_y += self.Gravity * 0.3
            self.state = "Forcing"
            self.slide_cooldown_timer = 0
            return
  
    def start_slide(self):
        if self.grounded and self.slide_cooldown_timer <= 0 and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = 0
            self.height = self.normal_height // 2

    def start_dash(self):
        if not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = 0

    def update_slide(self, delta):
        if self.is_sliding:
            self.slide_timer += delta
            self.velocity_x = self.slide_speed * self.facing_direction

            if self.slide_timer >= self.slide_duration:
                self.is_sliding = False
                self.height = self.normal_height
                self.slide_cooldown_timer = self.slide_cooldown

    def update_dash(self, delta):
        if self.is_dashing:
            self.dash_timer += delta
            self.velocity_x = self.dash_speed * self.facing_direction

            if self.dash_timer >= self.dash_duration:
                self.is_dashing = False

    def update_charge(self, delta):
        if self.is_charging:
            self.charge_timer -= delta
            if self.charge_timer <= 0:
                self.is_charging = False

    def update_weapons(self, delta):
        for weapon in self.weapon_slots:
            if weapon:
                weapon.update(delta)

    def add_weapon(self, weapon):
        for i, slot in enumerate(self.weapon_slots):
            if slot is None:
                self.weapon_slots[i] = weapon
                return
        self.weapon_slots.pop(0)
        self.weapon_slots.append(weapon)

    def remove_weapon(self, slot_index):
        """무기 슬롯에서 무기 제거"""
        if 0 <= slot_index < len(self.weapon_slots):
            self.weapon_slots[slot_index] = None
            # 현재 장착된 무기가 제거되면 다른 무기로 자동 전환
            if self.current_weapon_index == slot_index:
                # 다음 사용 가능한 무기 찾기
                for i in range(len(self.weapon_slots)):
                    if self.weapon_slots[i] is not None:
                        self.current_weapon_index = i
                        break

    def equip_weapon(self, slot_index):
        """무기를 장착 (선택)"""
        if 0 <= slot_index < len(self.weapon_slots):
            if self.weapon_slots[slot_index] is not None:
                self.current_weapon_index = slot_index

    def use_current_weapon(self, entities):
        """현재 장착된 무기 사용"""
        weapon = self.weapon_slots[self.current_weapon_index]
        if weapon:
            weapon.use(self, entities)

    def use_weapon(self, slot_index, entities):
        if 0 <= slot_index < len(self.weapon_slots):
            weapon = self.weapon_slots[slot_index]
            if weapon:
                weapon.use(self, entities)

    def switch_weapon(self, direction):
        """무기 전환 (direction: 1=다음, -1=이전)"""
        if len(self.weapon_slots) == 0:
            return

        # 현재 무기에서 direction 방향으로 이동
        self.current_weapon_index = (self.current_weapon_index + direction) % len(self.weapon_slots)

        # None이 아닌 무기 찾기 (최대 한 바퀴)
        checked = 0
        while self.weapon_slots[self.current_weapon_index] is None and checked < len(self.weapon_slots):
            self.current_weapon_index = (self.current_weapon_index + direction) % len(self.weapon_slots)
            checked += 1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def Input_Manager(self, keys, entities, delta):
        # 히트스톱 중에는 키입력 차단
        if self.hitstop_timer > 0:
            return

        # 이동 플래그 초기화
        self.is_moving = False

        if not self.is_sliding and not self.is_dashing:
            self.accel = 0
            if keys[pygame.K_a] and self.x - self.width + 22 >= 0:
                self.accel = -3000
                self.facing_direction = -1
                self.is_moving = True
            if keys[pygame.K_d] and self.x + self.width + 22 <= SCREEN_WIDTH:
                self.accel = 3000
                self.facing_direction = 1
                self.is_moving = True

        if keys[pygame.K_SPACE]:
            if self.grounded:
                # 땅에 있으면 점프
                self.jump()
            elif not self.jump_key_held:
                # 공중에서 키를 다시 누르면 낙하 메소드 실행
                self.Forcing(delta)
                self.jump_key_held = True
            elif self.velocity_y >= -100:
                # 키를 계속 누르고 있는데 낙하 중이면 낙하 메소드 실행
                self.Forcing(delta)
        else:
            # 점프 키를 떼면 플래그 리셋
            self.jump_key_held = False

        if keys[pygame.K_s] and not self.grounded:
            self.Forcing(delta)
        if keys[pygame.K_LSHIFT]:
            self.start_slide()

    def check_collision(self, platforms, camera=None):
        self.grounded = False
        player_rect = self.get_rect()

        for platform in platforms:
            platform_rect = platform.get_rect()

            if player_rect.colliderect(platform_rect):
                overlap_top = player_rect.bottom - platform_rect.top
                overlap_bottom = platform_rect.bottom - player_rect.top
                overlap_left = player_rect.right - platform_rect.left
                overlap_right = platform_rect.right - player_rect.left

                min_overlap = min(overlap_top, overlap_bottom, overlap_left, overlap_right)

                if min_overlap == overlap_top and self.velocity_y > 0:
                    # Forcing 상태에서 파괴 가능한 플랫폼(IntGrid == 1)은 튀어오르고 파괴
                    if platform.IntGrid == 1 and self.state == "Forcing" and self.velocity_y > 500:
                        self.y = platform_rect.top - self.height
                        self.velocity_y = -400  # 위로 튀어오름
                        camera.add_zoom_bounce(2, 0.1)
                        self.grounded = True
                        self.bouncing = True
                        self.state = "Normal"

                        # 쿨다운 초기화 및 콤보 증가
                        self.dive_cooldown = 0
                        self.can_dive = True
                        self.combo += 1
                        self.combo_timer = self.max_combo_time

                        platforms.remove(platform)
                        continue

                    # Forcing 상태에서 일반 플랫폼에 착지하면 튀어오름 + 쿨다운 적용
                    if self.state == "Forcing" and self.velocity_y > 500:
                        self.y = platform_rect.top - self.height
                        self.velocity_y = -400  # 위로 튀어오름
                        self.grounded = True
                        self.bouncing = True

                        # 쿨다운 적용
                        self.dive_cooldown = self.max_dive_cooldown
                        self.can_dive = False
                    # 일반 착지
                    else:
                        self.y = platform_rect.top - self.height
                        self.velocity_y = 0
                        self.grounded = True
                        self.bouncing = True
                elif min_overlap == overlap_bottom and self.velocity_y < 0:
                    self.y = platform_rect.bottom
                    self.velocity_y = 0
                elif min_overlap == overlap_left and self.velocity_x > 0:
                    self.x = platform_rect.left - self.width
                    self.velocity_x = 0
                elif min_overlap == overlap_right and self.velocity_x < 0:
                    self.x = platform_rect.right
                    self.velocity_x = 0

                self.state = 'Normal'

    def take_damage(self, damage, knockback_direction=0):
        """플레이어가 데미지를 받음"""
        if self.damage_cooldown <= 0:
            self.hp -= damage
            self.damage_cooldown = self.invincible_duration  # 무적 시간 적용

            # 넉백 효과 (강화)
            if knockback_direction != 0:
                self.velocity_x = knockback_direction * 800  # 넉백 속도 (강화)
                self.velocity_y = -400  # 위로 강하게 튕김

            # 히트스톱 효과 (시간 정지)
            self.hitstop_timer = self.hitstop_duration

            if self.hp <= 0:
                self.hp = 0

    def check_enemy_collision(self, enemies, delta):
        """몹과의 충돌 체크"""
        player_rect = self.get_rect()
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                # Forcing 상태: 몹 즉사
                if self.state == "Forcing" and self.velocity_y > 500:
                    self.combo += 1
                    enemy.instant_kill()
                # 슬라이딩 상태: 몹 넉백 (단, Tank는 제외)
                elif self.is_sliding:
                    if enemy.enemy_type != "tank":
                        knockback_direction = 1 if self.velocity_x > 0 else -1
                        enemy.apply_knockback(knockback_direction)
                    else:
                        # Tank 몹은 슬라이딩을 막고, 플레이어가 데미지 (넉백)
                        knockback_dir = -1 if self.velocity_x > 0 else 1
                        self.take_damage(1, knockback_dir)
                # 일반 상태: 플레이어가 데미지 (1칸)
                else:
                    # 넉백 방향 계산 (몹 위치 기준으로 플레이어 밀어냄)
                    knockback_dir = -1 if enemy.x < self.x else 1
                    self.take_damage(1, knockback_dir)

    def update_animation(self, delta):
        """애니메이션 업데이트"""
        # 이전 애니메이션 저장
        previous_animation = self.current_animation

        # 상태에 따라 애니메이션 결정
        weapon = self.weapon_slots[self.current_weapon_index]

        # 무기 사용 중 애니메이션 (최우선)
        if weapon and weapon.cooldown_timer > weapon.cooldown * 0.5:
            if isinstance(weapon, Dagger):
                self.current_animation = "dagger"
            elif isinstance(weapon, Rifle):
                self.current_animation = "rifle"
        # 슬라이딩 애니메이션
        elif self.is_sliding:
            self.current_animation = "sliding"
        # 공중 애니메이션 - 점프/낙하 통합
        elif not self.grounded and abs(self.velocity_y) > 50:
            self.current_animation = "jumping"
        # 걷기 애니메이션 - 이동 키를 누르고 있을 때만
        elif self.is_moving:
            self.current_animation = "walking"
        # 대기 애니메이션
        else:
            self.current_animation = "idle"

        # 애니메이션이 바뀌면 프레임 리셋
        if previous_animation != self.current_animation:
            self.animation_frame = 0
            self.animation_timer = 0

        # 프레임 업데이트
        self.animation_timer += delta
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.sprites[self.current_animation]
            self.animation_frame = (self.animation_frame + 1) % len(frames)

    def broUpdate_Screen(self, delta, platforms, camera, enemies=None):
        if self.slide_cooldown_timer > 0:
            self.slide_cooldown_timer -= delta

        if self.damage_cooldown > 0:
            self.damage_cooldown -= delta

        # 히트스톱 타이머 감소
        if self.hitstop_timer > 0:
            self.hitstop_timer -= delta
            if self.hitstop_timer <= 0:
                self.hitstop_timer = 0

        # 급강하 쿨다운 감소
        if self.dive_cooldown > 0:
            self.dive_cooldown -= delta
            if self.dive_cooldown <= 0:
                self.dive_cooldown = 0
                self.can_dive = True

        # 콤보 타이머 감소
        if self.combo > 0:
            self.combo_timer -= delta
            if self.combo_timer <= 0:
                self.combo = 0

        self.update_slide(delta)
        self.update_dash(delta)
        self.update_charge(delta)
        self.update_weapons(delta)
        self.update_animation(delta)

        if not self.is_sliding and not self.is_dashing:
            self.velocity_x += self.accel * delta
            self.velocity_x *= 0.9

        self.velocity_y += self.Gravity * delta
        self.velocity_y = min(self.velocity_y, self.MAX_FALL_SPEED)

        self.x += self.velocity_x * delta
        self.check_collision(platforms, camera)

        self.y += self.velocity_y * delta
        self.check_collision(platforms, camera)

        # 몹과의 충돌 체크
        if enemies:
            self.check_enemy_collision(enemies, delta)

    def draw(self, surface, camera):
        screen_y = camera.DrawAgain(self.y)

        # 현재 애니메이션의 현재 프레임 가져오기
        frames = self.sprites[self.current_animation]
        current_sprite = frames[self.animation_frame]

        # 좌우 반전 (facing_direction에 따라)
        if self.facing_direction < 0:
            current_sprite = pygame.transform.flip(current_sprite, True, False)

        # 데미지 받을 때 깜박임 효과
        if self.damage_cooldown > 0 and int(self.damage_cooldown * 10) % 2 == 0:
            # 흰색으로 변경 (피격 효과)
            white_sprite = current_sprite.copy()
            white_sprite.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(white_sprite, (self.x, screen_y))
        else:
            surface.blit(current_sprite, (self.x, screen_y))

        # 무기 인디케이터
        weapon_y = screen_y - 20
        for i, weapon in enumerate(self.weapon_slots):
            weapon_x = self.x + i * 15
            if weapon:
                # 현재 장착된 무기는 노란색, 쿨다운 중이면 회색, 아니면 파란색
                if i == self.current_weapon_index:
                    color = YELLOW if weapon.can_use() else ORANGE
                    radius = 7  # 장착된 무기는 더 크게
                else:
                    color = BLUE if weapon.can_use() else GRAY
                    radius = 5
                pygame.draw.circle(surface, color, (int(weapon_x), int(weapon_y)), radius)

# ═══════════════════════════════════════════════════
# HUD DRAWING
# ═══════════════════════════════════════════════════

def draw_health_hud(surface, player):
    """플레이어 체력 HUD 그리기 (오른쪽 상단, 6칸 시스템)"""
    # HUD 위치 (화면 오른쪽 상단)
    base_x = SCREEN_WIDTH - 20
    base_y = 30

    # 각 칸의 크기
    cell_width = 40
    cell_height = 25
    cell_gap = 4

    # 전체 너비 계산 (6칸 + 5개의 간격)
    total_width = cell_width * 6 + cell_gap * 5

    # 시작 위치 (오른쪽 정렬)
    start_x = base_x - total_width

    # 배경 박스
    bg_rect = pygame.Rect(start_x - 5, base_y - 5, total_width + 10, cell_height + 10)

    # 무적 시간일 때 배경색 변경
    if player.damage_cooldown > 0:
        bg_color = (100, 100, 0)  # 노란빛 배경
        border_color = YELLOW
    else:
        bg_color = (40, 40, 40)
        border_color = WHITE

    pygame.draw.rect(surface, bg_color, bg_rect)
    pygame.draw.rect(surface, border_color, bg_rect, 3)

    # 각 칸 그리기
    for i in range(6):
        cell_x = start_x + i * (cell_width + cell_gap)
        cell_rect = pygame.Rect(cell_x, base_y, cell_width, cell_height)

        # 체력이 남아있는 칸은 빨간색, 없는 칸은 어두운 회색
        if i < player.hp:
            color = RED
        else:
            color = (60, 60, 60)

        pygame.draw.rect(surface, color, cell_rect)
        pygame.draw.rect(surface, border_color, cell_rect, 2)

    # 체력 텍스트 (중앙에 표시)
    font = pygame.font.Font(None, 32)
    hp_text = font.render(f"{player.hp}/{player.max_hp}", True, WHITE)
    text_rect = hp_text.get_rect(center=(start_x + total_width // 2, base_y + cell_height // 2))

    # 텍스트 배경 (가독성)
    text_bg = pygame.Rect(text_rect.x - 3, text_rect.y - 1, text_rect.width + 6, text_rect.height + 2)
    pygame.draw.rect(surface, BLACK, text_bg)

    surface.blit(hp_text, text_rect)

    # 무적 시간 표시 (박스 아래)
    if player.damage_cooldown > 0:
        invincible_font = pygame.font.Font(None, 24)
        invincible_text = invincible_font.render(f"무적: {player.damage_cooldown:.1f}s", True, YELLOW)
        invincible_rect = invincible_text.get_rect(topright=(base_x, base_y + cell_height + 15))
        surface.blit(invincible_text, invincible_rect)

def draw_weapon_hud(surface, player):
    """화면 하단 무기 UI (왼쪽 하단)"""
    weapon = player.weapon_slots[player.current_weapon_index]
    if not weapon:
        return

    base_x = 20
    base_y = SCREEN_HEIGHT - 80

    # 무기 이름 표시
    font = pygame.font.Font(None, 48)
    weapon_name = font.render(weapon.name, True, WHITE)
    surface.blit(weapon_name, (base_x, base_y))

    # 탄약 시스템이 있는 무기만 표시
    if weapon.ammo >= 0:
        ammo_y = base_y + 50

        # 탄약 텍스트
        ammo_font = pygame.font.Font(None, 36)
        if weapon.is_reloading:
            ammo_text = ammo_font.render(f"재장전 중... {weapon.reload_timer:.1f}s", True, ORANGE)
        else:
            ammo_text = ammo_font.render(f"{weapon.ammo}/{weapon.max_ammo}", True, YELLOW)
        surface.blit(ammo_text, (base_x, ammo_y))

        # 탄약 바 (가로)
        bar_x = base_x + 200
        bar_y = ammo_y + 5
        bar_width = 200
        bar_height = 20

        # 배경
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # 채워진 부분
        if weapon.is_reloading:
            # 재장전 진행도
            progress = 1 - (weapon.reload_timer / weapon.reload_time)
            fill_color = ORANGE
        else:
            # 남은 탄약 비율
            progress = weapon.ammo / weapon.max_ammo
            fill_color = YELLOW if progress > 0.3 else RED

        fill_width = int(bar_width * progress)
        pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

# ═══════════════════════════════════════════════════
# PLATFORM GENERATOR
# ═══════════════════════════════════════════════════

class PlatformGenerator:
    def __init__(self):
        self.platforms = []
        self.last_y = 0
        self.min_gap_y = 70
        self.max_gap_y = 170
        self.min_width = 50
        self.max_width = 500
        self.platformchoice = random.randint(1, 100)
        self.breakablespawn = 40
        self.started = False

        self.create_initial_platforms()

    def create_initial_platforms(self):
        initial_y = SCREEN_HEIGHT // 4
        platform_width = SCREEN_WIDTH // 2 - 100
        height = 20

        left_platform = Platform(0, initial_y, platform_width, height)
        self.platforms.append(left_platform)

        right_platform = Platform(SCREEN_WIDTH // 2 + 100, initial_y, platform_width, height)
        self.platforms.append(right_platform)

    def generate(self):
        self.last_y += random.randint(self.min_gap_y, self.max_gap_y)
        width = random.randint(self.min_width, self.max_width)
        x = random.randint(0, max(0, SCREEN_WIDTH - width))
        height = 20

        if self.platformchoice >= self.breakablespawn:
            platform = Platform(x, self.last_y, width, height)
            self.platforms.append(platform)
        else:
            Breakplatform = BreakablePlatform(x, self.last_y, width, height)
            self.platforms.append(Breakplatform)
        self.platformchoice = random.randint(1, 100)

    def update(self, camera_y, player_y, camera):
        initial_platform_y = SCREEN_HEIGHT // 4
        if player_y > initial_platform_y + 50 and not self.started:
            self.started = True
            self.last_y = initial_platform_y
            camera.activate()
            camera.lock_player = True  # DOWNWELL 스타일 플레이어 추적 활성화

        for platform in self.platforms[:]:
            screen_y = platform.y + camera_y
            if screen_y < -100:
                self.platforms.remove(platform)

        if self.started:
            if len(self.platforms) == 0:
                self.generate()
            else:
                last_screen_y = self.platforms[-1].y + camera_y
                if last_screen_y < SCREEN_HEIGHT + 200:
                    self.generate()

    def draw(self, surface, camera):
        for platform in self.platforms:
            screen_y = camera.DrawAgain(platform.y)
            pygame.draw.rect(surface, platform.color, (platform.x, screen_y, platform.width, platform.height))

# ═══════════════════════════════════════════════════
# TITLE MAKER
# ═══════════════════════════════════════════════════

class TitleMaker:
    def __init__(self, T, x, y, color):
        self.T = T
        self.typespeed = 50
        self.color = color
        self.font = pygame.font.Font(None, 36)
        self.x = x
        self.y = y
        self.current_index = 0
        self.last_update = pygame.time.get_ticks()

    def text_typing(self, surface, direction):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.typespeed:
            self.current_index += direction
            self.last_update = current_time

            if self.current_index > len(self.T):
                self.current_index = len(self.T)
            elif self.current_index < 0:
                self.current_index = 0

        text = self.T[:self.current_index]
        text_surface = self.font.render(text, True, self.color)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x, self.y)
        surface.blit(text_surface, text_rect)

    def text_reset(self):
        self.current_index = 0

# ═══════════════════════════════════════════════════
# DEPTH TRACKER & WEAPON SELECTION
# ═══════════════════════════════════════════════════

class DepthTracker:
    def __init__(self):
        self.depth = 0
        self.last_checkpoint = 0
        self.checkpoint_interval = 2000  # 50km마다 무기 선택aaa

    def update(self, camera_y):
        self.depth = abs(camera_y)
        return self.depth // self.checkpoint_interval > self.last_checkpoint // self.checkpoint_interval

    def mark_checkpoint(self, camera_y):
        self.last_checkpoint = abs(camera_y)

class WeaponSelectionScreen:
    def __init__(self, weapon_pool):
        self.active = False
        self.weapons = []
        self.weapon_pool = weapon_pool
        self.font = pygame.font.Font(None, 48)

    def activate(self):
        self.active = True
        self.weapons = random.sample(self.weapon_pool, min(3, len(self.weapon_pool)))

    def draw(self, surface):
        if not self.active:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        title = self.font.render("Choose a Weapon", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)

        for i, weapon in enumerate(self.weapons):
            y_pos = 200 + i * 100
            text = self.font.render(f"{i+1}. {weapon.name} ({weapon.weapon_type})", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
            surface.blit(text, text_rect)

    def select(self, choice, player):
        if 0 <= choice < len(self.weapons):
            selected_weapon = self.weapons[choice]
            weapon_instance = type(selected_weapon)()
            player.add_weapon(weapon_instance)
            self.active = False
            return True
        return False

class StartScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.blink_timer = 0
        self.show_text = True

    def draw(self, surface):
        surface.fill(BLACK)

        # 게임 타이틀
        title = self.title_font.render("RE:Venture", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(title, title_rect)

        # 깜빡이는 시작 안내
        if self.show_text:
            start_text = self.subtitle_font.render("Press SPACE to Start", True, GRAY)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            surface.blit(start_text, start_rect)

    def update(self, delta):
        self.blink_timer += delta
        if self.blink_timer >= 0.5:
            self.show_text = not self.show_text
            self.blink_timer = 0

class GameOverScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.blink_timer = 0
        self.show_text = True
        self.active = False

    def activate(self):
        self.active = True

    def draw(self, surface):
        if not self.active:
            return

        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        surface.blit(overlay, (0, 0))

        # GAME OVER 텍스트
        title = self.title_font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        surface.blit(title, title_rect)

        # 깜빡이는 재시작 안내
        if self.show_text:
            restart_text = self.subtitle_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(restart_text, restart_rect)

            quit_text = self.subtitle_font.render("Press ESC to Quit", True, GRAY)
            quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            surface.blit(quit_text, quit_rect)

    def update(self, delta):
        self.blink_timer += delta
        if self.blink_timer >= 0.5:
            self.show_text = not self.show_text
            self.blink_timer = 0

# ═══════════════════════════════════════════════════
# GAME INITIALIZATION
# ═══════════════════════════════════════════════════

leejammin = Player(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 4 - 50)
MainCamera = Camera()
leejammin.camera = MainCamera  # 플레이어에게 카메라 참조 전달
platformGen = PlatformGenerator()
Stage1 = TitleMaker("Stage 1", SCREEN_WIDTH // 2, SCREEN_HEIGHT-150, WHITE)
Entitle = TitleMaker("Underneath", SCREEN_WIDTH // 2, SCREEN_HEIGHT-200, WHITE)

entities = []
depth_tracker = DepthTracker()
enemy_spawner = EnemySpawner()

weapon_pool = [Dagger(), Rifle(), BoostBoots(), CircularSaw(), HealthPotion(), Revolver(), RocketLauncher(), Shotgun()]
weapon_selection = WeaponSelectionScreen(weapon_pool)
start_screen = StartScreen()
game_over_screen = GameOverScreen()

BroGaming = True
game_started = False
game_over = False
start_time = pygame.time.get_ticks()

# ═══════════════════════════════════════════════════
# GAME LOOP
# ═══════════════════════════════════════════════════

while BroGaming:
    delta = clock.tick(FPS) / 1000

    # 시작 화면 처리
    if not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                BroGaming = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_started = True
                    start_time = pygame.time.get_ticks()  # 게임 시작 시간 재설정

        start_screen.update(delta)
        start_screen.draw(screen)
        pygame.display.flip()
        continue

    # 게임 진행 중
    check_t = pygame.time.get_ticks() - start_time
    mouse_pos = pygame.mouse.get_pos()
    leejammin.mouse_pos = mouse_pos  # 마우스 위치 먼저 업데이트

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            BroGaming = False

        if event.type == pygame.KEYDOWN:
            # 게임 오버 화면에서 키 처리
            if game_over:
                if event.key == pygame.K_r:
                    # 게임 재시작
                    game_over = False
                    game_over_screen.active = False
                    leejammin = Player(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 4 - 50)
                    MainCamera = Camera()
                    leejammin.camera = MainCamera
                    platformGen = PlatformGenerator()
                    entities = []
                    depth_tracker = DepthTracker()
                    enemy_spawner = EnemySpawner()
                    start_time = pygame.time.get_ticks()
                elif event.key == pygame.K_ESCAPE:
                    BroGaming = False

            # Z키: 이전 무기로 전환
            if event.key == pygame.K_z and not weapon_selection.active and not game_over and leejammin.hitstop_timer <= 0:
                leejammin.switch_weapon(-1)

            # C키: 다음 무기로 전환
            if event.key == pygame.K_c and not weapon_selection.active and not game_over and leejammin.hitstop_timer <= 0:
                leejammin.switch_weapon(1)

            if weapon_selection.active:
                if event.key == pygame.K_1:
                    weapon_selection.select(0, leejammin)
                elif event.key == pygame.K_2:
                    weapon_selection.select(1, leejammin)
                elif event.key == pygame.K_3:
                    weapon_selection.select(2, leejammin)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not weapon_selection.active and not game_over and leejammin.hitstop_timer <= 0:
                # 좌클릭으로 현재 장착된 무기 사용 (히트스톱 중에는 불가)
                if event.button == 1:  # Left click
                    leejammin.use_current_weapon(entities)

    # 게임 오버가 아닐 때만 게임 업데이트
    if not game_over and not weapon_selection.active:
        keys = pygame.key.get_pressed()
        leejammin.Input_Manager(keys, entities, delta)
        leejammin.broUpdate_Screen(delta, platformGen.platforms, MainCamera, enemy_spawner.enemies)
        MainCamera.CameraChase(delta, leejammin)
        MainCamera.update_zoom(delta)
        platformGen.update(MainCamera.y, leejammin.y, MainCamera)

        # Update entities (히트스톱 중에는 업데이트 안 함)
        if leejammin.hitstop_timer <= 0:
            for entity in entities[:]:

                if isinstance(entity, LaserBeam) and hasattr(entity, 'needs_raycast'):
                    entity.raycast(enemy_spawner.enemies, platformGen.platforms)
                    delattr(entity, 'needs_raycast')

                # BounceBullet 플랫폼 충돌 체크
                if isinstance(entity, BounceBullet):
                    entity.check_platform_collision(platformGen.platforms)

                # Rocket 충돌 및 트레일 생성
                if isinstance(entity, Rocket):
                    rocket_rect = entity.get_rect()
                    # 플랫폼과 충돌
                    for platform in platformGen.platforms:
                        if rocket_rect.colliderect(platform.get_rect()):
                            entity.explode(entities)
                            break
                    # 적과 충돌
                    for enemy in enemy_spawner.enemies[:]:
                        if rocket_rect.colliderect(enemy.get_rect()):
                            entity.explode(entities)
                            enemy.instant_kill()
                            break

                # Explosion 플레이어 및 적 충돌 체크
                if isinstance(entity, Explosion):
                    entity.check_player_in_range(leejammin)
                    entity.check_enemies_in_range(enemy_spawner.enemies)

                # 엔티티 업데이트 (Rocket은 트레일 생성)
                if isinstance(entity, Rocket):
                    trail = entity.update(delta)
                    if trail:
                        entities.append(trail)
                else:
                    entity.update(delta)
                if not entity.active:
                    entities.remove(entity)

            # Update enemies
            enemy_spawner.update(delta, MainCamera.y)
            enemy_spawner.update_enemies(delta, leejammin, platformGen.platforms, entities)

        # Check for weapon selection checkpoint
        if depth_tracker.update(MainCamera.y):
            weapon_selection.activate()
            depth_tracker.mark_checkpoint(MainCamera.y)
            MainCamera.scrolling += 25
            platformGen.max_gap_y += 25
            platformGen.breakablespawn += 5

    MainCamera.draw_bg(MainCamera.render_surface)
    platformGen.draw(MainCamera.render_surface, MainCamera)

    for entity in entities:
        entity.draw(MainCamera.render_surface, MainCamera)

    enemy_spawner.draw(MainCamera.render_surface, MainCamera)
    leejammin.draw(MainCamera.render_surface, MainCamera)
    screen_y = MainCamera.DrawAgain(leejammin.y)

    # Title text (게임 오버가 아닐 때만)
    if not game_over:
        if check_t < 5 * SEC_CONST:
            Stage1.text_typing(MainCamera.render_surface, 1)
            if check_t > 1 * SEC_CONST:
                Entitle.text_typing(MainCamera.render_surface, 1)
        else:
            Stage1.text_typing(MainCamera.render_surface, -1)
            Entitle.text_typing(MainCamera.render_surface, -1)
    
    MainCamera.zooming(screen)

    # 히트스톱 효과 (시각적 피드백)
    if leejammin.hitstop_timer > 0:
        # 카메라 줌 효과
        MainCamera.add_zoom_bounce(1.15, leejammin.hitstop_timer)

        # 화면 흑백 효과
        grayscale_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        grayscale_overlay.fill((200, 200, 200))
        grayscale_overlay.set_alpha(int(100 * (leejammin.hitstop_timer / leejammin.hitstop_duration)))
        screen.blit(grayscale_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # 체력 HUD 표시 (게임 오버가 아닐 때만)
    if not game_over:
        draw_health_hud(screen, leejammin)
        draw_weapon_hud(screen, leejammin)

    # Combo UI 표시 (오른쪽 상단, 체력 아래)
    if leejammin.combo > 0 and not game_over:
        combo_y_start = 110

        # 콤보 텍스트
        combo_font = pygame.font.Font(None, 48)
        combo_text = combo_font.render(f"COMBO x{leejammin.combo}", True, YELLOW)
        combo_rect = combo_text.get_rect(topright=(SCREEN_WIDTH - 80, combo_y_start))
        screen.blit(combo_text, combo_rect)

        # 콤보 지속시간 바
        bar_x = SCREEN_WIDTH - 80 - 200
        bar_y = combo_y_start + 40
        bar_width = 200
        bar_height = 15

        # 배경 (회색)
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # 진행도 계산
        progress = leejammin.combo_timer / leejammin.max_combo_time

        # 채워진 부분 (노란색 -> 빨간색으로 변화)
        fill_width = int(bar_width * progress)
        if progress > 0.5:
            bar_color = YELLOW
        elif progress > 0.25:
            bar_color = ORANGE
        else:
            bar_color = RED
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_width, bar_height))

        # 테두리
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

    # Dive 쿨다운 표시 (오른쪽 상단)
    if leejammin.dive_cooldown > 0 and not game_over:
        dive_y = 180 if leejammin.combo > 0 else 110
        cooldown_font = pygame.font.Font(None, 32)
        cooldown_text = cooldown_font.render(f"DIVE: {leejammin.dive_cooldown:.1f}s", True, RED)
        cooldown_rect = cooldown_text.get_rect(topright=(SCREEN_WIDTH - 80, dive_y))
        screen.blit(cooldown_text, cooldown_rect)

    # Weapon selection screen
    weapon_selection.draw(screen)

    if game_over:
        game_over_screen.update(delta)
        game_over_screen.draw(screen)
    
    # Game over check (DOWNWELL 스타일: 위로만 벗어나면 게임 오버)
    if screen_y <= 0 or leejammin.hp <= 0:
        if not weapon_selection.active and not game_over:
            game_over = True
            game_over_screen.activate()

    pygame.display.flip()

pygame.quit()
sys.exit()
