import pygame as pg
import sys
from time import time
from random import randint
from pygame.math import Vector2
import pickle

try:
    with open("highscore.pkl", "rb") as f:
        highscore = pickle.load(f)
except:
    highscore = 0

pg.init()
screen = pg.display.set_mode((600, 700))
clock = pg.time.Clock()

pg.display.set_caption("Blood Ball - A Flappy Bird Clone")
GRAVITY = Vector2(0, 1000)
speed = 150

font = pg.font.Font("Mono.ttf", 30) 
font2 = pg.font.Font("Mono.ttf", 100)

class Birdy:
    def __init__(self, pos):
        self.pos = pos
        self.vel = Vector2(0, 0)
        self.collision_points = [Vector2(1,0).rotate(angle)*20 for angle in range(0, 360, 30)]
        self.prev_points = []

        self.counter = 0
        self.radius = 20

    def jump(self):
        self.vel = Vector2(0, -450)
    
    def update(self, deltatime):
        self.counter += deltatime
        if self.counter >= 0.023:
            self.prev_points.append(self.pos.copy())
            self.prev_points = self.prev_points[-40:]
            self.counter = 0

        for point in self.prev_points:
            point += Vector2(-speed, 0) * deltatime

        self.vel += GRAVITY * deltatime
        self.pos += self.vel * deltatime

        if not 0 < self.pos.y < 600:
            return True
    
    def draw(self, screen):
        colors = ["#ffeeee", "#ffdddd", "#ffcccc", "#ffbbbb", "#ffaaaa", "#ff9999", "#ff7777", "#ff6666", "#ff5555", "#ff4444"]

        for i, point in enumerate(self.prev_points):
            pg.draw.circle(screen, colors[int(i/4)], point, i/2)

        pg.draw.circle(screen, "#ee0000", self.pos, self.radius)



class Pipe:
    VELOCITY = Vector2(-speed, 0)
    score = 0

    def __init__(self, x):
        self.hightfactor = randint(-2, 2)
        self.pos = Vector2(x, 300 + 50*self.hightfactor)
        self.rect1 = pg.Rect(self.pos - Vector2(0, 500), (50, 400))
        self.rect2 = pg.Rect(self.pos + Vector2(0, 100), (50, 400))
        self.score_rect = pg.Rect(self.pos - Vector2(-25, 100), (25, 200))
        self.score_added = False

    def update(self, deltatime):
        self.pos += self.VELOCITY * deltatime
        if self.pos.x < -50:
            self.pos.x = 800
            self.hightfactor = randint(-2,2)
            self.pos.y = 300 + 50 * self.hightfactor
            self.score_added = False

        self.rect1 = pg.Rect(self.pos - Vector2(0, 500), (50, 400))
        self.rect2 = pg.Rect(self.pos + Vector2(0, 100), (50, 400))
        self.score_rect = pg.Rect(self.pos - Vector2(-25, 100), (25, 200))

        Pipe.VELOCITY = Vector2(-speed, 0)

    def add_score(self):
        if not self.score_added:
            Pipe.score += 1
            self.score_added = True
    
    def draw(self, screen):
        pg.draw.rect(screen, "#aaaaaa", self.rect1, 0, 10)
        pg.draw.rect(screen, "#aaaaaa", self.rect2, 0, 10)

        pg.draw.rect(screen, "#bbbbbb", self.rect1, 10, 10)
        pg.draw.rect(screen, "#bbbbbb", self.rect2, 10, 10)

birdy = Birdy(Vector2(100, 300))

def main():
    global speed, highscore

    birdy.pos = Vector2(100, 300)
    birdy.vel = Vector2(0, 0)
    birdy.prev_points = []

    pipes = [Pipe(400+200*x) for x in range(4)]
    deltatime = 1/60

    started = False
    ended = False

    if Pipe.score > highscore:
        highscore = Pipe.score
        with open("highscore.pkl", "wb") as f:
            pickle.dump(highscore, f)

    Pipe.score = 0
    speed = 150


    while True:
        prevtime = time()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    started = True
                    birdy.jump()

                    if ended:
                        return True

            
        screen.fill("#dddddd")

        if started and not ended:
            if birdy.update(deltatime):
                ended = True
            
            for point in birdy.collision_points:
                for pipe in pipes:
                    if pipe.rect1.collidepoint(birdy.pos + point) or pipe.rect2.collidepoint(birdy.pos + point):
                        ended = True
                    if pipe.score_rect.collidepoint(birdy.pos + point):
                        pipe.add_score()
                    

        for pipe in pipes:
            pipe.draw(screen)
            if started and not ended:
                pipe.update(deltatime)


        birdy.draw(screen)

        # UI

        pg.draw.rect(screen, "#333333", (0, 625, 600, 100))

        if not started:
            label = font.render("Press Space to start", True, "#ffffff")
            screen.blit(label, label.get_rect(center=(300, 667)))
            birdy.radius = max((birdy.radius - 50), 20)
        elif ended:
            label = font.render("Press Space to restart", True, "#ffffff")
            screen.blit(label, label.get_rect(center=(300, 667)))
            birdy.radius = min((birdy.radius + 50), 1000)
            if birdy.radius == 1000:
                info_label1 = font.render("Game Over", True, "#ffffff")
                screen.blit(info_label1, info_label1.get_rect(center=(300, 100)))

                info_label2 = font.render(f"Your Score", True, "#ffffff")
                screen.blit(info_label2, info_label2.get_rect(center=(150, 200)))

                score_label = font2.render(f"{Pipe.score}", True, "#ffffff")
                screen.blit(score_label, score_label.get_rect(center=(150, 300)))

                info_label3 = font.render(f"High Score", True, "#ffffff")
                screen.blit(info_label3, info_label3.get_rect(center=(450, 200)))

                score_label2 = font2.render(f"{highscore}", True, "#ffffff")
                screen.blit(score_label2, score_label2.get_rect(center=(450, 300)))
        else:
            label = font.render(f"Score: {Pipe.score} || Speed: {speed}", True, "#ffffff")
            screen.blit(label, label.get_rect(center=(300, 667)))


        clock.tick(60) 

        deltatime = time() - prevtime

        pg.display.flip()

        if Pipe.score > 10:
            speed = min((150 + 5 * (Pipe.score-10)), 300)


if __name__ == "__main__":
    while True:
        main()