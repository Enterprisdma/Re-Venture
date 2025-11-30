# 다음 작업 - 플레이어 업그레이드 UI 만들기

import subprocess
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

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
        "SFX/23M-RFT70_Appear.mp3",
        "SFX/23M-RFT70_Teleport.mp3",
        "SFX/23M-RFT70_TeleportEnd.mp3",
        "SFX/23M-RFT70_AttackAlarm.mp3",
        "SFX/23M-RFT70_Death.mp3",
        "SFX/23M-RFT70_EdgeShredding.mp3",
        "SFX/23M-RFT70_CuttingDimension.mp3",
        "SFX/23M-RFT70_TremblingSlash.mp3",
        "SFX/Break_platform.mp3",
        "SFX/Hype.mp3",
        "SFX/Interude.mp3",
        "SFX/RE_Venture-Starting.wav",
    ]

    assets += [f"Sprites/Backgrounds/Main{i}.png" for i in range(1, 5)]
    assets += [f"Sprites/Cutscene/StartCutscene{i}.png" for i in range(1, 3)]
    assets += [f"Sprites/Player/LEEJAMMIN{i}.png" for i in range(1, 17)]
    assets += [f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png" for i in range(1, 11)]
    assets += [f"Sprites/Enemy/Ranged_Robot/Ranged_Robot{i}.png" for i in range(1, 27)]
    assets += [f"Sprites/Entities/Laser/Laser{i}.png" for i in range(1, 11)]
    assets += [f"Sprites/Boss/23M-RFT70/23M-{i}.png" for i in range(1, 61)]
    assets += [f"SFX/10km_Howling{i}.png" for i in range(1, 6)]

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

import pygame
import pygame.gfxdraw
import math
import json
import random

pygame.init()

SCREEN_WIDTH = 1140
SCREEN_HEIGHT = 852
FPS = 60
icon = pygame.image.load("Sprites/Object/CompanyLogo.png")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
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

    
    def draw_again(self, entity):
        if isinstance(entity, (int, float)):
            return entity + self.camera_y
        else:
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

def draw_health_hud(surface, player, km):
    base_x = 20
    base_y = 30

    cell_width = 40
    cell_height = 25
    cell_gap = 4

    total_width = cell_width * 6 + cell_gap * 5

    start_x = base_x

    bg_rect = pygame.Rect(start_x - 5, base_y - 5, total_width + 10, cell_height + 10)

    if player.invincible_timer > 0:
        bg_color = (100, 100, 0)
        border_color = YELLOW
    else:
        bg_color = (40, 40, 40)
        border_color = WHITE

    pygame.draw.rect(surface, bg_color, bg_rect)
    pygame.draw.rect(surface, border_color, bg_rect, 3)

    for i in range(6):
        cell_x = start_x + i * (cell_width + cell_gap)
        cell_rect = pygame.Rect(cell_x, base_y, cell_width, cell_height)

        if i < player.hp:
            color = RED
        else:
            color = (60, 60, 60)

        pygame.draw.rect(surface, color, cell_rect)
        pygame.draw.rect(surface, border_color, cell_rect, 2)

    font = pygame.font.Font(None, 32)
    hp_text = font.render(f"{player.hp}/{player.max_hp}", True, WHITE)
    text_rect = hp_text.get_rect(
        center=(start_x + total_width // 2, base_y + cell_height // 2)
    )

    text_bg = pygame.Rect(
        text_rect.x - 3, text_rect.y - 1, text_rect.width + 6, text_rect.height + 2
    )
    pygame.draw.rect(surface, BLACK, text_bg)

    surface.blit(hp_text, text_rect)
    
    km_font = pygame.font.Font(None, 24)
    km_text = km_font.render(f"KM: {km:.1f}s", True, YELLOW)
    km_rect = km_text.get_rect(topleft=(base_x, base_y + cell_height + 15))
    surface.blit(km_text, km_rect)

def draw_boss_health_bar(surface, boss):
    if boss is None or boss.state == "dead":
        return

    bar_width = 800
    bar_height = 30
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = 50

    bg_rect = pygame.Rect(bar_x - 5, bar_y -5, bar_width + 10, bar_height + 10)
    pygame.draw.rect(surface, (40, 40, 40), bg_rect)
    pygame.draw.rect(surface, WHITE, bg_rect, 3)

    hp_ratio = max(0, boss.HP / boss.max_HP)
    current_bar_width = int(bar_width * hp_ratio)

    if hp_ratio > 0.6:
        bar_color = (255, 0, 0)
    elif hp_ratio > 0.3:
        bar_color = (255, 165, 0)
    else:
        bar_color = (255, 255, 0)

    if current_bar_width > 0:
        hp_rect = pygame.Rect(bar_x, bar_y, current_bar_width, bar_height)
        pygame.draw.rect(surface, bar_color, hp_rect)

    border_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(surface, WHITE, border_rect, 2)

    font = pygame.font.Font(None, 28)
    name_text = font.render("Boss: 23M-RFT70", True, WHITE)
    name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 20))
    surface.blit(name_text, name_rect)

    hp_font = pygame.font.Font(None, 24)
    hp_text = hp_font.render(f"{int(boss.HP)} / {int(boss.max_HP)}", True, WHITE)
    hp_text_rect = hp_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2))

    text_bg = pygame.Rect(
        hp_text_rect.x - 3,
        hp_text_rect.y - 1,
        hp_text_rect.width + 6,
        hp_text_rect.height + 2,
    )
    pygame.draw.rect(surface, BLACK, text_bg)
    surface.blit(hp_text, hp_text_rect)

