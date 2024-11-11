# 이것은 각 상태들을 객체로 구현한 것임.

from pico2d import get_time, load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, load_font
from state_machine import *
from ball import Ball
import game_world
import game_framework



class Idle:
    @staticmethod
    def enter(boy, e):
        if start_event(e):
            boy.action = 3
            boy.face_dir = 1
        elif right_down(e) or left_up(e):
            boy.action = 2
            boy.face_dir = -1
        elif left_down(e) or right_up(e):
            boy.action = 3
            boy.face_dir = 1

        boy.frame = 0
        boy.wait_time = get_time()

    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()

    @staticmethod
    def do(boy):

        boy.frame = (boy.frame + boy.FRAMES_PER_ACTION * boy.ACTION_PER_TIME * game_framework.frame_time) % 5

        if boy.frame == 0:
            boy.action += 1

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(int(boy.frame) * 186, boy.action * 168, 186, 168, boy.x, boy.y)
        if boy.face_dir == -1:
            boy.image.clip_composite_draw(int(boy.frame) * 186, boy.action * 168, 186, 168, 0, 'h', boy.x, boy.y, 186, 168)


class Sleep:
    @staticmethod
    def enter(boy, e):
        if start_event(e):
            boy.face_dir = 1
            boy.action = 3
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + boy.FRAMES_PER_ACTION * boy.ACTION_PER_TIME * game_framework.frame_time) % 5
        if boy.frame == 0:
            boy.action += 1

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 300, 100, 100,
                                          3.141592 / 2, '', boy.x - 25, boy.y - 25, 100, 100)
        else:
            boy.image.clip_composite_draw(int(boy.frame) * 100, 200, 100, 100,
                                          -3.141592 / 2, '', boy.x + 25, boy.y - 25, 100, 100)


class Run:

    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e): # 오른쪽으로 RUN
            boy.dir, boy.face_dir, boy.action = 1, 1, 1
        elif left_down(e) or right_up(e): # 왼쪽으로 RUN
            boy.dir, boy.face_dir, boy.action = -1, -1, 0


    @staticmethod
    def exit(boy, e):
        if space_down(e):
            boy.fire_ball()


    @staticmethod
    def do(boy):
        PIXEL_PER_METER = (10.0 / 1.0)
        RUN_SPEED_KMPH = 20.0
        RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
        RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
        RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

        boy.x += boy.dir * RUN_SPEED_PPS * game_framework.frame_time
        boy.frame = (boy.frame + boy.FRAMES_PER_ACTION * boy.ACTION_PER_TIME * game_framework.frame_time) % 5
        if boy.frame == 0:
            boy.action += 1

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:
            boy.image.clip_draw(int(boy.frame) * 186, boy.action * 168, 186, 168, boy.x, boy.y)
        if boy.face_dir == -1:
            boy.image.clip_composite_draw(int(boy.frame) * 186, boy.action * 168, 186, 168, 0, 'h', boy.x, boy.y, 186, 168)





class Boy:

    def __init__(self):
        self.TIME_PER_ACTION = 0.7
        self.ACTION_PER_TIME = 1.0 / self.TIME_PER_ACTION
        self.FRAMES_PER_ACTION = 5
        self.x, self.y = 400, 90
        self.face_dir = 1
        self.image = load_image('bird_animation.png')
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, space_down: Idle},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle, space_down: Run},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle}
            }
        )
        self.font = load_font('ENCR10B.TTF', 16)

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # 여기서 받을 수 있는 것만 걸러야 함. right left  등등..
        self.state_machine.add_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()

    def fire_ball(self):
        ball = Ball(self.x, self.y, self.face_dir * 10)
        game_world.add_object(ball)