'''
뭐가 AI고 뭐가 사람인지 확실히 봐라
AI
- 성수위한패키지다운로드 - 무슨 메소드 써야 하는지 AI가 알려줌
- 기본적 틀 ( 그리기는 draw 함수로 이름 정해야 일관성 있고 이뻐진다, 게임 루프에서 실시간 반복은 update로 정해야 이뻐진다...)
- 서브스텝 알고리즘 ( 나눠서 충돌 검사하는거 )
- UIManager ( 어캐만드냐 )

인간
- 상태 머신 ( 클래스로 묶어서 관리함 ㅅㄱ -> 게임 루프마다 바꾸면서 상태 변했는지 체크 )
- json으로 컷씬 관리하기 ( 아이디어 낸 자한테 박수111111 )
- 플레이어 이동, 플랫폼 생성, 카메라 ( AI가 만든 줄 알었지? - 월드 좌표 / 화면 좌표 개념과 공식은 AI가 알려줌 )
'''

import subprocess
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def sungsoo_wihan_package_downloader(package):
    try:
        __import__(package)
        print("이 게임은 pygame-ce 기반입니다. pygame을 지우고 pygame-ce로 주입합니다.")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame-ce"])
    except ImportError:
        print("파이게임CE가 설치되어있지 않군요! 파이게임CE를 주입합니다.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame-ce"])
        print("파이게임CE 설치 완료!")
    finally:
        print("파이게임CE가 설치되어 있군요! 잘했네~")
    
    print('게임 에셋을 다운로드합니다.')
    url = "https://raw.githubusercontent.com/Enterprisdma/Re-Venture/main"
    assets = [
        "Sprites/Object/CompanyLogo.png",
        "Sprites/Object/RE-Venture.png",
        "Sprites/Object/Platforms/BreakablePlatform/BreakablePlatform.png",
        "Sprites/Object/Platforms/NormalPlatform/NormalPlatform.png",
        "Font/DNFForgedBlade-Medium.ttf",
        "Sprites/Backgrounds/5km.png",
        "CutsceneData/cutscene_data.json",
    ]

    assets += [f"Sprites/Backgrounds/Main{i}.png" for i in range(1, 5)]
    assets += [f"Sprites/Cutscene/StartCutscene{i}.png" for i in range(1, 3)]
    assets += [f"Sprites/Player/LEEJAMMIN{i}.png" for i in range(1, 17)]
    assets += [f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png" for i in range(1, 11)]

    import urllib.request
    import os

    for asset in assets:
        if not os.path.exists(asset):
            print(asset)
            target_url = f"{url}/{asset}"
            os.makedirs(os.path.dirname(asset), exist_ok=True)

            try:
                urllib.request.urlretrieve(target_url, asset)
                print(f" {asset} 다운로드 성공")
            except Exception as e:
                print(f" {asset} 다운로드 실패")


    print('완벽합니다.')


sungsoo_wihan_package_downloader("pygame")

import pygame  # noqa: E402
import pygame.gfxdraw # noqa: E402
import math  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402

pygame.init()

SCREEN_WIDTH = 1140
SCREEN_HEIGHT = 852
FPS = 60
icon = pygame.image.load("Sprites/Object/CompanyLogo.png")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RE:Venture")
clock = pygame.time.Clock()
pygame.display.set_icon(icon)

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

# 메인 클래스

# UI들

class LogoShow:
    def __init__(self):
        logo = pygame.image.load("Sprites/Object/CompanyLogo.png")
        ScaleW = int(SCREEN_WIDTH * 0.2)
        ScaleH = int(SCREEN_HEIGHT * 0.27)


        self.logo = pygame.transform.scale(logo, (ScaleW, ScaleH))

        self.x = SCREEN_WIDTH // 2 - self.logo.get_width() // 2
        self.y = SCREEN_HEIGHT // 2 - self.logo.get_height() // 2

        self.timer = 0
        self.duration = 4.0
        self.fade_in = 1.0
        self.fade_out = 1.0

        self.transparent = 0
        self.active = True
        
        self.fading = UIManager(duration=1.0)

    def update(self, delta):
        self.timer += delta

        if self.timer < self.fade_in:
            self.transparent = self.fading.fadein(delta)

        elif self.timer < self.duration - self.fade_out:
            self.transparent = 255
            if self.timer < self.duration - self.fade_out - 0.01:
                self.fading.reset_timer()
        
        elif self.timer < self.duration:
            self.transparent = self.fading.fadeout(delta)

        else:
            self.transparent = 0
            self.active = False
        
    def draw(self):
        screen.fill(BLACK)

        temp_logo = self.logo.copy()
        temp_logo.set_alpha(self.transparent)
        screen.blit(temp_logo, (self.x, self.y))

    def finished(self):
        return not self.active

class CutsceneBase:
    def __init__(self, images, duration, text):
        self.duration = duration
        self.images = []
        self.font = pygame.font.Font("Font/DNFForgedBlade-Medium.ttf", 32)

        if isinstance(images, list):
            for img in images:
                if isinstance(img, str):
                    buffer = pygame.image.load(img)
                    scaled = pygame.transform.scale(buffer, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    self.images.append(scaled)
                else:
                    raise ValueError
        
        self.timer = 0
        self.index = 0
        self.text_index = 0
        self.text_show_index = 0
        self.active = True
        self.Text = text
        self.text_placeholder = []

    def update(self, delta):
        if not self.active:
            return
        
        self.timer += delta

        self.text_show_duration = 0.03

        if len(self.text_placeholder) < len(self.Text[self.text_index]):
            if self.timer >= self.text_show_duration:
                self.text_placeholder.append(
                    self.Text[self.text_index][self.text_show_index]
                )
                self.text_show_index += 1
                self.timer = 0

        if self.timer >= self.duration:
            self.index += 1
            self.text_index += 1
            self.timer = 0
            self.text_show_index = 0
            self.text_placeholder = []

            screen.fill(BLACK)

            if self.index >= len(self.images):
                self.active = False
    
    def draw(self):
        if self.active and 0 <= self.index < len(self.images):
            screen.blit(
                self.images[self.index],
                (
                    (SCREEN_WIDTH - self.images[self.index].get_width()) / 2,
                    (SCREEN_HEIGHT - self.images[self.index].get_height()) / 2.5
                )
            )

            show_text = self.font.render(''.join(map(str, self.text_placeholder)), True, WHITE)
            screen.blit(
                show_text,
                (
                    (SCREEN_WIDTH - show_text.get_width()) / 2,
                    (SCREEN_HEIGHT - show_text.get_height()) / 1.25
                )
            )
    
    def ended(self):
        return not self.active

class StartMenu:
    def __init__(self):
        self.game_logo = pygame.image.load("Sprites/Object/CompanyLogo.png")
        self.backgrounds = {
            "Main": [
                pygame.image.load(f"Sprites/Backgrounds/Main{i}.png")
                for i in range(1, 5)
            ]
        }

        self.normal_size = 32
        self.min_size = 32
        self.max_size = 48

        self.game_logo = pygame.image.load("Sprites/Object/RE-Venture.png")
        self.font = pygame.font.Font(None, self.normal_size)
        self.text = "Press Space to Start"

        self.blinking = UIManager(0.25)
        self.fillactive = False
        self.frame_refresh = 0.1
        self.blink_duration = 1
        self.current_frame = 0

        self.timer = 0
        self.total_timer = 0
    
    def update(self, delta):
        mouse_pos = pygame.mouse.get_pos()
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )

        padding = 20
        box_rect = text_rect.inflate(padding*10, padding*2)

        self.total_timer += delta
        self.timer += delta

        if self.total_timer < self.blink_duration:
            self.fillactive = self.blinking.blink(delta)
        else:
            self.fillactive = False

        if self.timer >= self.frame_refresh:
            self.current_frame += 1
            self.timer = 0

            if self.current_frame >= len(self.backgrounds["Main"]):
                self.current_frame = 0
        
        if box_rect.collidepoint(mouse_pos):
            if (self.normal_size <= self.max_size):
                self.normal_size += 2
        else:
            if self.normal_size >= self.min_size:
                self.normal_size -= 2
        self.font = pygame.font.Font(None, self.normal_size)



    
    def draw(self):
        Filling = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        current_bg = self.backgrounds["Main"][self.current_frame]
        screen.blit(current_bg, (-350, 0))

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )

        logo_x = SCREEN_WIDTH // 2 - self.game_logo.get_width() // 2
        logo_y = SCREEN_HEIGHT // 4 - self.game_logo.get_height() // 2

        screen.blit(self.game_logo, (logo_x, logo_y))
        padding = 20
        box_rect = text_rect.inflate(padding * 10, padding * 2)
        pygame.draw.rect(screen, BLACK, box_rect)
        pygame.draw.rect(screen, WHITE, box_rect, 3)
        screen.blit(text_surface, text_rect)

        if self.fillactive:
            Filling.fill(BLACK)
            Filling.set_alpha(255)
            screen.blit(Filling, (0, 0))