class UpgradeUI:
    def __init__(self):
        self.active = False

        self.choices = []
        self.selected = None

        self.font_title = pygame.font.Font(None, 32)
        self.font_upgrade_name = pygame.font.Font("Font/DNFForgedBlade-Medium.ttf", 32)
        self.font_upgrade_desc = pygame.font.Font("Font/DNFForgedBlade-Medium.ttf", 24)
        
        self.input_timer = 0.0
        self.input_cooldown = 0.05

        self.fade_timer = 0
        self.fade_manager = UIManager(duration=0.5)

        self.choice_pointer = 0

        self.available_upgrades = [
            "FocusingSight",
            "Shotgunning",
            "DestructiveLaser",
            "Explosive",
            "ExtraSlicing",
            "StylishStomping",
            "WavingStomp",
            "Heal",
            "MechanicalBlood",
        ]
    
    def open(self, exclude_list=None):
        if exclude_list is None:
            exclude_list = []
        self.choices = random.sample(self.available_upgrades, 3)
        self.selected = None
        self.active = True
        self.choice_pointer = 0
        self.fade_manager.reset_timer()
    
    def get_fade_alpha(self, delta):

        if not self.active:
            return 0
        
        val = self.fade_manager.fadein(delta)
        return val
    
    def is_active(self):
        return self.active

    def update(self, delta):
        if not self.active:
            return None

        if self.input_timer > 0:
            self.input_timer -= delta
        if self.input_timer <= 0:
            self.input_timer = 0

        keys = pygame.key.get_pressed()

        if self.input_timer <= 0 and keys[pygame.K_a]:
            self.choice_pointer -= 1
            if self.choice_pointer <= 0:
                self.choice_pointer = 0
            self.input_timer = self.input_cooldown
        elif self.input_timer <= 0 and keys[pygame.K_d]:
            self.choice_pointer += 1
            if self.choice_pointer >= len(self.choices) - 1:
                self.choice_pointer = len(self.choices) - 1
            self.input_timer = self.input_cooldown
        
        if keys[pygame.K_RETURN]:
            if 0 <= self.choice_pointer < len(self.choices):
                self.selected = self.choices[self.choice_pointer]
                self.active = False
                self.input_timer = self.input_cooldown
                return self.selected
        
        return None

    def draw(self, surface):
        if not self.active:
            return

        title = self.font_title.render("Choose an Upgrade", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        surface.blit(title, title_rect)

        card_rects = self.get_card_rects()

        for i, rect in enumerate(card_rects):
            pygame.draw.rect(surface, (50, 50, 50), rect)
            pygame.draw.rect(surface, WHITE, rect, 3)

            if i >= len(self.choices):
                continue

            key = self.choices[i]
            name_text = self.font_upgrade_name.render(self.get_name(key), True, YELLOW)
            name_rect = name_text.get_rect(center=(rect.centerx, rect.top + 30))
            surface.blit(name_text, name_rect)

            for j, line in enumerate(self.get_desc_lines(key)):
                desc_text = self.font_upgrade_desc.render(line, True, WHITE)
                desc_rect = desc_text.get_rect(
                    center=(rect.centerx, rect.top + 70 + j * 28)
                )
                surface.blit(desc_text, desc_rect)

        self.draw_pointer(surface, card_rects)

    def draw_pointer(self, surface, card_rects):
        if not card_rects or self.choice_pointer < 0:
            return
        if self.choice_pointer >= len(card_rects):
            return

        target_rect = card_rects[self.choice_pointer]

        base_height = 30
        half_h = base_height // 2

        center_y = target_rect.top + 30 
        center_x = target_rect.left - 40

        p1 = (center_x, center_y - half_h)
        p2 = (center_x, center_y + half_h)
        p3 = (center_x + base_height, center_y)

        pygame.draw.polygon(surface, RED, [p1, p2, p3])
    
    def get_card_rects(self):
        card_width = 280
        card_height = 160
        gap = 40
        total_width = card_width * 3 + gap * 2
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 3

        rects = []
        for i in range(3):
            x = start_x + i * (card_width + gap)
            rects.append(pygame.Rect(x, y, card_width, card_height))
        return rects

    def get_name(self, key):
        names = {
            "FocusingSight": "포커싱 사이트",
            "Shotgunning": "샷거닝",
            "DestructiveLaser": "데스트럭티브 레이저",
            "Explosive": "익스플로시브",
            "ExtraSlicing": "익스트라 슬라이싱",
            "StylishStomping": "스타일리쉬 스톰핑",
            "WavingStomp": "웨이빙 스톰프",
            "Heal": "회복",
            "MechanicalBlood": "메카니컬 블러드",
        }
        return names.get(key, key)

    def get_desc_lines(self, key):
        desc = {
            "FocusingSight": ["단검 레이저의 굵기와", "나아가는 속도가 증가한다."],
            "Shotgunning": ["단검 레이저 발사 시", "세 갈래로 나간다.", "반동+데미지 추가."],
            "DestructiveLaser": ["단검 레이저가 일정 확률로", "플랫폼을 파괴한다."],
            "Explosive": ["단검 레이저 충돌 지점에", "파동이 발생한다."],
            "ExtraSlicing": ["매우 낮은 확률로", "매우 거대한 레이저 발사."],
            "StylishStomping": ["스톰핑 시 바운싱이", "최대 3회 억제된다."],
            "WavingStomp": ["스톰핑 시", "파동이 발생한다."],
            "Heal": ["HP를 4 회복한다."],
            "MechanicalBlood": ["적 10회 처치 시", "HP를 1 회복한다."],
        }
        return desc.get(key, ["설명 없음"])


    

class GameOverScreen:
    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.max_combo_font = pygame.font.Font(None, 36)
        self.max_location_font = pygame.font.Font(None, 36)

        self.rectangular_height = 0
        self.max_height = SCREEN_HEIGHT
        self.rectangular_width = SCREEN_WIDTH // 3
        self.skew_offset = 100

        self.expand_speed = 1000

        self.max_combo = 0
        self.max_location = 0

        self.show_text = True

    def update(self, delta, max_combo, max_location):

        self.max_combo = max_combo
        self.max_location = max_location

        if self.rectangular_height < self.max_height:
            self.rectangular_height += self.expand_speed * delta
    
    def draw(self, surface):
        
        surface.fill(BLACK)

        if self.rectangular_height > 0:
            point = [
                (SCREEN_WIDTH // 2 - self.rectangular_width // 2 + self.skew_offset, 0),
                (SCREEN_WIDTH // 2 + self.rectangular_width // 2 + self.skew_offset, 0),
                (
                    SCREEN_WIDTH // 2 + self.rectangular_width // 2 - self.skew_offset,
                    self.rectangular_height,
                ),
                (
                    SCREEN_WIDTH // 2 - self.rectangular_width // 2 - self.skew_offset,
                    self.rectangular_height,
                ),
            ]
            pygame.draw.polygon(surface, WHITE, point)
        
        if self.rectangular_height >= self.max_height:
            title_text = self.title_font.render("Game Over", True, BLACK)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 3 + 250, SCREEN_HEIGHT // 3))
            surface.blit(title_text, title_rect)

            combo_text = self.max_combo_font.render(f"Max Combo: {self.max_combo}", True, BLACK)
            combo_rect = combo_text.get_rect(
                center=(SCREEN_WIDTH // 3 + 200, SCREEN_HEIGHT // 3 + 100)
            )
            surface.blit(combo_text, combo_rect)

            location_text = self.max_location_font.render(f"Max Location: {self.max_location:.2f}KM", True, BLACK)
            location_rect = location_text.get_rect(
                center=(
                    SCREEN_WIDTH // 3 + 170,
                    SCREEN_HEIGHT // 3 + 150,
                )
            )
            surface.blit(location_text, location_rect)

            if self.show_text:
                restart_text = self.max_combo_font.render(
                    "Press R to Restart", True, BLACK
                )
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
                surface.blit(restart_text, restart_rect)

    def reset(self):
        self.active = False
        self.parallelogram_height = 0
        self.max_combo = 0
        self.max_height = 0
        self.blink_timer = 0
        self.show_text = True

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
        self.max_fall_speed = 4000
        self.accel = 0
        self.is_moving = False
        self.width = 64
        self.height = 64
        self.grounded = False
        self.state = "grounded"
        self.diving = False
        self.bouncing = False
        self.can_dive = True
        self.facing = 1
        self.iswarped = False
        self.jump_key_held = False
        self.input_blocked = False

        self.slide_timer = 0
        self.slide_duration = 1
        self.slide_holding = False
        self.sliding_velocity = 2000
        self.slide_cooldown_timer = 0
        self.slide_cooldown = 0.5

        self.hp = 6
        self.max_hp = 6
        self.invincible = True
        self.invincible_timer = 1
        self.invincible_duration = 1

        self.hitstop_timer = 0
        self.hitstop_duration = 0.5

        self.stun_timer = 0.0
        self.stun_duration = 1.0
        self.slow_timer = 0.0
        self.slow_duration = 2.0

        self.coord_debuff_active = False
        self.coord_debuff_timer = 0.0
        self.coord_debuff_duration = 1.5

        self.current_animation = 'idle'
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1

        self.weapon = Dagger(cooldown=0.1)
        self.mouse_pos = (0, 0)
        self.camera = None

        self.max_bounce_count = 1
        self.stomp_wave_enabled = False
        self.blood_heal_enabled = False
        self.blood_kill_count = 0

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

    def apply_stun(self):
        self.stun_timer = self.stun_duration

    def apply_slow(self):
        self.slow_timer = self.slow_duration

    def jump(self):
        if self.grounded:
            self.y_velocity = -1500
            self.grounded = False
            self.current_animation = "jumping"
            self.state = 'jumping'
            self.bouncing = False
            self.jump_key_held = True
        
    def Forcing(self, delta):
        if self.grounded:
            self.y_velocity = 0
            self.bouncing  = True
            self.state = "grounded"
            self.diving = False
            return
        elif not self.grounded and self.can_dive and not self.jump_key_held and self.y_velocity > 0:
            self.y_velocity += self.max_fall_speed * 0.2
            self.state = "forcing"
            self.diving = not self.bouncing
            self.slide_cooldown_timer = 0
            return
    
    def sliding(self):
        if not self.slide_holding:
            self.current_animation = "sliding"
            self.slide_timer = self.slide_duration
            self.height //= 2
            self.slide_holding = True
            self.slide_cooldown_timer = self.slide_cooldown
    
    def slide_cooldown_update(self):
        if self.slide_holding:
            self.slide_holding = False
            self.height *= 2
            self.current_animation = 'idle'
    
    def use_weapon(self, entities):
        self.weapon.execute_action(self, entities)
        
    def input_manager(self, keys, entities, delta):

        if self.hitstop_timer > 0 or self.stun_timer > 0:
            return
        
        if self.input_blocked:
            return

        self.is_moving = False
        self.accel = 0
        self.mouse_pos = pygame.mouse.get_pos()
        
        move_speed = 10000
        if self.slow_timer > 0:
            move_speed *= 0.5

        if keys[pygame.K_a]:
            self.accel = -move_speed
            self.is_moving = True
            self.facing = -1
        elif keys[pygame.K_d]:
            self.accel = move_speed
            self.is_moving = True
            self.facing = 1
        
        if keys[pygame.K_LSHIFT]:
            if self.grounded and self.slide_cooldown_timer <= 0 and not self.slide_holding:
                self.sliding()
        else:
            self.slide_cooldown_update()
            
        if keys[pygame.K_SPACE]:
            if self.grounded:
                self.jump()
            elif not self.jump_key_held:
                if not self.invincible:
                    self.Forcing(delta)
            elif self.y_velocity >= -500 and self.jump_key_held:
                self.jump_key_held = False 
                self.Forcing(delta)
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
                        if self.y_velocity > 0:
                            platform.break_platform(debris_list)
                            self.y_velocity = -1000
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
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def take_damage(self, damage):

        kb_x = 500
        kb_y = -1500
        
        if self.invincible:
            return False

        self.hp -= damage
        if self.hp < 0:
            self.hp = 0
        
        self.invincible = True
        self.invincible_timer = self.invincible_duration

        self.x_velocity = self.facing * kb_x
        self.y_velocity = kb_y

        self.hitstop_timer = self.hitstop_duration
        return True

    def apply_coord_debuff(self):
        self.coord_debuff_active = True
        self.coord_debuff_timer = self.coord_debuff_duration
    
    def update_animation(self, delta):
        previous_animation = self.current_animation

        if self.slide_holding:
            self.current_animation = 'sliding'
        elif self.is_moving:
            self.current_animation = 'walking'
        elif self.state == "forcing" or self.state == "falling":
            self.current_animation = "falling"
        elif self.state == "jumping":
            self.current_animation = "jumping"
        elif self.state == 'grounded':
            self.current_animation = 'idle'
        
        if previous_animation != self.current_animation:
            self.animation_frame = 0
            self.animation_timer = 0

        self.animation_timer += delta
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.sprites[self.current_animation]
            self.animation_frame = (self.animation_frame + 1) % len(frames)
    
    def update(self, delta, platforms, debrises, entities, camera):
        screen_y = self.y + camera.camera_y

        if self.stun_timer > 0:
            self.stun_timer -= delta
        if self.slow_timer > 0:
            self.slow_timer -= delta

        if self.coord_debuff_timer > 0:
            self.coord_debuff_timer -= delta
            if self.coord_debuff_timer <= 0:
                self.coord_debuff_active = False

        if self.hitstop_timer > 0:
            self.hitstop_timer -= delta
            if self.hitstop_timer <= 0:
                self.hitstop_timer = 0

        if not self.invincible:
            if screen_y < self.height - 32:
                self.y = abs(camera.camera_y) + self.height
                self.take_damage(1)

        keys = pygame.key.get_pressed()
        collision_checking = 8
        collision_checking_term = delta / collision_checking
        self.input_manager(keys, entities, delta)
        self.update_animation(delta)

        if not self.grounded:
            self.y_velocity += self.gravity * delta
            self.y_velocity = min(self.y_velocity, self.max_fall_speed)
        
        if not self.grounded and self.y_velocity > 10:
            self.state = "falling"
        if self.diving and self.y_velocity > 2000:
            self.state = "forcing"
        
        if self.invincible:
            self.invincible_timer -= delta
            if self.invincible_timer <= 0:
                self.invincible = False
        
        self.weapon.update(delta)
        
        if self.slide_cooldown_timer > 0 and not self.slide_holding:
            self.slide_cooldown_timer -= delta
        
        if self.slide_holding:
            self.slide_timer = max(0, self.slide_timer - delta)
            ratio = max(0, self.slide_timer / self.slide_duration)
            self.x_velocity = self.sliding_velocity * self.facing * ratio
        else:
            self.slide_cooldown_update()
            self.x_velocity += self.accel * delta
            self.x_velocity *= 0.9
        self.grounded = False

        for _ in range(collision_checking):
            self.x += self.x_velocity * collision_checking_term
            self.y += self.y_velocity * collision_checking_term

            if self.check_platform_collision(platforms, debrises):
                break
        
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    
    def draw(self, surface, camera):
        screen_y = camera.draw_again(self)

        if self.current_animation in self.sprites:
            frames = self.sprites[self.current_animation]
            if self.animation_frame < len(frames):
                current_sprite = frames[self.animation_frame]
                current_sprite = pygame.transform.flip(current_sprite, not self.facing < 0, False)
            else:
                current_sprite = frames[0]
        else:
            current_sprite = self.sprites['idle'][0]

        
        if self.invincible_timer > 0 and self.invincible_timer % 0.2 > 0.1:
            surface.blit(current_sprite, (self.x, screen_y))
        elif self.coord_debuff_active and self.coord_debuff_timer % 0.2 > 0.1:
            blue_sprite = current_sprite.copy()
            blue_sprite.fill(BLUE, special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(blue_sprite, (self.x, screen_y))
        else:
            surface.blit(current_sprite, (self.x, screen_y))

class Dagger:
    def __init__(self, cooldown):
        
        self.cooldown = cooldown
        self.cooldown_timer = 0
        self.damage = 150

        self.laser_width_multiplier = 1
        self.shotgun_enabled = False
        self.destructive_chance = 0.0
        self.explosive_chance = 0.0
        self.max_bounce = 0
        self.extra_slice_chance = 0.0
    
    def update(self, delta):
        
        if self.cooldown_timer > 0:
            self.cooldown_timer -= delta


    def execute_action(self, player, entities):

        if self.cooldown_timer > 0:
            return
        
        self.cooldown_timer = self.cooldown

        bullet_x = player.x + player.width // 2
        bullet_y = player.y + player.height // 2

        mouse_x, mouse_y = player.mouse_pos

        if player.camera:
            player_screen_y = player.camera.draw_again(bullet_y)
        else:
            player_screen_y = bullet_y

        dx = mouse_x - bullet_x
        dy = mouse_y - player_screen_y
        angle = math.atan2(dy, dx)

        shotgun_angles = [angle]

        if self.shotgun_enabled:
            kb = 1000
            spread = math.radians(30)
            shotgun_angles = [angle-spread, angle, angle+spread]
            if 32 + player.width < player.x < SCREEN_HEIGHT - player.width - 32:
                player.x_velocity -= math.cos(angle) * kb
            player.y_velocity -= math.sin(angle) * kb
            self.damage += 20

        for ang in shotgun_angles:
            laser = LaserBeam(bullet_x, bullet_y, ang, self.damage, camera=player.camera, dagger=self)
            entities.append(laser)
            laser.needs_raycast = True
            laser.camera = player.camera
        
class PulseWave:
    def __init__(self, x, y, initial_radius, max_radius, thickness, growth_speed, color, filled=False, effect=None, owner=None):
        
        self.x = x
        self.y = y
        
        self.radius = initial_radius
        self.max_radius = max_radius
        self.growth_speed = growth_speed
        
        self.color = color
        self.filled = filled
        self.thickness = thickness if not filled else 0
        
        self.active = True
        self.hit_player = False
        self.hit_enemies = set()
        self.owner = owner
        self.is_player_owned = False
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
        
        if screen_y < -400 or screen_y > SCREEN_HEIGHT + 400:
            return

        temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*self.color, int(self.alpha))
        
        if self.filled:
            pygame.draw.circle(
                temp_surface,
                color,
                (int(self.x), int(screen_y)),
                int(self.radius)
            )
        else:
            for i in range(self.thickness):
                pygame.draw.circle(
                    temp_surface,
                    color,
                    (int(self.x), int(screen_y)),
                    int(self.radius) - i
                )
        
        surface.blit(temp_surface, (0, 0))
    
    def check_collision_enemy(self, enemy):
        if not self.active:
            return None
        
        if id(enemy) in self.hit_enemies:
            return None
    
        if self.owner and enemy is self.owner:
            return None

        enemy_rect = enemy.get_rect()
        enemy_center_x = enemy_rect.centerx
        enemy_center_y = enemy_rect.centery

        dx = enemy_center_x - self.x
        dy = enemy_center_y - self.y
        dist = math.hypot(dx, dy)

        if self.filled:
            hit = dist <= self.radius
        else:
            outline = 30
            hit = abs(dist - self.radius) < outline

        if hit:
            self.hit_enemies.add(id(enemy))
        
            dmg = self.effect.get("damage", 0)
            if dmg > 0:
                enemy.take_damage(dmg)
            return self.effect

        return None
    
    def get_rect(self):
        return pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

class DoomLaser:
    sprite_cash = None


    def __init__(self, x, y, growth_speed, angle, default_height, max_height, effect):

        self.x = x
        self.y = y

        self.angle = angle
        self.effect = effect

        self.growth_speed = growth_speed
        self.default_height = default_height
        self.max_height = max_height

        self.start_width = 32
        self.current_width = self.start_width
        self.max_width = 2200

        self.stretch_timer = 0
        self.stretch_time = 0.5
        self.holding_duration = self.stretch_time + 2.0
        self.disappearing_duration = self.holding_duration + 1.0

        self.state = "releasing"
        self.frame_timer = 0
        self.current_frame = 0
        self.animation_speed = 0.1

        self.rect = pygame.Rect(0,0,0,0)
        self.hit_player = False

        sprite_size = (self.default_height, self.current_width)

        if DoomLaser.sprite_cash is None:
            DoomLaser.sprite_cash = {
                "appear": [
                    load_sprites(
                        f"Sprites/Entities/Laser/Laser{i}.png", sprite_size
                    )
                    for i in range(1, 6)
                ],
                "disappear": [
                    load_sprites(
                        f"Sprites/Entities/Laser/Laser{i}.png", sprite_size
                    )
                    for i in range(6, 11)
                ]
            }

        self.sprites = DoomLaser.sprite_cash

    def check_collision(self, player, camera):
        if self.hit_player or not (self.state == 'holding' or self.state == 'releasing'):
            return None

        player_rect = player.get_rect()
        player_rect.y = camera.draw_again(player.y)

        laser_len = self.current_width
        laser_thickness = self.default_height
        radius = laser_thickness / 2.0

        if radius <= 0:
            return None

        dir_x = math.cos(self.angle)
        dir_y = math.sin(self.angle)
        step = radius * 1.8 
        if step <= 0:
            return None
            
        num_steps = int(math.ceil(laser_len / step))
        
        for i in range(num_steps + 1):
            interp = (i / num_steps) - 0.5 if num_steps > 0 else 0
            dist_from_center = interp * laser_len

            circle_x = self.x + dist_from_center * dir_x
            world_y = self.y + dist_from_center * dir_y
            screen_y = camera.draw_again(world_y)

            closest_x = max(player_rect.left, min(circle_x, player_rect.right))
            closest_y = max(player_rect.top, min(screen_y, player_rect.bottom))

            distance_x = circle_x - closest_x
            distance_y = screen_y - closest_y
            distance_squared = (distance_x**2) + (distance_y**2)

            if distance_squared < (radius**2) and player.hitstop_timer <= 0:
                self.hit_player = True
                player.take_damage(self.effect.get("damage", 1))
                return self.effect

        return None

    def update(self, delta):
        self.stretch_timer += delta

        if self.stretch_timer <= self.stretch_time:
            self.state = 'releasing'
            self.default_height += self.growth_speed * delta
            if self.default_height >= self.max_height:
                self.default_height = self.max_height
            progress = max(0.0, min(1.0, self.stretch_timer / self.stretch_time))
            self.current_width = self.start_width + progress * (self.max_width - self.start_width)
        elif self.stretch_timer <= self.holding_duration:
            self.state = 'holding'
            self.current_width = self.max_width
        elif self.stretch_timer <= self.disappearing_duration:
            self.state = 'disappearing'
            elapsed = self.stretch_timer - self.holding_duration
            duration = self.disappearing_duration - self.holding_duration
            progress = max(0.0, min(1.0, elapsed / duration))
            self.current_width = self.start_width + (1-progress) * (
                self.max_width - self.start_width
            )
        else:
            self.state = 'releasing'
            self.current_width = 0
            self.stretch_timer = 0

        
        self.frame_timer += delta
        if self.frame_timer >= self.animation_speed:
            self.frame_timer = 0
            self.current_frame += 1

            if self.current_frame >= 4:
                self.current_frame = 4
    
    def draw(self, surface, camera):
        screen_y = self.y + camera.camera_y
        
        if self.state == 'releasing' or self.state == 'holding':
            sprites = self.sprites['appear']
        elif self.state == 'disappearing' or self.state == 'finished':
            sprites = self.sprites['disappear']

        frame_index = min(self.current_frame, len(sprites) - 1)
        width = max(1, int(self.current_width))
        height = max(1, int(self.default_height))
    
        scaled_sprite = pygame.transform.scale(
            sprites[frame_index], (width, height)
        )

        degrees = math.degrees(self.angle)

        rotated_sprite = pygame.transform.rotate(scaled_sprite, -degrees)
        self.rect = rotated_sprite.get_rect(center=(self.x, screen_y))
        surface.blit(rotated_sprite, self.rect)

class LaserBeam:
    def __init__(self, start_x, start_y, angle, damage, max_length=2000, camera=None, dagger=None, owner_pattern=None):
        self.start_x = start_x
        self.start_y = start_y
        self.damage = damage
        self.angle = angle
        self.max_length = max_length
        self.camera = camera

        self.end_x = start_x + math.cos(angle) * max_length
        self.end_y = start_y + math.sin(angle) * max_length

        self.hit_x = self.end_x
        self.hit_y = self.end_y
        
        self.lifetime = 0.1
        self.age = 0
        self.active = True
        self.width = 4
        if dagger is not None:
            self.width *= dagger.laser_width_multiplier
            self.platform_destroy_chance = dagger.destructive_chance
            self.explosive_chance = dagger.explosive_chance
        else:
            self.platform_destroy_chance = 0.0
            self.explosive_chance = 0.0

        self.color = WHITE

        self.raycast_done = False
        self.hit_something = False
        self.enemy_damaged = False

        self.owner_pattern = owner_pattern

    def raycast(self, enemies, platforms, pulses=None):
        if self.raycast_done:
            return

        closest_distance = self.max_length
        hit_target = None

        for enemy in enemies:
            if isinstance(enemy, Boss23M):
                if enemy.state == "dead":
                    continue
                elif enemy.state == 'spawning':
                    continue

            distance = self.line_rect_intersection(
                self.start_x, self.start_y, self.end_x, self.end_y, enemy.get_rect()
            )

            if distance and distance < closest_distance:
                closest_distance = distance
                hit_target = enemy

        for platform in platforms:
            distance = self.line_rect_intersection(
                self.start_x, self.start_y, self.end_x, self.end_y, platform.get_rect()
            )

            if distance and distance < closest_distance:
                closest_distance = distance
                hit_target = platform

        if hit_target and isinstance(hit_target, Enemy) and not self.enemy_damaged:
            hit_target.take_damage(self.damage)
            self.enemy_damaged = True
        
        if hit_target and isinstance(hit_target, PlatformBase) and self.platform_destroy_chance >= random.random():
            hit_target.break_platform(debris_list=None)

        dir_x = math.cos(self.angle)
        dir_y = math.sin(self.angle)
        self.hit_x = self.start_x + dir_x * closest_distance
        self.hit_y = self.start_y + dir_y * closest_distance
        self.hit_something = (closest_distance < self.max_length)
        self.raycast_done = True

        if self.hit_something and self.explosive_chance >= random.random():
            effect = {"damage" : 50}
            pulse = PulseWave(
                x=self.hit_x,
                y=self.hit_y,
                initial_radius=10,
                max_radius=200,
                thickness=10,
                growth_speed=400,
                color=WHITE,
                filled=False,
                effect=effect,
                owner=self
            )
            pulse.is_player_owned = True
            pulses.append(pulse)

    def line_rect_intersection(self, x1, y1, x2, y2, rect):
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)

        if length == 0:
            return None

        dx /= length
        dy /= length

        steps = int(length)
        for i in range(steps):
            check_x = x1 + dx * i
            check_y = y1 + dy * i

            if rect.collidepoint(check_x, check_y):
                return i

        return None

    def update(self, delta):
        self.age += delta
        if self.age >= self.lifetime:
            self.active = False
            self.enemy_damaged = False

    def draw(self, surface, camera):
        screen_start_y = camera.draw_again(self.start_y)
        screen_hit_y = camera.draw_again(self.hit_y)

        progress = self.age / self.lifetime
        alpha = int(255 * (1 - progress))

        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.line(
            temp_surface,
            color_with_alpha,
            (int(self.start_x), int(screen_start_y)),
            (int(self.hit_x), int(screen_hit_y)),
            self.width,
        )

        surface.blit(temp_surface, (0, 0))

        if self.hit_something and self.age < 0.05:
            pygame.draw.circle(
                surface,
                self.color,
                (int(self.hit_x), int(screen_hit_y)),
                int(10 - self.age * 100),
                3,
            )

    def get_rect(self):
        return pygame.Rect(0, 0, 0, 0)
        


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
        temp_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        temp_surf.fill((*self.color, self.alpha))
        surface.blit(temp_surf, (self.x, screen_y))

class AfterImage:
    def __init__(self, x, y, sprite, duration, facing):
        self.x = x
        self.y = y
        self.sprite = pygame.transform.flip(sprite, not facing < 0, False)
        self.duration = duration
        self.lifetime = duration
        self.initial_alpha = 150

    def update(self, delta):
        self.lifetime -= delta
        if self.lifetime < 0:
            self.lifetime = 0
    
    def get_rect(self):
        return self.sprite.get_rect(topleft=(self.x, self.y))

    def draw(self, surface, camera):
        if self.lifetime > 0:
            alpha = (self.lifetime / self.duration) * self.initial_alpha
            temp_sprite = self.sprite.copy()
            temp_sprite.set_alpha(alpha)
            screen_y = camera.draw_again(self)
            surface.blit(temp_sprite, (self.x, screen_y))

class Enemy:

    def __init__(self, HP, sprite_size, can_death_instantly, x, y):

        self.max_HP = HP
        self.HP = HP
        self.can_death_instantly = can_death_instantly
        self.x = x
        self.y = y
        self.width, self.height = sprite_size
        self.state = "active"
        self.active = True

        self.sprites = {}
        self.current_animation = "default"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.05
    
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

    def draw(self, surface, camera):
        screen_y = camera.draw_again(self)

        if self.current_animation in self.sprites:
            frames = self.sprites[self.current_animation]
            if len(frames) > 0 and self.animation_frame < len(frames):
                current_sprite = frames[self.animation_frame]
                surface.blit(current_sprite, (self.x, screen_y))
        
        hp_ratio = self.HP / self.max_HP
        hpb_width = self.width
        hpb_height = 4

        pygame.draw.rect(surface, RED, (self.x, screen_y - 8, hpb_width, hpb_height))
        pygame.draw.rect(surface, GREEN, (self.x, screen_y - 8, hpb_width * hp_ratio, hpb_height))
    
    def take_damage(self, damage, is_forcing = False):
        if is_forcing and self.can_death_instantly:
            self.HP = 0
            return True

        self.HP -= damage
        
        if self.HP <= 0:
            self.state = "death_anim_playing"
            return True
        
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
        self.pulse_period = 1.0
        self.pulse_radius = 32.0
        self.max_pulse_radius = 128.0

        if FireRobot.sprite_cash is None:
            FireRobot.sprite_cash = {"default":[load_sprites(f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png", sprite_size) for i in range(1, 6)],
                                    "death":[load_sprites(f"Sprites/Enemy/Fire_Robot/Fire_Robot{i}.png", sprite_size) for i in range(6, 11)],}

        self.sprites = FireRobot.sprite_cash

    def update(self, delta, player, camera, pulses=None):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.x += (dx / dist) * self.x_velocity * delta
            self.y += (dy / dist) * (self.y_velocity + (camera.scrolling_speed  * 2)) * delta

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
            thickness=15,
            growth_speed = 300,
            color = ORANGE,
            filled = False,
            effect = effect,
            owner=self
        )
    
        pulses.append(pulse)

    def draw(self, surface, camera):
        super().draw(surface, camera)

class RangedRobot(Enemy):
    sprite_cash = None

    def __init__(self, HP, sprite_size, can_death_instantly, x, y):
        super().__init__(HP, sprite_size, can_death_instantly, x, y)
        self.x_velocity = 600
        self.y_velocity = 600
        self.laser_period = 1.5
        self.laser_radius = 32.0
        self.max_laser_radius = 200.0

        self.timer = 0
        self.idle_time = 0.5
        self.ready_time = self.idle_time + 1.0
        self.fire_time = self.ready_time + 1.0

        self.colideable = True
        self.GRAVITY = 8000

        self.current_animation = 'default'

        self.laser_fired = False

        if RangedRobot.sprite_cash is None:
            RangedRobot.sprite_cash = {
                "default": [
                    load_sprites(
                        f"Sprites/Enemy/Ranged_Robot/Ranged_Robot{i}.png", sprite_size
                    )
                    for i in range(1, 6)
                ],
                "shootready": [
                    load_sprites(
                        f"Sprites/Enemy/Ranged_Robot/Ranged_Robot{i}.png", sprite_size
                    )
                    for i in range(6, 11)
                ],
                "fire": [
                    load_sprites(
                        f"Sprites/Enemy/Ranged_Robot/Ranged_Robot{i}.png", sprite_size
                    )
                    for i in range(11, 21)
                ],
                "death": [
                    load_sprites(
                        f"Sprites/Enemy/Ranged_Robot/Ranged_Robot{i}.png", sprite_size
                    )
                    for i in range(21, 27)
                ],
            }

        self.sprites = RangedRobot.sprite_cash

    def update(self, delta, player, platform, camera, lasers=None):

        self.y_velocity += self.GRAVITY * delta

        self.y += self.y_velocity * delta

        self.moving(platform, camera)

        self.state_cycle(delta)

        if self.current_animation == 'fire':
            if not self.laser_fired:
                self.attack_laser(player, lasers)
                self.laser_fired = True
        
        self.update_animation(delta)
    
    def state_cycle(self, delta):

        self.timer += delta

        if self.timer <= self.idle_time:
            self.current_animation = 'default'
            self.laser_fired = False
        elif self.timer <= self.ready_time:
            self.current_animation = 'shootready'
        elif self.timer <= self.fire_time:
            self.current_animation = 'fire'
        else:
            self.current_animation = 'default'
            self.laser_fired = False
            self.timer = 0 
    
    def moving(self, platform, camera):
        self.check_platform_collision(platform)
    
    def check_platform_collision(self, platforms):
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for platform in platforms:
            platform_rect = platform.get_rect()

            if enemy_rect.colliderect(platform_rect):

                top_overlap = enemy_rect.bottom - platform_rect.top
                bottom_overlap = platform_rect.bottom - enemy_rect.top
                left_overlap = enemy_rect.right - platform_rect.left
                right_overlap = platform_rect.right - enemy_rect.left

                real_overlap = min(
                    top_overlap, bottom_overlap, left_overlap, right_overlap
                )

                if real_overlap == top_overlap and self.y_velocity >= 0:
                    self.y = platform_rect.top - self.height
                    self.y_velocity = 0
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

    def attack_laser(self, player, lasers):
        effect = {"damage": 1, "knockback": (0, -300), "stun_duration": 0.3}

        player.current_x = player.x
        player.current_y = player.y

        angle = math.atan2(player.y - self.y, player.x - self.x)

        if len(lasers) >= 2:
            lasers.pop(0)
        
        laser = DoomLaser(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2,
            default_height=self.laser_radius,
            max_height=self.max_laser_radius,
            angle=angle,
            growth_speed=100,
            effect=effect
        )

        lasers.append(laser)

    def draw(self, surface, camera):
        super().draw(surface, camera)

class Boss23M(Enemy):
    sprite_cash = None

    def __init__(self, x, y):
        boss_hp = 1000000     
        sprite_size = (128, 128)
        super().__init__(boss_hp, sprite_size, False, x, y)

        if Boss23M.sprite_cash is None:
            Boss23M.sprite_cash = {
                "appear": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(1, 16)
                ],
                "idle": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(16, 26)
                ],
                "shootready": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(26, 31)
                ],
                "shoot": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(31, 43)
                ],
                "strikeready": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(43, 46)
                ],
                "falling": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(46, 48)
                ],
                "defenseready": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(48, 51)
                ],
                "defense": [
                    load_sprites("Sprites/Boss/23M-RFT70/23M-51.png", sprite_size)
                ],
                "attackready": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(52, 54)
                ],
                "attack": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(54, 57)
                ],
                "counter": [
                    load_sprites("Sprites/Boss/23M-RFT70/23M-57.png", sprite_size)
                ],
                "stunned": [
                    load_sprites(f"Sprites/Boss/23M-RFT70/23M-{i}.png", sprite_size)
                    for i in range(58, 61)
                ],
            }
        self.sprites = Boss23M.sprite_cash
        self.current_animation = "appear"

        self.phase = 1
        self.state = "spawning"
        self.spawn_timer = 0.8
        self.invincible = True
        self.attack_cooldown = 1.5
        self.attack_timer = 0.0

        self.current_pattern = None
        self.pattern_step = 0
        self.pattern_timer = 0.0

        self.ground_y_offset = 300
        self.move_speed = 1000
        self.y_velocity = 0

        self.edge_shredding_state = None
        self.edge_shredding_teleport_count = 0
        self.guard_damage_taken = 0
        self.guard_damage_limit = 300

        self.boss_attack_term = 0.03
        self.boss_attack_duration = 1.0
        self.boss_pose_duration = 1.0
        self.boss_wave_effect_duration = 3.0
        
        self.cutting_dimension_uses = 0

        self.idle_target_x = None
        self.idle_target_y = None
        self.idle_move_speed = 600
        self.idle_target_change_timer = 0.0
        self.idle_target_change_interval = 0.05


    def take_damage(self, damage, is_forcing=False):
        if self.invincible:
            return False

        if (
            self.state == "attacking"
            and self.current_pattern == "edge_shredding"
            and self.edge_shredding_state == "guarding"
        ):
            self.guard_damage_taken += damage
            if self.guard_damage_taken >= self.guard_damage_limit:
                self.state = "stunned"
                self.pattern_timer = 0.0
            return False

        if (
            self.state == "attacking"
            and self.current_pattern == "edge_shredding"
            and self.edge_shredding_state == "spinning"
        ):
            self.edge_shredding_state = "counter_triggered"
            return False

        took = super().take_damage(damage, is_forcing)
        return took

    def enter_phase2(self):
        self.phase = 2
        self.guard_damage_limit = 500
        self.boss_attack_term = 0.01
        self.boss_attack_duration = 2.0
        self.boss_pose_duration = 1.5
        self.boss_wave_effect_duration = 4.0
        self.attack_cooldown = 1.0

    def update(self, delta, player, camera, pulses, lasers, platforms, after_images):
        if self.HP <= 0 and self.state != "dead":
            self.state = "dead"
            self.current_animation = "stunned"
            self.active = False

        if self.state == "dead":
            self.update_animation(delta)
            return

        if self.state == "stunned":
            self.current_animation = "stunned"
            stun_duration = 3.0
            self.pattern_timer += delta
            if self.pattern_timer >= stun_duration:
                self.state = "idle"
                self.pattern_timer = 0.0
                self.attack_timer = 0.0
            return

        if self.state == "spawning":
            self.spawn_timer -= delta
            self.current_animation = "appear"
            self.y = abs(camera.camera_y) + self.ground_y_offset
            if self.spawn_timer <= 0:
                self.state = "idle"
                self.invincible = False
                self.current_animation = "idle"
            self.update_animation(delta)
            return

        if self.state == "attacking":
            
            self.update_pattern(
                delta, player, camera, pulses, lasers, platforms, after_images
            )
        else:
            if self.phase == 1 and self.HP <= 500:
                self.enter_phase2()
            
            self.attack_timer += delta
            self.idle_target_change_timer += delta
            
            screen_top = abs(camera.camera_y)
            screen_bottom = screen_top + SCREEN_HEIGHT
            
            current_screen_y = self.y - screen_top
            if current_screen_y < 0 or current_screen_y > SCREEN_HEIGHT:
                self.idle_target_change_timer = self.idle_target_change_interval
            
            if self.idle_target_x is None or self.idle_target_change_timer >= self.idle_target_change_interval:
                margin = 100
                self.idle_target_x = random.randint(margin, SCREEN_WIDTH - margin - self.width)
                
                target_screen_offset = random.uniform(SCREEN_HEIGHT * 0.2, SCREEN_HEIGHT * 0.6)
                self.idle_target_y = screen_top + target_screen_offset
                self.idle_target_change_timer = 0.0
            
            if self.idle_target_x is not None and self.idle_target_y is not None:
                distance_to_target = math.hypot(
                    self.idle_target_x - self.x,
                    self.idle_target_y - self.y
                )
                
                if distance_to_target > 10:
                    move_x = (self.idle_target_x - self.x) / distance_to_target * self.idle_move_speed * delta
                    move_y = (self.idle_target_y - self.y) / distance_to_target * self.idle_move_speed * delta
                    
                    self.x += move_x
                    self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
                    
                    self.y += move_y
                    self.y = max(screen_top, min(self.y, screen_bottom - self.height))
                else:
                    self.x = self.idle_target_x
                    self.y = self.idle_target_y
            
            self.current_animation = "idle"
            
            if self.attack_timer >= self.attack_cooldown:
                self.choose_next_pattern(player)
                self.state = "attacking"
                self.pattern_step = 0
                self.pattern_timer = 0.0
                self.attack_timer = 0.0
    
            
            if self.idle_target_x is not None and self.idle_target_y is not None:
                distance_to_target = math.hypot(
                    self.idle_target_x - self.x,
                    self.idle_target_y - self.y
                )
    
                if distance_to_target > 10:
                    move_x = (self.idle_target_x - self.x) / distance_to_target * self.idle_move_speed * delta
                    move_y = (self.idle_target_y - self.y) / distance_to_target * self.idle_move_speed * delta
        
                    self.x += move_x
                    self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
                    self.y += move_y
                    screen_top = abs(camera.camera_y)
                    screen_bottom = screen_top + SCREEN_HEIGHT

                    if self.y < screen_top:
                        self.y = screen_top

                    if self.y + self.height > screen_bottom:
                        self.y = screen_bottom - self.height                    
                    self.current_animation = "idle"
                else:
                    self.x = self.idle_target_x
                    self.y = self.idle_target_y

        if self.attack_timer >= self.attack_cooldown:
            self.choose_next_pattern(player)
            self.state = "attacking"
            self.pattern_step = 0
            self.pattern_timer = 0.0
            self.attack_timer = 0.0

        self.update_animation(delta)

    def choose_next_pattern(self, player):
        patterns_phase1 = ["edge_shredding", "trembling_slash", "dimension_strike", "cutting_dimension", "cutting_dimension"]
        patterns_phase2 = ["edge_shredding", "trembling_slash", "dimension_strike"]
        
        if self.cutting_dimension_uses < 2:
            patterns_phase2.append("cutting_dimension")

        x_dist = abs(self.x - player.x)
        if x_dist > 100:
            if "trembling_slash" in patterns_phase1: 
                patterns_phase1.remove("trembling_slash")
            if "trembling_slash" in patterns_phase2: 
                patterns_phase2.remove("trembling_slash")
        
        if self.y >= player.y:
            if "dimension_strike" in patterns_phase1: 
                patterns_phase1.remove("dimension_strike")
            if "dimension_strike" in patterns_phase2: 
                patterns_phase2.remove("dimension_strike")

        if self.phase == 1:
            pool = patterns_phase1
        else:
            pool = patterns_phase2
        
        if not pool:
            pool = ["edge_shredding"]

        self.current_pattern = random.choice(pool)

    def update_pattern(self, delta, player, camera, pulses, lasers, platforms, after_images):
        if self.current_pattern == "dimension_strike":
            done = self.pattern_dimension_strike(delta, player, camera, pulses, platforms)
        elif self.current_pattern == "edge_shredding":
            done = self.pattern_edge_shredding(delta, player, camera, pulses)
        elif self.current_pattern == "trembling_slash":
            done = self.pattern_trembling_slash(delta, player, camera, after_images)
        elif self.current_pattern == "cutting_dimension":
            done = self.pattern_cutting_dimension(delta, player, camera, lasers)
        else:
            done = True

        if done:
            self.state = "idle"
            self.current_pattern = None
            self.current_animation = "idle"

    def check_platform_collision(self, platforms):
        boss_rect = self.get_rect()
        for platform in platforms:
            platform_rect = platform.get_rect()
            if boss_rect.colliderect(platform_rect):
                if (
                    self.y_velocity >= 0
                    and boss_rect.bottom > platform_rect.top
                    and boss_rect.top < platform_rect.top
                ):
                    return platform
        return None

    def pattern_dimension_strike(self, delta, player, camera, pulses, platforms):
        self.pattern_timer += delta

        if self.pattern_step == 0:
            self.current_animation = "strikeready"
            target_x = player.x
            self.x += (target_x - self.x) * 0.1
            self.y = player.y - 400
            if abs(self.x - target_x) < 20:
                self.pattern_step = 1
                self.pattern_timer = 0.0
                self.y_velocity = 0
                self._ds_breaks = 0

        elif self.pattern_step == 1:
            self.current_animation = "falling"
            self.y_velocity += 12000 * delta
            self.y += self.y_velocity * delta

            max_fall_time = 15.0
            if self.pattern_timer >= max_fall_time:
                self.pattern_step = 2
                self.pattern_timer = 0.0

            if self.get_rect().colliderect(player.get_rect()):
                if player.take_damage(1):
                    if player.coord_debuff_active:
                        self.teleport_player_down(player, platforms, 3)
                    player.apply_coord_debuff()
                    player.apply_stun()
                self.pattern_step = 2
                self.y_velocity = 0

            collided_platform = self.check_platform_collision(platforms)
            if collided_platform:
                if isinstance(collided_platform, BreakablePlatform) and self._ds_breaks < 2:
                    collided_platform.break_platform(None)
                    self._ds_breaks += 1
                else:
                    self.y = collided_platform.y - self.height
                    self.y_velocity = 0
                    
                effect = {"coord_debuff": True, "damage": 1}
                pulse = PulseWave(
                    x=self.x + self.width // 2,
                    y=self.y + self.height,
                    initial_radius=10,
                    max_radius=500,
                    thickness=20,
                    growth_speed=1000,
                    color=BLUE,
                    effect=effect,
                )
                pulses.append(pulse)
                self.pattern_step = 2

        elif self.pattern_step == 2:
            if self.pattern_timer >= 1.0:
                return True

        return False

    def teleport_player_down(self, player, platforms, num_platforms):
        sorted_platforms = sorted(platforms, key=lambda p: p.y, reverse=False)
        current_idx = -1
        for i, p in enumerate(sorted_platforms):
            if player.y <= p.y:
                current_idx = i
                break

        target_idx = current_idx + num_platforms
        if 0 <= target_idx < len(sorted_platforms):
            target_platform = sorted_platforms[target_idx]
            player.x = (
                target_platform.x + target_platform.width // 2 - player.width // 2
            )
            player.y = target_platform.y - player.height - 10
            player.y_velocity = 0

    def pattern_edge_shredding(self, delta, player, camera, pulses):
        self.pattern_timer += delta

        if self.pattern_step == 0:
            self.edge_shredding_teleport_count = 0
            self.pattern_step = 1
            self.pattern_timer = 0.0

        elif self.pattern_step == 1:
            if self.pattern_timer >= 0.05:
                if self.edge_shredding_teleport_count >= 5:
                    self.pattern_step = 3
                    return False
                
                screen_top = abs(camera.camera_y)
                margin = 100
                self.x = random.randint(margin, SCREEN_WIDTH - margin - self.width)
                
                teleport_y_offset = random.uniform(SCREEN_HEIGHT * 0.3, SCREEN_HEIGHT * 0.6)
                self.y = screen_top + teleport_y_offset
                
                self.edge_shredding_teleport_count += 1
                
                effect = {
                    "knockback": (200 * (-1 if self.x > player.x else 1), -300),
                    "coord_debuff": True,
                }
                pulse = PulseWave(
                    x=self.x + self.width // 2,
                    y=self.y + self.height // 2,
                    initial_radius=10,
                    max_radius=500,
                    thickness=15,
                    growth_speed=1000,
                    color=BLUE,
                    effect=effect
                )
                pulses.append(pulse)
                
                self.edge_shredding_state = random.choice(['attackable', 'guarding', 'spinning'])
                self.pattern_timer = 0.0
                self.pattern_step = 2
                self.guard_damage_taken = 0
            
            if self.pattern_timer >= 0.05:
                self.pattern_step = 2
                self.pattern_timer = 0.0

        elif self.pattern_step == 2:
            sub_state_duration = self.boss_pose_duration

            if self.edge_shredding_state == "attackable":
                self.current_animation = "attack"
                if self.get_rect().colliderect(player.get_rect()):
                    if player.take_damage(1):
                        player.apply_coord_debuff()

            elif self.edge_shredding_state == "guarding":
                self.current_animation = "defense"

            elif self.edge_shredding_state == "spinning":
                self.current_animation = "counter"

            elif self.edge_shredding_state == "counter_triggered":
                self.x = player.x - 100 if player.facing > 0 else player.x + 100
                self.y = player.y
                if self.pattern_timer >= self.boss_attack_duration / 2:
                    effect = {"damage": 1, "coord_debuff": True}
                    pulse = PulseWave(
                        x=self.x + self.width // 2,
                        y=self.y + self.height // 2,
                        initial_radius=10,
                        max_radius=500,
                        thickness=10,
                        growth_speed=1000,
                        color=BLUE,
                        effect=effect,
                    )
                    pulses.append(pulse)
                    self.pattern_step = 1
                    self.pattern_timer = 0.0

            if (
                self.pattern_timer >= sub_state_duration
                and self.edge_shredding_state != "counter_triggered"
            ):
                self.pattern_step = 1
                self.pattern_timer = 0.0

        elif self.pattern_step == 3:
            return True

        return False

    def pattern_trembling_slash(self, delta, player, camera, after_images):
        self.pattern_timer += delta

        if self.pattern_step == 0:
            self.current_animation = "strikeready"
            if self.pattern_timer >= 0.5:
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.hypot(dx, dy)
                self._dash_duration = 0.3
                self._dash_vx = (
                    (dx / dist) * (dist / self._dash_duration) if dist > 0 else 0
                )
                self._dash_vy = (
                    (dy / dist) * (dist / self._dash_duration) if dist > 0 else 0
                )

                self.pattern_step = 1
                self.pattern_timer = 0.0
                self._dash_count = 0
                self._afterimage_timer = 0.0

        elif self.pattern_step == 1 or self.pattern_step == 3:
            self.current_animation = "attack"

            self.x += self._dash_vx * delta
            self.y += self._dash_vy * delta

            self._afterimage_timer += delta
            if self._afterimage_timer > 0.05:
                self._afterimage_timer = 0.0
                sprite = self.sprites[self.current_animation][self.animation_frame]
                facing = 1 if self._dash_vx > 0 else -1
                img = AfterImage(self.x, self.y, sprite, 0.5, facing)
                after_images.append(img)

            if self.pattern_timer >= self._dash_duration:
                self._dash_count += 1
                if self._dash_count >= 2:
                    self.pattern_step = 4
                else:
                    self.pattern_step += 1
                self.pattern_timer = 0.0

        elif self.pattern_step == 2:
            self.current_animation = "idle"
            pause_duration = 0.5
            if self.pattern_timer >= pause_duration:
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.hypot(dx, dy)
                self._dash_vx = (
                    (dx / dist) * (dist / self._dash_duration) if dist > 0 else 0
                )
                self._dash_vy = (
                    (dy / dist) * (dist / self._dash_duration) if dist > 0 else 0
                )

                self.pattern_step = 3
                self.pattern_timer = 0.0

        elif self.pattern_step == 4:
            return True

        return False

    def pattern_cutting_dimension(self, delta, player, camera, lasers):
        self.pattern_timer += delta

        if self.pattern_step == 0:
            self.current_animation = "shootready"
            screen_top = abs(camera.camera_y)
            self.x = 50 if player.x > SCREEN_WIDTH / 2 else SCREEN_WIDTH - 150
            self.y = screen_top + SCREEN_HEIGHT * 0.4
            
            self.pattern_step = 1
            self.pattern_timer = 0.0
            self.cutting_dimension_uses += 1
            self._cd_shot_count = 0

        elif self.pattern_step == 1:
            if self.pattern_timer >= 0.5 and self._cd_shot_count == 0:
                self.fire_cutting_dimension_volley(player, camera, lasers)
                self._cd_shot_count += 1
                self.pattern_timer = 0.0
            
            if self.pattern_timer >= 0.5 and self._cd_shot_count == 1:
                self.fire_cutting_dimension_volley(player, camera, lasers)
                self._cd_shot_count += 1
                self.pattern_step = 2
                self.pattern_timer = 0.0

        elif self.pattern_step == 2:
            if self.pattern_timer >= 1.5:
                return True

        return False

    def fire_cutting_dimension_volley(self, player, camera, lasers):
        dx = (player.x + player.width // 2) - (self.x + self.width // 2)
        dy = (player.y + player.height // 2) - (self.y + self.height // 2)
        base_angle = math.atan2(dy, dx)

        angles = [base_angle - math.radians(15), base_angle, base_angle + math.radians(15)]

        start_x = self.x + self.width // 2
        start_y = self.y + self.height // 2
        damage = 50
        max_length = 2000

        for ang in angles:
            beam = LaserBeam(
                start_x,
                start_y,
                ang,
                damage,
                max_length=max_length,
                camera=camera,
                dagger=None
            )
            beam.needs_raycast = True
            beam.camera = camera
            beam.is_boss_laser = True
            lasers.append(beam)

    def draw(self, surface, camera):
        super().draw(surface, camera)


class EnemySpawner:
    def __init__(self):
        self.enemies = []
        self.last_y = 600
        self.next_enemy_pointer = 0

        self.enemy_pattern = [
            "None",
            "FireRobot",
            "None",
            "FireRobot",
            "None",
            "FireRobot",
            "None",
            "RangedRobot",
        ]

        self.min_gap_y = 150
        self.max_gap_y = 500

        self.enemy_data = {
            "FireRobot": {
                "size": (32, 64),
                "hp": 200,
                "can_instant_death": False,
                "spawn_type": "air"
            },
            "RangedRobot": {
                "size": (64, 64),
                "hp": 400,
                "can_instant_death": True,
                "spawn_type": "platform"
            }
        }

        self.ranged_count = 0

        self.ranged_robot_unlocked = False

        for _ in range(3):
            self.generate('default', None)
    
    def change_pattern(self, pattern_list):
        new_pattern = []

        for name in pattern_list:
            new_pattern.append(name)

        self.enemy_pattern = new_pattern
        self.next_enemy_pointer = 0

    
    def generate(self, flag, platforms):
        self.last_y += random.randint(self.min_gap_y, self.max_gap_y)

        pattern_len = len(self.enemy_pattern)
        enemy_type_to_spawn = self.enemy_pattern[self.next_enemy_pointer % pattern_len]
        self.next_enemy_pointer += 1

        if enemy_type_to_spawn == "None":
            return

        enemy_data = self.enemy_data[enemy_type_to_spawn]
        size = enemy_data['size']
        hp = enemy_data['hp']
        instant_deathable = enemy_data['can_instant_death']
        spawn_type = enemy_data['spawn_type']

        enemy = None 

        if spawn_type == 'air':
            x = random.randint(100, SCREEN_WIDTH)
            y = self.last_y
            if enemy_type_to_spawn == 'FireRobot':
                enemy = FireRobot(hp, size, instant_deathable, x, y)
        
        elif spawn_type == 'platform':
            if platforms is None or len(platforms) == 0:
                return

            platform = max(platforms, key=lambda p: p.y)
            platform_x = platform.x
            platform_y = platform.y
            platform_width = platform.width

            enemy_width = size[0]
            if platform_width > enemy_width:
                x = random.randint(platform_x, platform_x + platform_width - enemy_width)
            else:
                x = platform_x
            
            enemy_height = size[1]
            y = platform_y - enemy_height

            if enemy_type_to_spawn == 'RangedRobot' and self.ranged_robot_unlocked:
                ranged_count = sum(1 for e in self.enemies if isinstance(e, RangedRobot))
                if ranged_count < 2:
                    enemy = RangedRobot(hp, size, instant_deathable, x, y)
        
        if enemy is not None:
            self.enemies.append(enemy)



        
    def update(self, camera, flag, platforms):
        if flag == 'Now Lasers will appear.' and not self.ranged_robot_unlocked:
            self.ranged_robot_unlocked = True

        for i in range(len(self.enemies) - 1, -1, -1):
            enemy = self.enemies[i]
            screen_y = enemy.y + camera.camera_y

            if screen_y < -200 or screen_y > 2000:
                self.enemies.pop(i)
                continue
            
            if enemy.is_dead():
                self.enemies.pop(i)
                continue
        
        if len(self.enemies) == 0:
            self.last_y = abs(camera.camera_y) + SCREEN_HEIGHT
        
        max_enemies_on_screen = 8
        if len(self.enemies) < max_enemies_on_screen:
            self.generate(flag, platforms)
    
    def draw(self, camera, surface):
        for enemy in self.enemies:
            enemy.draw(surface, camera)

class PlatformGen:
    def __init__(self):
        self.platforms = []
        self.last_y = 400
        self.platforms_pattern = ["Normal", "Normal", "Breakable", "Breakable", "Breakable"]
        self.pointer = 0
        self.NextPlatform = None
        self.min_gap_y = 70
        self.max_gap_y = 250
        self.min_width = 100
        self.max_width = 400
        self.fixed_height = 32

        self.where_width = 0
        for _ in range(5):
            self.generate()

    def rotation(self):
        self.NextPlatform = self.platforms_pattern[self.pointer % 5]
        self.pointer += 1
    
    def change_pattern(self, pattern_list):
        new_pattern = []

        for name in pattern_list:
            new_pattern.append(name)

        self.platforms_pattern = new_pattern
        self.pointer = 0

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
            elif isinstance(self.platforms[i], NormalPlatform):
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
        self.player.camera = self.camera

        self.enemy_spawner = EnemySpawner()
        self.current_attacks = []
        self.current_pulses = []
        self.current_lasers = []
        self.debrises = []
        self.after_images = []

        self.depth_checker = DepthChecker()
        self.current_event = 'Normal'
        self.weapon_select_flag = False
        self.speed_upable = False

        self.in_upgrade = False
        self.upgrade_shown_depths = set()
        self.selected_upgrades = []
        self.upgrade_ui = UpgradeUI()

        self.boss = None
        self.boss_fight_active = False
        self.boss_fight_start_depth = 0

        self.max_combo = 0
        self.current_combo = 0

        with open('CutsceneData/depth_list.json', 'r') as f:
            self.depth_list = json.load(f)
    
    def draw(self, delta):
        self.game_surface.fill(WHITE)

        self.camera.bg_cycle(self.game_surface)

        if self.screen_blink.active:
            self.screen_blink.update(delta)
            self.screen_blink.draw(self.game_surface)
        
        self.depth_checker.draw_alert(self.game_surface)
    
    def start_upgrade_UI(self, depth_marker):
        self.in_upgrade = True
        self.upgrade_shown_depths.add(depth_marker)
        self.upgrade_ui.open(exclude_list=self.selected_upgrades)
        self.camera.scroll_active = False
        self.player.input_blocked = True

        self.upgrade_start_depth = self.depth_checker.depth
        self.depth_checker.active = False
    
    def update_in_upgrade_phase(self, delta):
        self.player.update(delta, self.PlatformGenerator.platforms, self.debrises, self.current_attacks, self.camera)
        self.camera.camera_chase(delta, self.player)

        self.depth_checker.update(delta, self.camera.camera_y)

        choice = self.upgrade_ui.update(delta)

        if choice is not None:
            self.apply_upgrade(choice)
            self.depth_checker.depth = self.upgrade_start_depth
            self.camera.camera_y = -self.upgrade_start_depth
            self.player.y = abs(self.camera.camera_y) + SCREEN_HEIGHT * 0.65
            self.player.input_blocked = False

            self.in_upgrade = False
            self.camera.scroll_active = True
            self.depth_checker.active = True
            if self.player.hp < self.player.max_hp:
                self.player.hp += 1
    
    def draw_in_upgrade_phase(self, delta):
        self.game_surface.fill(WHITE)
        self.camera.bg_cycle(self.game_surface)

        self.PlatformGenerator.draw(self.camera, self.game_surface)
        for pulse in self.current_pulses:
            if hasattr(pulse, 'is_player_owned') and pulse.is_player_owned:
                continue
            pulse.draw(self.game_surface, self.camera)
        for laser in self.current_lasers:
            laser.draw(self.game_surface, self.camera)
        self.enemy_spawner.draw(self.camera, self.game_surface)

        transparent = self.upgrade_ui.get_fade_alpha(delta)
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        dim.fill(BLACK)
        dim.set_alpha(transparent)
        self.game_surface.blit(dim, (0, 0))

        self.player.draw(self.game_surface, self.camera)

        self.upgrade_ui.draw(self.game_surface)

    def start_boss_fight(self):
        self.boss_fight_active = True
        self.boss = Boss23M(SCREEN_WIDTH // 2 - 64, abs(self.camera.camera_y) + 200)
        
        self.camera.scroll_active = False
        self.depth_checker.active = False
        self.boss_fight_start_depth = self.depth_checker.depth

    def end_boss_fight(self):
        self.boss_fight_active = False
        self.boss = None
        
        resume_depth = 75000
        self.depth_checker.depth = resume_depth
        self.camera.camera_y = -resume_depth
        self.player.y = abs(self.camera.camera_y) + SCREEN_HEIGHT * 0.65
        
        self.camera.scroll_active = True
        self.depth_checker.active = True

    def apply_upgrade(self, upgrade_name):
        self.selected_upgrades.append(upgrade_name)
        if upgrade_name == "FocusingSight":
            self.player.weapon.laser_width_multiplier= 4
            self.player.weapon.cooldown = 0.05

        elif upgrade_name == "Shotgunning":
            self.player.weapon.shotgun_enabled = True

        elif upgrade_name == "DestructiveLaser":
            self.player.weapon.destructive_chance = 0.1

        elif upgrade_name == "Explosive":
            self.player.weapon.explosive_chance = 0.4

        elif upgrade_name == "Bouncing":
            self.player.weapon.max_bounce += 1

        elif upgrade_name == "ExtraSlicing":
            self.player.weapon.extra_slice_chance += 0.01

        elif upgrade_name == "StylishStomping":
            self.player.max_bounce_count = 3

        elif upgrade_name == "WavingStomp":
            self.player.stomp_wave_enabled = True

        elif upgrade_name == "Heal":
            self.player.hp = min(self.player.max_hp, self.player.hp + 4)

        elif upgrade_name == "MechanicalBlood":
            self.player.blood_heal_enabled = True
            self.player.blood_kill_count = 0
    
    def check_boss_laser_hit_player(self, laser, player, camera):
        player_rect = player.get_rect()
        screen_y = camera.draw_again(player.y)
        player_rect.y = screen_y
    
        distance = laser.line_rect_intersection(
            laser.start_x, laser.start_y,
            laser.end_x, laser.end_y,
            player_rect
        )
    
        return distance is not None

    def run(self):
        delta = clock.tick(FPS) / 900

        if self.in_upgrade:
            self.update_in_upgrade_phase(delta)
            self.draw_in_upgrade_phase(delta)
            screen.blit(self.game_surface, (0, 0))
            return

        self.world_timer += delta

        if not self.boss_fight_active:
            self.current_event, self.weapon_select_flag, pattern_change = self.depth_checker.update(delta, self.camera.camera_y)
        else:
            pattern_change = None

        if self.current_event == "23M-RFT70 Appeared." and self.boss is None and not self.boss_fight_active:
            self.start_boss_fight()

        upgrade_trigger_per_depth = 15000
        upgrade_triggered_per_depth = int(self.depth_checker.depth // upgrade_trigger_per_depth)

        if not self.in_upgrade and not self.boss_fight_active and upgrade_triggered_per_depth > 0:
            for marker in range(1, upgrade_triggered_per_depth + 1):
                if marker not in self.upgrade_shown_depths:
                    self.start_upgrade_UI(marker)
                    break
        
        if pattern_change:
            if pattern_change.get("enemy_pattern") is not None:
                self.enemy_spawner.change_pattern(pattern_change.get("enemy_pattern"))
            if pattern_change.get("platform_pattern") is not None:
                self.PlatformGenerator.change_pattern(pattern_change.get("platform_pattern"))
            if pattern_change.get("min_gap_y") is not None:
                self.PlatformGenerator.min_gap_y = pattern_change.get("min_gap_y")
            if pattern_change.get("max_gap_y") is not None:
                self.PlatformGenerator.max_gap_y = pattern_change.get("max_gap_y")
            if pattern_change.get("min_width") is not None:
                self.PlatformGenerator.min_width = pattern_change.get("min_width")
            if pattern_change.get("max_width") is not None:
                self.PlatformGenerator.max_width = pattern_change.get("max_width")


        if self.current_event == 'Speeding Up.' and not self.speed_upable:
            self.speed_upable = True
            self.camera.scrolling_speed += 50
        elif self.current_event == "Speeding Down." and not self.speed_upable:
            self.speed_upable = True
            self.enemy_spawner.enemy_pattern = ["FireRobot", "RangedRobot", "FireRobot", "RangedRobot", "FireRobot", "RangedRobot", "FireRobot", "RangedRobot"]
            self.camera.scrolling_speed -= 50
        elif not self.current_event == "Speeding Up." and not self.current_event == "Speeding Down.":
            self.speed_upable = False

        if self.world_timer < 10:
            self.blink_timer += delta
            if self.blink_timer >= 0.15:
                self.screen_blink.reset()
                self.blink_timer = 0
        else:
            self.blink_timer = 0
            self.screen_blink.reset()
        
        self.player.update(delta, self.PlatformGenerator.platforms, self.debrises, self.current_attacks, self.camera)
        
        if self.player.hitstop_timer <= 0:

            if self.boss_fight_active:
                self.camera.camera_chase(delta, self.player)
            else:
                self.camera.camera_chase(delta, self.player)
                self.enemy_spawner.update(self.camera, self.current_event, self.PlatformGenerator.platforms)


            if self.boss:
                self.boss.update(delta, self.player, self.camera, self.current_pulses, self.current_lasers, self.PlatformGenerator.platforms, self.after_images)
                if self.boss.HP <= 0:
                    self.end_boss_fight()
                elif self.player.get_rect().colliderect(self.boss.get_rect()):
                    if self.player.hitstop_timer <= 0:
                        self.player.take_damage(1)
                for i in range(len(self.current_lasers) - 1, -1, -1):
                    laser = self.current_lasers[i]
                    if isinstance(laser, LaserBeam):
                        laser.update(delta)
                        
                        if not laser.active:
                            self.current_lasers.pop(i)
                            continue
                        
                        targets = self.enemy_spawner.enemies[:]
                        if self.boss:
                            targets.append(self.boss)
                        
                        laser.raycast(targets, self.PlatformGenerator.platforms)
                    
                    elif isinstance(laser, DoomLaser):
                        laser.update(delta)
                        
                        if laser.state == "releasing" and laser.current_width == 0:
                            self.current_lasers.pop(i)
                            continue
                        
                        laser.check_collision(self.player, self.camera)
            
            for attacks in self.current_attacks[:]:
                if isinstance(attacks, LaserBeam):
                    attacks.update(delta)
                    if not attacks.active:
                        self.current_attacks.remove(attacks)
                        continue
                    
                    targets = self.enemy_spawner.enemies + ([self.boss] if self.boss else [])
                    attacks.raycast(targets, self.PlatformGenerator.platforms, self.current_pulses)

                    if self.check_boss_laser_hit_player(attacks, self.player, self.camera):
                        self.player.take_damage(1)


            for enemy in self.enemy_spawner.enemies:
                if isinstance(enemy, FireRobot):
                    enemy.update(delta, self.player, self.camera, self.current_pulses)
                elif isinstance(enemy, RangedRobot):
                    enemy.update(delta, self.player, self.PlatformGenerator.platforms, self.camera, self.current_attacks)
                else:
                    enemy.update(delta, self.player)
            
                if self.player.get_rect().colliderect(enemy.get_rect()):
                    if self.player.state == 'forcing' and enemy.can_death_instantly:
                        enemy.take_damage(1, is_forcing=True)
                    elif self.player.hitstop_timer <= 0:
                        self.player.take_damage(1)
        
            for i in range(len(self.current_pulses) - 1, -1, -1):
                pulse = self.current_pulses[i]
                pulse.update(delta)
    
                effect = pulse.check_collision_enemy(self.player)
                if effect:
                    if "coord_debuff" in effect:
                        if self.player.coord_debuff_active:
                            if self.boss:
                                self.boss.teleport_player_down(self.player, self.PlatformGenerator.platforms, 3)
                        else:
                            self.player.apply_coord_debuff()
        
                    if "slow" in effect:
                        self.player.apply_slow()
        
                    if "knockback" in effect:
                        kb_x, kb_y = effect['knockback']
                        self.player.x_velocity += kb_x
                        self.player.y_velocity += kb_y
                
                targets = self.enemy_spawner.enemies + ([self.boss] if self.boss else [])
                for target in targets:
                    pulse.check_collision_enemy(target)
                
                if not pulse.active:
                    self.current_pulses.pop(i)
            
            for i in range(len(self.after_images) - 1, -1, -1):
                img = self.after_images[i]
                img.update(delta)
                if img.get_rect().colliderect(self.player.get_rect()):
                    if not self.player.coord_debuff_active:
                        self.player.apply_coord_debuff()
                if img.lifetime <= 0:
                    self.after_images.pop(i)
        
            for i in range(len(self.current_attacks) - 1, -1, -1):
                attack = self.current_attacks[i]
                if isinstance(attack, LaserBeam):
                    attack.update(delta)
                    if not attack.active:
                        self.current_attacks.pop(i)
                        continue
                    if hasattr(attack, 'is_boss_laser'):
                        player_as_target = [self.player]
                        attack.raycast(player_as_target, self.PlatformGenerator.platforms, self.current_pulses)
                    else:
                        targets = self.enemy_spawner.enemies[:]
                        if self.boss:
                            targets.append(self.boss)
                        attack.raycast(targets, self.PlatformGenerator.platforms, self.current_pulses)
                elif isinstance(attack, DoomLaser):
                    attack.update(delta)
                    if attack.state == "releasing" and attack.current_width == 0 and attack.stretch_timer > attack.disappearing_duration:
                        self.current_attacks.pop(i)
                        continue
                    attack.check_collision(self.player, self.camera)

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
        for img in self.after_images:
            img.draw(self.game_surface, self.camera)
        for laser in self.current_lasers:
            laser.draw(self.game_surface, self.camera)
        self.enemy_spawner.draw(self.camera, self.game_surface)
        self.player.draw(self.game_surface, self.camera)
        if self.boss:
            self.boss.draw(self.game_surface, self.camera)
        for attacks in self.current_attacks:
            if isinstance(attacks, LaserBeam):
                attacks.draw(self.game_surface, self.camera)
            elif isinstance(attacks, DoomLaser):
                attacks.draw(self.game_surface, self.camera)
        for debris in self.debrises:
            debris.update(delta)
            debris.draw(self.game_surface, self.camera)
        self.debrises = [d for d in self.debrises if d.lifetime > 0]
        if not game_over:
            draw_health_hud(self.game_surface, self.player, abs(self.depth_checker.depth) / 10000)
            draw_boss_health_bar(self.game_surface, self.boss)
        screen.blit(self.game_surface, (0, 0))

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

class DepthChecker:
    def __init__(self):
        self.depth = 0
        self.event_interval = 5000
        self.events = [
            "Normal",
            "Speeding Up.",
            "Now Lasers will appear.",
            "Speeding Up.",
            "Normal",
            "Normal",
            "Speeding Down.",
            "23M-RFT70 will appear.",
            "Normal",
            "23M-RFT70 Appeared.",
            "Speeding Up.",
            "The Howling appeared.",
            "Speeding Up.",
            "Dr.R appeared.",
        ]

        self.alert_text = pygame.font.Font(None, 72)
        self.alert_text_duration = 3.0
        self.alert_text_timer = 0

        self.previous_event_index = 0
        self.current_alert_text = ''
        self.show_alert = False

        self.active = True

        with open('CutsceneData/depth_list.json', 'r') as f:
            self.depth_list = json.load(f)
        self.depth_list = sorted([(int(k), v) for k, v in self.depth_list.items()], key=lambda x: x[0])
        self.pattern_index = -1

    def update(self, delta, camera_y):

        if self.active:
            self.depth = abs(camera_y)

            index = int(self.depth // self.event_interval)
            if index >= len(self.events):
                index = len(self.events) - 1
        
            self.current_event = self.events[index]

            if not index == self.previous_event_index:
                self.current_alert_text = self.current_event
                self.show_alert = True
                self.alert_text_timer = self.alert_text_duration
                self.previous_event_index = index
        
            if self.alert_text_timer > 0:
                self.alert_text_timer -= delta
                if self.alert_text_timer <= 0:
                    self.show_alert = False

            pattern_change = None
        
            next_idx = self.pattern_index + 1
            if next_idx < len(self.depth_list):
                next_check_depth, next_data = self.depth_list[next_idx]
                if self.depth >= next_check_depth:
                    self.pattern_index = next_idx
                    pattern_change = {
                        "enemy_pattern": next_data.get("enemy_pattern"),
                        "platform_pattern": next_data.get("platform_pattern")
                    }
        
            return (self.events[index], True, pattern_change)

        return (self.current_event, False, None)

    def draw_alert(self, screen):
        if not self.show_alert:
            return
        
        alpha = int(255 * self.alert_text_timer / self.alert_text_duration)
        alpha = max(0, min(255, alpha))

        if self.current_alert_text == 'Normal':
            self.current_alert_text = str(
                format(self.depth / 10000, ".1f") + " KM reached."
            )
        
        text = self.alert_text.render(self.current_alert_text, True, WHITE)

        text.set_alpha(alpha)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.85))
        screen.blit(text, text_rect)



with open("CutsceneData/cutscene_data.json", encoding='utf-8') as f:
    cutscene_data = json.load(f)

cutscene_data = {int(k): v for k, v in cutscene_data.items()}

LogoMaker = LogoShow()
Starter = StartMenu()
Ingame = Game()
game_over_screen = GameOverScreen()

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
game_over = False
camera = Camera((SCREEN_WIDTH, SCREEN_HEIGHT))

while not current_state == GameState.EXIT:
    delta = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            current_state = GameState.EXIT
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and current_state == GameState.PLAYING and not game_over and Ingame.player.hitstop_timer <= 0:
                Ingame.player.use_weapon(Ingame.current_attacks)
                
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    game_over = False
                    Ingame = Game()
                    game_over_screen = GameOverScreen()
                    current_state = GameState.PLAYING
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
        max_location = abs(Ingame.camera.camera_y) / 10000
        if not game_over:
            Ingame.run()
        else:
            game_over_screen.update(delta, Ingame.max_combo, max_location)
            game_over_screen.draw(screen)
            

    if Ingame and Ingame.player.hp <= 0:
        if not game_over:
            game_over = True
        
        if game_over:
            game_over_screen.update(delta, Ingame.max_combo, max_location)
            game_over_screen.draw(screen)

    
    pygame.display.flip()

pygame.quit()
sys.exit()