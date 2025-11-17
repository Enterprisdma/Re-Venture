import subprocess
import sys

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
        "Font/DNFForgedBlade-Medium.ttf",
        "Sprites/Backgrounds/5km.png",
        "CutsceneData/cutscene_data.json",
    ]

    assets += [f"Sprites/Backgrounds/Main{i}.png" for i in range(1, 5)]
    assets += [f"Sprites/Cutscene/StartCutscene{i}.png" for i in range(1, 3)]
    assets += [f"Sprites/Player/LEEJAMMIN{i}.png" for i in range(1, 17)]

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
    
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_velocity = 0
        self.y_velocity = 0
        self.gravity = 1200
        self.max_fall_speed = 1500
        self.accel = 0
        self.width = 64
        self.height = 64
        self.grounded = False
        self.state = "Normal" # "forcing", "stunned", "sliding"
        self.facing = 1
        self.iswarped = False

        self.slide_timer = 0
        self.slide_holding = False
        self.sliding_velocity = 5000

        self.weapon_cooldown_list = []
        

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.camera = Camera((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.fading = UIManager(duration=1.0)
        self.background = pygame.image.load("5km.png")

        self.world_timer = 0
        self.blink_timer = 0
        self.timer = 0

        self.fading.duration = 3.0
        self.fade_in = 1.0
        self.fade_out = 1.0
        self.world_transparency = 0

        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.screen_blink = ScreenBlinker(BLACK, 10.0)
    
    def draw(self, delta):
        self.game_surface.fill(WHITE)
        self.game_surface.blit(self.background, (0, 0))

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
        

        if self.world_timer <= self.fade_in:
            surface_transparent = self.fading.fadein(delta)
            self.game_surface.set_alpha(surface_transparent)
        else:
            self.game_surface.set_alpha(255)

        self.draw(delta)

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