class Camera:
    def __init__(self, screen_size):
        self.screen_size = screen_size
        self.zoom = 1.1
        self.speed = 1.25
        self.timer = 0.0
        self.bouncing = True
        self.cycle_duration = 0.25

        self.scroll_active = False
        self.scrolling_speed = 150
        self.camera_y = 0
        self.bg = pygame.image.load("Sprites/Backgrounds/5km.png")
        self.bg_height = self.bg.get_height()

        self.active = False
    
    def bg_cycle(self, surface):
        bg_y = self.camera_y % self.bg_height
        surface.blit(self.bg, (0, bg_y))
        surface.blit(self.bg, (0, bg_y - self.bg_height))
    
    def camera_chase(self, delta, player=None):
        if self.active:

            if self.scroll_active:
                self.camera_y -= self.scrolling_speed * delta

            if player:
                border = SCREEN_HEIGHT * 0.65
                player_screen_y = self.draw_again(player)

                if player_screen_y >= border:
                    set_y = -(player.y - border)
                    self.camera_y = set_y
                
            if self.scroll_active:
                self.camera_y -= self.scrolling_speed * delta

    
    def draw_again(self, entity): # 카메레에 그리기
        return entity.y + self.camera_y

    def update(self, dt):
        if self.bouncing:
            self.timer += dt * self.speed
            progress = (self.timer % self.cycle_duration) / self.cycle_duration
            self.zoom = 1.1 - 0.1 * progress

    def apply(self, surf):
        w, h = self.screen_size
        sw, sh = int(w * self.zoom), int(h * self.zoom)
        surf_zoomed = pygame.transform.smoothscale(surf, (sw, sh))
        L, t = (sw - w) // 2, (sh - h) // 2
        subs = surf_zoomed.subsurface((L, t, w, h)).copy()
        return subs

