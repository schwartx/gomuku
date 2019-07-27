from random import randint

class Robot:
    def __init__(self):
        self.steps = []
        self.current_step = tuple()

    def gen_step(self):
        self.current_step = randint(0,7), randint(0,7)

    def play(self):
        self.gen_step()
        while self.current_step in self.steps:
            self.gen_step()
            self.steps.append(self.current_step)
        return self.current_step
