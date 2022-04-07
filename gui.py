import os, sys
with open(os.devnull, 'w') as f:
    oldstdout = sys.stdout
    sys.stdout = f
    import pygame
    sys.stdout = oldstdout
import random


class Graphics:
    pixelWidth, pixelHeight, page, cubeSize = 0, 0, 0, 0

    def __init__(self, cubeSize, game, delay=1000):
        self.cubeSize = cubeSize
        h=len(game.foodGrid); w=len(game.foodGrid[0])
        self.pixelWidth, self.pixelHeight = w * self.cubeSize + w - 1, h * self.cubeSize + h - 1
        self.page = pygame.display.set_mode((self.pixelWidth + 7 * self.cubeSize, self.pixelHeight + 2 * self.cubeSize))
        self.delay=0
        self.redrawPage(game)
        self.delay=delay

    def wait(self, time):
        for i in range(time//10):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            pygame.time.wait(time//10)

    def redrawPage(self, game):
        self.wait(self.delay)
        self.page.fill((0, 0, 0))
        self.drawFood(game)
        self.drawSnake(game)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

    def drawFood(self, game):
        foodGrid=list(zip(*game.foodGrid))
        for i in range(len(foodGrid)):
            for j in range(len(foodGrid[i])):
                color = foodGrid[i][j]/max([max(fg) for fg in foodGrid])*255 // 1
                self.colorCube(i, j, (255 - color, 255, 255 - color))

    def drawSnake(self, game):
        for i, snake in enumerate(game.agent_list):
            if snake.body==[]: continue
            for part in snake.body:
                self.colorCube(part[1], part[0], self.randColor(i+1))
            self.markHead(snake.body[-1][1], snake.body[-1][0])

    def drawTextLog(self, text, color):
        color=self.randColor(color + 1)
        pygame.draw.rect(self.page, (0, 0, 0),
                         (0, self.pixelHeight, self.pixelWidth + 6 * self.cubeSize, 2 * self.cubeSize))
        pygame.font.init()
        font = pygame.font.SysFont('arial', self.cubeSize)
        text_surface = font.render(text, True, color)
        self.page.blit(text_surface, (self.cubeSize // 3, self.pixelHeight + self.cubeSize // 3))
        pygame.display.update()
        # self.wait(self.delay)

    def drawScores(self, game):
        teams=[]
        for agent_idx, agent in enumerate(game.agent_list):
            if agent.team not in teams: teams.append((agent_idx, agent.team))

        for i, (agent_idx, team_name) in enumerate(teams):
            pygame.draw.rect(self.page, (0, 0, 0), (0, self.pixelHeight, self.pixelWidth, 2 * self.cubeSize))
            pygame.font.init()
            font = pygame.font.SysFont('arial', self.cubeSize)

            color = self.randColor(agent_idx + 1)
            text = "team " + team_name + ": " + str(game.get_team_score(i))
            text_surface = font.render(text, True, color)

            x = len(game.foodGrid[0]) * (self.cubeSize + 1) + self.cubeSize // 3
            y = i * self.cubeSize + i * self.cubeSize // 3
            self.page.blit(text_surface, (x, y))

            pygame.display.update()

    def colorCube(self, i, j, color):
        pygame.draw.rect(self.page, color, (self.pixelPos(i), self.pixelPos(j), self.cubeSize, self.cubeSize))

    def markHead(self, i, j):
        circlePos = (self.pixelPos(i) + 2 * self.cubeSize // 7, self.pixelPos(j) + 2 * self.cubeSize // 5)
        pygame.draw.circle(self.page, (0, 0, 0), circlePos, self.cubeSize // 10)
        circlePos = (self.pixelPos(i) + 5 * self.cubeSize // 7, self.pixelPos(j) + 2 * self.cubeSize // 5)
        pygame.draw.circle(self.page, (0, 0, 0), circlePos, self.cubeSize // 10)

    def pixelPos(self, i):
        return i * self.cubeSize + i

    def getAction(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        return "LEFT"
                    if event.key == pygame.K_RIGHT:
                        return "RIGHT"
                    if event.key == pygame.K_DOWN:
                        return "DOWN"
                    if event.key == pygame.K_UP:
                        return "UP"

    def randColor(self, n):
        random.seed(312)
        ret = 0
        r = int(random.random() * 220) + 30
        g = int(random.random() * 150)
        b = int(random.random() * 200) + 30
        step = 256 / n
        for i in range(n):
            r += step
            g += step
            b += step
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            ret = (r, g, b)
        return ret