# 플레이어

def load_sprites(path, size, flip=False):
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, size)

    if flip:
        img = pygame.transform.flip(img, True, False)
    return img
    
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_velocity = 0
        self.y_velocity = 0
        self.gravity = 8000
        self.max_fall_speed = 10000
        self.accel = 0
        self.is_moving = False
        self.width = 64
        self.height = 64
        self.grounded = False
        self.state = "grounded" # "Forcing", "stunned", "sliding", "falling"
        self.diving = False
        self.bouncing = False
        self.can_dive = True
        self.facing = 1
        self.iswarped = False
        self.jump_key_held = False

        self.slide_timer = 0
        self.slide_holding = False
        self.sliding_velocity = 5000

        self.current_weapon = "rifle"

        self.load_sprites()

    def load_sprites(self):
        size = (self.width, self.height)
        self.sprites = {
            "idle":[load_sprites(f"Sprites/Player/LEEJAMMIN{i}.png", size) for i in range(1, 5)],
            "falling":[load_sprites("Sprites/Player/LEEJAMMIN5.png", size)],
            "jumping":[load_sprites("Sprites/Player/LEEJAMMIN6.png", size)],
            "dagger":[load_sprites("Sprites/Player/LEEJAMMIN7.png", size)],
            "rifleshoot":[load_sprites("Sprites/Player/LEEJAMMIN8.png", size)],
            "walking":[load_sprites(f"Sprites/Player/LEEJAMMIN{i}.png", size) for i in range(9, 16)],
            "sliding":[load_sprites("Sprites/Player/LEEJAMMIN16.png", size)]
        }

    def jump(self):
        if self.grounded:
            self.y_velocity = -1500
            self.grounded = False
            self.bouncing = False
            self.jump_key_held = True
        
    def Forcing(self):
        if self.grounded:
            self.y_velocity = 0
            self.bouncing  = True
            self.state = "grounded"
            self.diving = False
            return
        elif not self.grounded and self.can_dive:
            self.y_velocity += self.gravity * 0.3
            self.state = "forcing"
            self.diving = not self.bouncing
            self.slide_cooldown_timer = 0
            return
        
    def input_manager(self, keys):
        self.is_moving = False
        self.accel = 0
        if keys[pygame.K_a]:
            self.accel = -10000
            self.is_moving = True
            self.facing = -1
        elif keys[pygame.K_d]:
            self.accel = 10000
            self.is_moving = True
            self.facing = 1
            
        if keys[pygame.K_SPACE]:
            if self.grounded:
                self.jump()
            elif not self.jump_key_held:
                self.Forcing()
                self.jump_key_held = True
            elif self.y_velocity >= -100: 
                self.Forcing()
        else:
            self.jump_key_held = False

    def check_platform_collision(self, platforms, debris_list):
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
    
        for platform in platforms:
            platform_rect = platform.get_rect()

            if player_rect.colliderect(platform_rect):
                if self.state == "forcing":
                    self.state = "forcing"
                else:
                    self.state = "grounded"

                top_overlap = player_rect.bottom - platform_rect.top
                bottom_overlap = platform_rect.bottom - player_rect.top
                left_overlap = player_rect.right - platform_rect.left
                right_overlap = platform_rect.right - player_rect.left

                real_overlap = min(top_overlap, bottom_overlap, left_overlap, right_overlap)
    
                if real_overlap == top_overlap and self.y_velocity >= 0:
                    if self.state == "forcing" and isinstance(platform, BreakablePlatform):
                        platform.break_platform(debris_list)
                        self.y_velocity = -1000
                        print('OK')
                        return True
                    if self.y_velocity > 0:
                        self.y = platform_rect.top - self.height
                        self.y_velocity = 0
                    self.grounded = True
                    self.diving = False
                    return True
                elif real_overlap == bottom_overlap and self.y_velocity < 0:
                    self.y = platform_rect.bottom
                    self.y_velocity = 0
                    return True
                elif real_overlap == left_overlap and self.x_velocity > 0:
                    self.x = platform_rect.left - self.width
                    self.x_velocity = 0
                    return True
                elif real_overlap == right_overlap and self.x_velocity < 0:
                    self.x = platform_rect.right
                    self.x_velocity = 0
                    return True
    
    def update(self, delta, platforms, debrises):
        print(self.state)
        keys = pygame.key.get_pressed()
        collision_checking = 8
        collision_checking_term = delta / collision_checking
        self.input_manager(keys)

        if not self.grounded:
            self.y_velocity += self.gravity * delta
            self.y_velocity = min(self.y_velocity, self.max_fall_speed)
        
        if not self.grounded and self.y_velocity > 10:
            self.state = "falling"
        if self.diving and self.y_velocity > 1000:
            self.state = "forcing"

        
        self.x_velocity += self.accel * delta
        self.x_velocity *= 0.9 # 마찰ㄺ
        self.grounded = False

        for _ in range(collision_checking): # Protip - 다운웰 느낌나는 서브스텝 알고리즘
            self.x += self.x_velocity * collision_checking_term
            self.y += self.y_velocity * collision_checking_term

            if self.check_platform_collision(platforms, debrises):
                break
        
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
    
    def draw(self, surface, camera):
        screen_y = camera.draw_again(self)

        if self.state == "grounded":
            current_sprite = self.sprites["idle"][0]
        else:
            current_sprite = self.sprites["falling"][0]
        
        surface.blit(current_sprite, (self.x, screen_y))

