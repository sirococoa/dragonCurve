import pyxel

WINSOW_W = 256
WINSOW_H = 256

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 10

    def draw(self):
        pyxel.circb(self.x, self.y, self.r, 7)

class Line:
    def __init__(self, s :Point, t :Point) -> None:
        self.s = s
        self.t = t
    
    def draw(self):
        pyxel.line(self.s.x, self.s.y, self.t.x, self.t.y, 7)

class App:
    def __init__(self):
        pyxel.init(WINSOW_W, WINSOW_H)
        self.points = [Point(50, 50), Point(50, 150), Point(150, 150), Point(150, 50)]
        self.lines = [Line(*self.points[:2]), Line(*self.points[1:3]), Line(*self.points[2:4])]
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        for line in self.lines:
            line.draw()
        for point in self.points:
            point.draw()

App()
