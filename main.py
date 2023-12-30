import pyxel

from typing import TypeVar
import math

N = TypeVar("N", int, float)

WINSOW_W = 256
WINSOW_H = 256

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 10

    def draw(self):
        pyxel.circb(self.x, self.y, self.r, 7)

    def vector(self) -> list:
        return [self.x, self.y, 1]

    def __str__(self) -> str:
        return f"({self.x},{self.y})"
    
def create_point_from_vector(vector :list) -> Point:
    return Point(vector[0], vector[1])

class Line:
    def __init__(self, s :Point, t :Point) -> None:
        self.s = s
        self.t = t
    
    def draw(self):
        pyxel.line(self.s.x, self.s.y, self.t.x, self.t.y, 7)

    def vector(self) -> list:
        return [self.t.x - self.s.x, self.t.y - self.s.y, 0]
    
    def __str__(self) -> str:
        return f"{self.s}->{self.t}"

class Transformer:
    def __init__(self, lines :list[Line]) -> None:
        self.lines = lines
        self.base = Line(lines[0].s, lines[-1].t)
    
    def transrate(self, target :Line) -> list[Line]:
        T1 = [[1, 0, -self.base.s.x], [0, 1, -self.base.s.y], [0, 0, 1]] # Translation matrix to move base.s -> (0, 0)
        targetVector = target.vector()
        baseVector = self.base.vector()
        theta = math.atan2(cross(baseVector, targetVector), inner(baseVector, targetVector))
        R = [[math.cos(theta), -math.sin(theta), 0], 
             [math.sin(theta), math.cos(theta), 0],
             [0, 0, 1]] # Rotation matrix to rotate base vector -> target vector
        scale = length(baseVector) / length(targetVector)
        S = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]] # Scale matrix to scale base -> target
        T2 = [[1, 0, target.s.x], [0, 1, target.s.y], [0, 0, 1]] # Translation matrix to move (0, 0) -> target
        # T = product_matrix(T2, product_matrix(S, product_matrix(R, T1)))
        T = product_matrix(T2, T1)
        print("T1", T1)
        print("T2", T2)
        print("T", T)
        new_lines = []
        for line in self.lines:
            new_sv = product(T, line.s.vector())
            new_tv = product(T, line.t.vector())
            new_line = Line(create_point_from_vector(new_sv), create_point_from_vector(new_tv))
            new_lines.append(new_line)
        return new_lines

def product_matrix(A :list[list[N]], B :list[list[N]]) -> list[list[N]]:
    result = []
    BT = list(zip(*B))
    for column_B in BT:
        row_result = []
        for row_A in A:
            tmp = 0
            for a, b in zip(column_B, row_A):
                tmp += a*b
            row_result.append(tmp)
        result.append(row_result)
    return result

def product(A :list[list[N]], B: list[N]) -> list[N]:
    result = []
    for row_A in A:
        tmp = 0
        for a, b in zip(row_A, B):
            tmp += a*b
        result.append(tmp)
    return result

def cross(a :list[N], b :list[N]) -> N:
    return a[0]*b[0] + a[1]*b[1]

def inner(a :list[N], b :list[N]) -> N:
    return a[0]*b[0] - a[1]*b[0]

def length(a :list[N]) -> N:
    return math.sqrt(a[0]**2 + a[1]**2)

class App:
    def __init__(self):
        pyxel.init(WINSOW_W, WINSOW_H)
        self.points = [Point(50, 150), Point(100, 100), Point(150, 150),]
        self.lines = [Line(*self.points[:2]), Line(*self.points[1:3])]
        self.transformer = Transformer(self.lines)
        self.new_lines = []
        for line in self.lines:
            self.new_lines.extend(self.transformer.transrate(line))
        print(*self.lines)
        print(*self.new_lines)
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        if pyxel.frame_count % 60 < 30:
            for line in self.lines:
                line.draw()
        else:
            for line in self.new_lines:
                line.draw()
        for point in self.points:
            point.draw()

App()