# 효과들 ( 총알, 파동... )

class PulseWave:
    def __init__(self, x, y, initial_radius, max_radius, growth_speed, color, filled=False, effect=None):
        
        self.x = x
        self.y = y
        
        self.radius = initial_radius
        self.max_radius = max_radius
        self.growth_speed = growth_speed
        
        self.color = color
        self.filled = filled
        self.thickness = 3 if not filled else 0
        
        self.active = True
        self.hit_player = False
        self.effect = effect if effect else {}

        self.fadeout_manager = UIManager(duration=1)
        self.alpha = 0
    
    def update(self, delta):
        
        self.radius += self.growth_speed * delta

        if not self.fadeout_manager.completed:
            self.alpha = self.fadeout_manager.fadeout(delta)
        else:
            self.alpha = 0
        
        if self.radius >= self.max_radius:
            self.active = False
    
    def draw(self, surface, camera):

        screen_y = self.y + camera.camera_y
        
        if screen_y < -200 or screen_y > SCREEN_HEIGHT + 200:
            return

        color = (*self.color, self.alpha)
        
        if self.filled:
            pygame.gfxdraw.filled_circle(
                surface,
                int(self.x),
                int(screen_y),
                int(self.radius),
                color
            )
        else:
            for i in range(self.thickness):
                pygame.gfxdraw.circle(
                    surface,
                    int(self.x),
                    int(screen_y),
                    int(self.radius) - i,
                    color
                )
    
    def check_collision(self, player):
        if self.hit_player:
            return None
        
        player_center_x = player.x + player.width // 2
        player_center_y = player.y + player.height // 2
        
        dx = player_center_x - self.x
        dy = player_center_y - self.y
        dist = math.hypot(dx, dy)
         
        
        if self.filled:
            if dist <= self.radius:
                self.hit_player = True
                return self.effect
            else:
                outline = 30
                if abs(dist - self.radius) < outline:
                    self.hit_player = True
                    return self.effect
        return None
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class Debris:
    def __init__(self, x, y, velocity_x, velocity_y, size, color):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.color = color
        self.gravity = 2000
        self.lifetime = 1.0 
        self.alpha = 255
    
    def update(self, delta):
        self.x += self.velocity_x * delta
        self.y += self.velocity_y * delta
        self.velocity_y += self.gravity * delta
        

        self.lifetime -= delta
        self.alpha = max(0, int(255 * (self.lifetime / 1.0)))
    
    def draw(self, surface, camera):
        screen_y = self.y + camera.camera_y
        pygame.draw.rect(
            surface,
            self.color,
            (self.x, screen_y, self.size, self.size)
        )

