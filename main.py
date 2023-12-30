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
    def __init__(self, s :Point, t :Point, reverse :bool=False) -> None:
        self.s = s
        self.t = t
        self.reverse = reverse
    
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
        scale = length(targetVector) / length(baseVector)
        S = [[scale, 0, 0], [0, scale, 0], [0, 0, 1]] # Scale matrix to scale base -> target
        if target.reverse:
            tau = math.atan2(targetVector[1], targetVector[0])
            M = [[math.cos(2*tau), math.sin(2*tau), 0], 
                [math.sin(2*tau), -math.cos(2*tau), 0],
                [0, 0, 1]] # Reflection matrix to reflect symmetrically to the target vector
        else:
            M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        T2 = [[1, 0, target.s.x], [0, 1, target.s.y], [0, 0, 1]] # Translation matrix to move (0, 0) -> target
        T = product_matrix(T2, product_matrix(M, product_matrix(S, product_matrix(R, T1))))
        new_lines = []
        for line in self.lines:
            new_sv = product(T, line.s.vector())
            new_tv = product(T, line.t.vector())
            new_line = Line(create_point_from_vector(new_sv), create_point_from_vector(new_tv), line.reverse)
            new_lines.append(new_line)
        return new_lines

def finish_translate(line :Line) -> bool:
    return abs(int(line.s.x) - int(line.t.x)) + abs(int(line.s.y) - int(line.t.y)) <= 1

def product_matrix(A :list[list[N]], B :list[list[N]]) -> list[list[N]]:
    result = []
    BT = list(zip(*B))
    for row_A in A:
        row_result = []
        for column_B in BT:
            tmp = 0
            for a, b in zip(row_A, column_B):
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

def inner(a :list[N], b :list[N]) -> N:
    return a[0]*b[0] + a[1]*b[1]

def cross(a :list[N], b :list[N]) -> N:
    return a[0]*b[1] - a[1]*b[0]

def length(a :list[N]) -> N:
    return math.sqrt(a[0]**2 + a[1]**2)

class Editor:
    def __init__(self) -> None:
        self.points = []
    
    def update(self):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, repeat=10):
            self.points.append(Point(pyxel.mouse_x, pyxel.mouse_y))
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT, repeat=10):
            if self.points:
                self.points.pop()

    def generate(self) -> tuple[list[Point], list[Line]]:
        lines = []
        for i, pair in enumerate(zip(self.points, self.points[1:])):
            lines.append(Line(pair[0], pair[1], bool(i%2)))
        return self.points, lines

    def generatable(self) -> bool:
        return len(self.points) >= 3
    
    def draw(self):
        for point in self.points:
            point.draw()

class App:
    def __init__(self):
        pyxel.init(WINSOW_W, WINSOW_H)
        self.editor = Editor()
        self.state = "Edit"

        self.points = []
        self.lines = []
        self.finish_lines = []
        self.transformer = Transformer(self.lines)
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.state == "Edit":
            self.editor.update()
            if pyxel.btnp(pyxel.KEY_SPACE, repeat=60) and self.editor.generatable():
                self.points, self.lines = self.editor.generate()
                self.state = "Translate"
        elif self.state == "Translate":
            if pyxel.btnp(pyxel.KEY_SPACE, repeat=60):
                new_lines = []
                for line in self.lines:
                    new_lines.extend(self.transformer.transrate(line))
                self.lines = [line for line in new_lines if not finish_translate(line)]
                self.finish_lines.extend([line for line in new_lines if line not in self.lines])
        else:
            pass

    def draw(self):
        pyxel.cls(0)
        if self.state == "Edit":
            self.editor.draw()
        elif self.state == "Translate":
            for line in self.lines:
                    line.draw()
            for line in self.finish_lines:
                    line.draw()
            for point in self.points:
                point.draw()
        else:
            pass

App()