# 적들

class Enemy:

    def __init__(self, HP, sprite_size, can_death_instantly, x, y):
        self.HP = HP
        self.can_death_instantly = can_death_instantly
        self.x = x
        self.y = y
        self.width, self.height = sprite_size
        self.state = "active"

        self.sprites = {}
        self.current_animation = "default"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1
    
    def update_animation(self, delta):
        self.animation_timer += delta

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame += 1

            if self.current_animation in self.sprites:
                if self.animation_frame >= len(self.sprites[self.current_animation]):
                    self.animation_frame = 0
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        pass
    
    def draw(self, surface, camera):
        screen_y = camera.draw_again(self)

        if self.current_animation in self.sprites:
            frames = self.sprites[self.current_animation]
            if len(frames) > 0 and self.animation_frame < len(frames):
                current_sprite = frames[self.animation_frame]
                surface.blit(current_sprite, (self.x, screen_y))
    
    def take_damage(self, is_forcing = False):
        if is_forcing and self.can_death_instantly:
            self.HP = 0
        else:
            return False
        
        if self.HP <= 0:
            self.state = "death_anim_playing"
            return True
        else:
            return False
    
    def is_dead(self):
        return self.HP <= 0

class FireRobot(Enemy):
    sprite_cash = None

    def __init__(self, HP, sprite_size, can_death_instantly, x, y):
        super().__init__(HP, sprite_size, can_death_instantly, x, y)
        self.x_velocity = 600
        self.y_velocity = 600
        self.pulse_timer = 0
        self.pulse_period = 2.0
        self.pulse_radius = 32.0
        self.max_pulse_radius = 128.0

        if FireRobot.sprite_cash is None:
            FireRobot.sprite_cash = {"default":[load_sprites(f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png", sprite_size) for i in range(1, 6)],
                                    "death":[load_sprites(f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png", sprite_size) for i in range(6, 11)],}

        self.sprites = FireRobot.sprite_cash

    def update(self, delta, player, pulses=None):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += (dx / dist) * self.x_velocity * delta
            self.y += (dy / dist) * self.y_velocity * delta

        self.pulse_timer += delta
        if self.pulse_timer >= self.pulse_period:
            self.pulse_timer = 0
            if pulses is not None:
                self.attack_wave(pulses)
        
        self.update_animation(delta)

    def attack_wave(self, pulses):
        effect = {
            "damage": 1,
            "knockback": (0, -300),
            "stun_duration": 0.3
        }
    
        pulse = PulseWave(
            x = self.x + self.width // 2,
            y = self.y + self.height // 2,
            initial_radius = self.pulse_radius,
            max_radius = self.max_pulse_radius,
            growth_speed = 200,
            color = ORANGE,
            filled = False,
            effect = effect
        )
    
        pulses.append(pulse)

    def draw(self, surface, camera):
        super().draw(surface, camera)

class EnemySpawner:
    def __init__(self):
        self.enemies = []
        self.last_y = 600
        self.next_enemy_pointer = 0

        self.enemy_pattern = ['FireRobot', 'None', 'None']

        self.min_gap_y = 150
        self.max_gap_y = 500

        self.enemy_data = {
            "FireRobot": {
                "size": (64, 128),
                "hp": 3,
                "can_instant_death": True,
                "spawn_type": "air"
            },
            "RangedRobot": {
                "size": (64, 64),
                "hp": 2,
                "can_instant_death": True,
                "spawn_type": "platform"
            }
        }

        for _ in range(3):
            self.generate(None)
        
    def rotation(self):
        pattern_len = len(self.enemy_pattern)
        self.next_enemy = self.enemy_pattern[self.next_enemy_pointer % pattern_len]
        self.next_enemy_pointer += 1
    
    def generate(self, platforms):
        self.last_y += random.randint(self.min_gap_y, self.max_gap_y)

        self.rotation()
        if self.next_enemy == "None":
            return

        enemy_data = self.enemy_data[self.next_enemy]

        size = enemy_data['size']
        hp = enemy_data['hp']
        instant_deathable = enemy_data['can_instant_death']
        spawn_type = enemy_data['spawn_type']

        if spawn_type == 'air':
            x = random.randint(100, SCREEN_WIDTH)
            y = self.last_y

            enemy = FireRobot(hp, size, instant_deathable, x, y)

            self.enemies.append(enemy)
        
    def update(self, camera, platforms):
        for i in range(len(self.enemies) - 1, -1, -1):
            screen_y = self.enemies[i].y + camera.camera_y
        
        if screen_y < -10000:
            self.enemies.pop(i)
        
        for i in range(len(self.enemies) - 1, -1, -1):
            if self.enemies[i].is_dead():
                self.enemies.pop(i)
        
        if len(self.enemies) == 0:
            self.last_y = abs(camera.camera_y) + SCREEN_HEIGHT
            self.generate(platforms)
        else:
            last_screen_y = self.enemies[-1].y + camera.camera_y
            if last_screen_y < SCREEN_HEIGHT + 500:
                self.generate(platforms)
    
    def draw(self, camera, surface):
        for enemy in self.enemies:
            enemy.draw(surface, camera)

# 플랫폼들

class PlatformGen:
    def __init__(self):
        self.platforms = []
        self.last_y = 400
        self.platforms_pattern = ["Normal", "Normal", "Breakable", "Normal", "Breakable"]
        self.pointer = 0
        self.NextPlatform = None
        self.min_gap_y = 70
        self.max_gap_y = 170
        self.min_width = 100
        self.max_width = 500
        self.fixed_height = 32

        self.where_width = 0
        for _ in range(5):
            self.generate()

    def rotation(self):
        self.NextPlatform = self.platforms_pattern[self.pointer % 5]
        self.pointer += 1

    def generate(self):
        self.last_y += random.randint(self.min_gap_y, self.max_gap_y)
        self.where_width = random.randint(self.min_width, self.max_width)
        x = random.randint(0, SCREEN_WIDTH - self.where_width)

        self.rotation()

        if self.NextPlatform == "Normal":
            self.NextPlatform = NormalPlatform(x, self.last_y, self.where_width, self.fixed_height)
            self.platforms.append(self.NextPlatform)
        elif self.NextPlatform == "Breakable":
            self.NextPlatform = BreakablePlatform(x, self.last_y, self.where_width, self.fixed_height)
            self.platforms.append(self.NextPlatform)
    
    def update(self, camera):

        for i in range(len(self.platforms) - 1, -1, -1):
            screen_y = self.platforms[i].y + camera.camera_y
            if screen_y < -100:
                self.platforms.pop(i)
            elif isinstance(self.platforms[i], BreakablePlatform):
                if self.platforms[i].is_broken():
                    self.platforms.pop(i)
        
        if len(self.platforms) == 0:
            self.last_y = abs(camera.camera_y) + SCREEN_HEIGHT
            self.generate()
        else:
            last_screen_y = self.platforms[-1].y + camera.camera_y
            if last_screen_y < SCREEN_HEIGHT + 500:
                self.generate()
    
    def draw(self, camera, surface):
        for platform in self.platforms[:]:
            screen_y = camera.draw_again(platform)
            if isinstance(platform, NormalPlatform):
                surface.blit(pygame.transform.scale(platform.sprite, (platform.width, platform.height)), (platform.x, screen_y))
            elif isinstance(platform, BreakablePlatform):
                surface.blit(
                    pygame.transform.scale(
                        platform.sprite, (platform.width, platform.height)
                    ),
                    (platform.x, screen_y),
                )

class PlatformBase:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, self.sprite, self.get_rect())

class NormalPlatform(PlatformBase):
    sprite_cash = None

    def __init__(self,x, y, width, height):
        super().__init__(x, y, width, height)
        if NormalPlatform.sprite_cash is None:
            NormalPlatform.sprite_cash = pygame.image.load(
                "Sprites/Object/Platforms/NormalPlatform/NormalPlatform.png"
            )
        self.sprite = NormalPlatform.sprite_cash
        self.Intgrid = 0

class BreakablePlatform(PlatformBase):
    sprite_cash = None

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        if BreakablePlatform.sprite_cash is None:
            BreakablePlatform.sprite_cash = pygame.image.load(
                "Sprites/Object/Platforms/BreakablePlatform/BreakablePlatform.png"
            )
        self.sprite = BreakablePlatform.sprite_cash
        self.Intgrid = 1
        self.broken = False
    
    def break_platform(self, debris_list=None):
        self.broken = True
        
        if debris_list is not None:
            for _ in range(25):
                debris = Debris(
                    x = self.x + random.randint(0, self.width),
                    y = self.y,
                    velocity_x=random.randint(-200, 200),
                    velocity_y=random.randint(-500, -200),
                    size = random.randint(4, 8),
                    color = GRAY
                )
                debris_list.append(debris)

        return True

    def is_broken(self):
        return self.broken

# 인게임 클래스        

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.camera = Camera((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fading = UIManager(duration=1.0)
        self.background = pygame.image.load("Sprites/Backgrounds/5km.png")

        self.world_timer = 0
        self.blink_timer = 0
        self.timer = 0

        self.fading.duration = 3.0
        self.fade_in = 1.0
        self.fade_out = 1.0
        self.world_transparency = 0

        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.screen_blink = ScreenBlinker(BLACK, 10.0)
        self.PlatformGenerator = PlatformGen()

        self.camera.active = True
        self.camera.scroll_active = True

        player_x = SCREEN_WIDTH // 2
        player_y = SCREEN_HEIGHT // 2
        self.player = Player(player_x, player_y)

        self.enemy_spawner = EnemySpawner()
        self.current_pulses = []
        self.debrises = []
    
    def draw(self, delta):
        self.game_surface.fill(WHITE)

        self.camera.bg_cycle(self.game_surface)

        if self.screen_blink.active:
            self.screen_blink.update(delta)
            self.screen_blink.draw(self.game_surface)


    
    def run(self):
        delta = clock.tick(FPS) / 1000
        self.world_timer += delta

        if self.world_timer < 10:
            self.blink_timer += delta
            if self.blink_timer >= 0.15:
                self.screen_blink.reset()
                self.blink_timer = 0
        else:
            self.blink_timer = 0
            self.screen_blink.reset()
        
        self.player.update(delta, self.PlatformGenerator.platforms, self.debrises)
        self.camera.camera_chase(delta, self.player)
        self.enemy_spawner.update(self.camera, self.PlatformGenerator.platforms)

        for enemy in self.enemy_spawner.enemies:
            if isinstance(enemy, FireRobot):
                enemy.update(delta, self.player, self.current_pulses)
            else:
                enemy.update(delta, self.player)
        
        for i in range(len(self.current_pulses) - 1, -1, -1):
            self.current_pulses[i].update(delta)

            effect = self.current_pulses[i].check_collision(self.player)

            if effect:
                if "knockback" in effect:
                    kb_x, kb_y = effect['knockback']
                    self.player.x_velocity += kb_x
                    self.player.y_velocity = kb_y
                
            if not self.current_pulses[i].active:
                self.current_pulses.pop(i)

        self.PlatformGenerator.update(self.camera)

        if self.world_timer <= self.fade_in:
            surface_transparent = self.fading.fadein(delta)
            self.game_surface.set_alpha(surface_transparent)
        else:
            self.game_surface.set_alpha(255)


        self.draw(delta)
        self.PlatformGenerator.draw(self.camera, self.game_surface)
        for pulse in self.current_pulses:
            pulse.draw(self.game_surface, self.camera)
        self.enemy_spawner.draw(self.camera, self.game_surface)
        self.player.draw(self.game_surface, self.camera)
        for debris in self.debrises:
            debris.update(delta)
            debris.draw(self.game_surface, self.camera)
        self.debrises = [d for d in self.debrises if d.lifetime > 0]
        screen.blit(self.game_surface, (0, 0))


# 보조 클래스

class UIManager:
    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.completed = False
        self.value = 0
    
    def fadein(self, delta):
        self.timer = min(self.timer + delta, self.duration)
        progress = self.timer / self.duration
        self.value = int(255 * progress)
        self.completed = (self.timer >= self.duration)
        return self.value

    def fadeout(self, delta):
        self.timer = min(self.timer + delta, self.duration)
        progress = self.timer / self.duration
        self.value = int(255 * ((1.0 - progress)))
        self.completed = (self.timer >= self.duration)
        return self.value

    def blink(self, delta):
        self.timer += delta
        if self.timer >= self.duration and not self.completed:
            self.timer = 0
        return self.timer < (self.duration / 2)
    
    def screen_shake(self, delta, Camera):
        pass
    
    def reset_timer(self):
        self.timer = 0
        self.completed = False
        self.value = 0

class GameState:
    LOGO = 'logo'
    CUTSCENE = 'cutscene'
    MENU = 'menu'
    PLAYING = 'playing'
    GAME_OVER = "game_over"
    EXIT = 'exit'

    @staticmethod
    def cutscene(scenenumber):
        return ('cutscene', scenenumber)

class ScreenFader:
    def __init__(self, surface, fade_duration, fade_in, fade_out):
        self.surface = surface.convert_alpha()
        self.timer = 0
        self.transparent = 0
        self.active = True

        self.fading = UIManager(duration=1.0)
        self.fade_in = fade_in
        self.duration = fade_duration
        self.fade_out = fade_out
        self.phase = "fade_in"


    def update(self, delta):
        self.timer += delta

        if self.timer < self.fade_in:
            self.transparent = self.fading.fadeout(delta)

        elif self.timer < self.duration - self.fade_out:
            self.transparent = 0
            self.phase = "show_cutscene"
            if self.timer < self.duration - self.fade_out - 0.01:
                self.fading.reset_timer()

        elif self.timer < self.duration:
            self.phase = "fade_out"
            self.transparent = self.fading.fadein(delta)

        else:
            self.phase = "done"
            self.transparent = 0
            self.active = False

    def draw(self):
        self.surface.set_alpha(self.transparent)
        if self.transparent >= 254:
            screen.fill(BLACK)
        screen.blit(self.surface, (0, 0))

    def reset(self):
        self.timer = 0
        self.transparent = 0
        self.active = True
        self.phase = "done"
        self.fading.reset_timer()

class ScreenBlinker:
    def __init__(self, color, duration):
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        self.surface.fill(color)
        self.color = color
        self.timer = 0
        self.transparent = 0
        self.active = True

        self.fading = UIManager(duration=0.05)
        self.fade_in = 0.25
        self.duration = duration
        self.fade_out = 0.25
        self.show_cutscene = False
    
    def update(self, delta):
        self.timer += delta

        if self.timer < self.fade_in:
            self.transparent = self.fading.fadein(delta / 2)

        elif self.timer < self.duration - self.fade_out:
            self.transparent = 255
            self.show_cutscene = True
            if self.timer < self.duration - self.fade_out - 0.01:
                self.fading.reset_timer()

        elif self.timer < self.duration:
            self.show_cutscene = False
            self.transparent = self.fading.fadeout(delta)

        else:
            self.transparent = 0
            self.active = False
    
    def draw(self, target_surface=None):

        if target_surface is None:
            target_surface = screen

        self.surface.set_alpha(self.transparent)
        target_surface.blit(self.surface, (0, 0))
    
    def reset(self):
        self.timer = 0
        self.transparent = 0
        self.active = True
        self.show_cutscene = False
        self.fading.reset_timer()

# 인게임

with open("CutsceneData/cutscene_data.json", encoding='utf-8') as f:
    cutscene_data = json.load(f)

cutscene_data = {int(k): v for k, v in cutscene_data.items()}

LogoMaker = LogoShow()
Starter = StartMenu()
Ingame = Game()
current_state = GameState.LOGO
screen_fader = None

def play_cutscene(scenenumber):
    global current_cutscene

    if scenenumber in cutscene_data:
        data = cutscene_data[scenenumber]
        current_cutscene = CutsceneBase(data['images'], data['duration'], data['text'])
    else:
        raise ValueError

current_cutscene = None
camera = Camera((SCREEN_WIDTH, SCREEN_HEIGHT))

while not current_state == GameState.EXIT:
    delta = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_state = GameState.EXIT
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if isinstance(current_state, tuple) and current_state[0] == 'cutscene':
                    if current_cutscene:
                        current_cutscene.active = False
                        
                        if screen_fader:
                            screen_fader.timer = (
                                screen_fader.duration - screen_fader.fade_out
                            )
                            screen_fader.phase = "fade_out"
                            screen_fader.fading.reset_timer()

    if isinstance(current_state, tuple):
        state_type, *data = current_state

        if state_type == 'cutscene':
            scenenumber = data[0]

            if screen_fader is None:
                cutscene_info = cutscene_data[scenenumber]


                total_cutscene_time = len(cutscene_info['images']) * cutscene_info['duration']
                fade_in_time = 3.0
                fade_out_time = 1.0

                total_dur = total_cutscene_time + fade_in_time + fade_out_time
                screen_fader = ScreenFader(screen, total_dur, fade_in_time, fade_out_time)
            
            screen_fader.update(delta)

            if current_cutscene is None and screen_fader.phase == "show_cutscene":
                play_cutscene(scenenumber)
            
            if current_cutscene:
                current_cutscene.update(delta)
            
            screen.fill(BLACK)
            screen_fader.draw()
            if screen_fader.phase == "show_cutscene" and current_cutscene:
                current_cutscene.draw()
            
            if screen_fader.phase == "fade_out":
                screen.fill(BLACK)

            if current_cutscene and current_cutscene.ended():
                if screen_fader.phase == "done":
                    screen.fill(BLACK)
                    current_state = GameState.PLAYING
                    current_cutscene = None
                    screen_fader = None



    if current_state == GameState.LOGO:
        LogoMaker.update(delta)
        LogoMaker.draw()

        if LogoMaker.finished():
            current_state = GameState.MENU
    
    if current_state == GameState.MENU:
        Starter.update(delta)
        Starter.draw() 
    
        temp_surface = screen.copy()
    
        camera.update(delta)
        result = camera.apply(temp_surface)
    
        screen.fill(BLACK)
        screen.blit(result, (0, 0))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            current_state = GameState.cutscene(1)
        elif keys[pygame.K_ESCAPE]:
            current_state = GameState.EXIT
    
    if current_state == GameState.PLAYING:
        Ingame.run()
    



    
    pygame.display.flip()

pygame.quit()
sys.exit()
