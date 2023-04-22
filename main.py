from ursina import *
from confic import *


class Game(Ursina):
    def __init__(self):
        super().__init__()
        # window.fullscreen = True
        Entity(model='sphere', scale=sphere_scale, texture=text_sky, double_sided=True)  # задаёт внешнюю сферу
        Entity(model='quad', scale=quad_scale, texture=tex_wh, texture_scale=(quad_scale, quad_scale), rotation_x=90,
               y=-5, color=color.light_gray)  # задаёт плоскость, важна для наглядности
        EditorCamera()  # даёт управление камерой

        self.load_game()

    def creating(self):  # создание индексов элементов кубика
        self.RIGHT = {Vec3(1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.LEFT = {Vec3(-1, y, z) for y in range(-1, 2) for z in range(-1, 2)}
        self.FRONT = {Vec3(x, y, -1) for x in range(-1, 2) for y in range(-1, 2)}
        self.BACK = {Vec3(x, y, 1) for x in range(-1, 2) for y in range(-1, 2)}
        self.TOP = {Vec3(x, 1, z) for x in range(-1, 2) for z in range(-1, 2)}
        self.BOTTOM = {Vec3(x, -1, z) for x in range(-1, 2) for z in range(-1, 2)}

        self.SIDE_POSITIONS = self.RIGHT | self.LEFT | self.FRONT | self.BACK | self.TOP | self.BOTTOM

    def load_game(self):
        self.PARENT = Entity()

        self.creating()
        self.CUBES = [Entity(model=model_cube, texture=texture_cube, position=pos) for pos
                      in self.SIDE_POSITIONS]  # создание самих кубиков

        self.trans_to_front()  # задание отсчёта для поворотов

        self.animation_time = start_animation_time

        self.action_trigger = True  # для отсутствия наложения действий друг на друга
        self.mode_of_spin = False  # для смены направления вращения сторон

        self.comand = ''
        self.comand_trigger = False
        self.comand_message = Text(text='', x=0, y=-0.40, color=color.black)
        self.instr_mode_comand = Text(text=comand_text_1, x=0, y=-0.43, color=color.black)
        b = Button(text=button_text, color=color.light_gray, scale=button_scale, y=-0.45, x=-0.14)
        b.fit_to_text()
        b.on_click = self.play_last_comand

        self.message = Text(origin=(-0.5, 19), color=color.black)  # подсказка для смены направления вращения
        self.switch_mode()
        Text.default_resolution = text_size_const * Text.size

        alfa = dedent(alfa_text).strip()
        self.instuction = Text(text=alfa, x=0.6, y=0.4, color=color.black)  # подсказка клавиш для поворотов

        self.create_sensors()  # создание точек для смены стороны вращения

    def randomizing(self, k=randomizing_constant):  # случайное перемешивание кубика
        [self.rand_func(random.choice(list(self.rotation_axes_all_cube))) for i in range(k)]

    def rand_func(self, side_name):
        rotation_axis = self.rotation_axes_all_cube[side_name]
        cube_positions = self.cubes_side_positons[side_name]

        self.reparent_to_scene()
        for cube in self.CUBES:
            if cube.position in cube_positions:
                cube.parent = self.PARENT
                exec(f'self.PARENT.rotation_{rotation_axis[1]} = 90')

    def create_sensors(self):  # создание сенсоров для смены стороны вращения + перемешивание

        create_sensor = lambda name, pos, scale, texture: Entity(name=name, position=pos, model='sphere',
                                                                 texture=texture,
                                                                 scale=scale, collider='box')
        self.random_st_sensor = create_sensor(name='LEFT', pos=(-6, -2, 0), scale=(s_s, s_s, s_s),
                                              texture='textures/blue')
        self.random_st_sensor = create_sensor(name='FRONT', pos=(0, -2, -6), scale=(s_s, s_s, s_s),
                                              texture='textures/red')
        self.random_st_sensor = create_sensor(name='RIGHT', pos=(6, -2, 0), scale=(s_s, s_s, s_s),
                                              texture='textures/green')
        self.random_st_sensor = create_sensor(name='BACK', pos=(0, -2, 6), scale=(s_s, s_s, s_s),
                                              texture='textures/orange')

        self.random_st_sensor = Entity(name='RANDOM', position=(0, -4.99, 0), rotation_x=90, model='quad',
                                       texture=random_texture, scale=(1, 1), collider='box')

    def switch_mode(self):  # смена направления вращения
        self.mode_of_spin = not self.mode_of_spin
        msg = (f"{'Normal spin mode' if self.mode_of_spin else 'UNNormal spin mode ON'}"
               f" (to switch - press middle mouse button)").strip()
        self.message.text = msg

    def switch_trigger(self):
        self.action_trigger = not self.action_trigger

    def rotation(self, side_name):  # основная функция вращения сторон кубика
        self.action_trigger = False
        rotation_axis = self.rotation_axes_all_cube[side_name]
        positions = self.cubes_side_positons[side_name]

        self.reparent_to_scene()

        for cube in self.CUBES:
            if cube.position in positions:
                cube.parent = self.PARENT
                if (rotation_axis[0] == '1') == self.mode_of_spin:
                    eval(f'self.PARENT.animate_rotation_{rotation_axis[1]}(90, duration=self.animation_time)')
                else:
                    eval(f'self.PARENT.animate_rotation_{rotation_axis[1]}(-90, duration=self.animation_time)')
        invoke(self.switch_trigger, delay=self.animation_time + 0.05)

    def trans_to_front(self):  # смена центра вращения
        self.rotation_axes_all_cube = {'LEFT': '0x', 'RIGHT': '1x', 'TOP': '1y', 'BOTTOM': '0y', 'FRONT': '1z',
                                       'BACK': '0z'}
        self.cubes_side_positons = {'LEFT': self.LEFT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.RIGHT, 'FRONT': self.FRONT,
                                    'BACK': self.BACK, 'TOP': self.TOP}

    def trans_to(self, side):
        if side == 'LEFT':
            self.rotation_axes_all_cube['LEFT'] = '0z'
            self.rotation_axes_all_cube['RIGHT'] = '1z'
            self.rotation_axes_all_cube['FRONT'] = '0x'
            self.rotation_axes_all_cube['BACK'] = '1x'
            self.cubes_side_positons['LEFT'] = self.BACK
            self.cubes_side_positons['RIGHT'] = self.FRONT
            self.cubes_side_positons['FRONT'] = self.LEFT
            self.cubes_side_positons['BACK'] = self.RIGHT
        elif side == 'RIGHT':
            self.rotation_axes_all_cube['LEFT'] = '1z'
            self.rotation_axes_all_cube['RIGHT'] = '0z'
            self.rotation_axes_all_cube['FRONT'] = '1x'
            self.rotation_axes_all_cube['BACK'] = '0x'
            self.cubes_side_positons['LEFT'] = self.FRONT
            self.cubes_side_positons['RIGHT'] = self.BACK
            self.cubes_side_positons['FRONT'] = self.RIGHT
            self.cubes_side_positons['BACK'] = self.LEFT
        elif side == 'BACK':
            self.rotation_axes_all_cube['LEFT'] = '1x'
            self.rotation_axes_all_cube['RIGHT'] = '0x'
            self.rotation_axes_all_cube['FRONT'] = '0z'
            self.rotation_axes_all_cube['BACK'] = '1z'
            self.cubes_side_positons['LEFT'] = self.RIGHT
            self.cubes_side_positons['RIGHT'] = self.LEFT
            self.cubes_side_positons['FRONT'] = self.BACK
            self.cubes_side_positons['BACK'] = self.FRONT

    def reparent_to_scene(self):  # привязка к мировой сцене для поворотов
        for cube in self.CUBES:
            if cube.parent == self.PARENT:
                world_pos = round(cube.world_position, 1)
                world_rot = cube.world_rotation
                cube.parent = scene
                cube.position = world_pos
                cube.rotation = world_rot
        self.PARENT.rotation = 0

    def switch_command_trigger(self):
        self.comand_trigger = not self.comand_trigger
        if not self.comand_trigger:
            self.instr_mode_comand.text = comand_text_1
        else:
            self.instr_mode_comand.text = comand_text_2

    def upd_text_message(self):
        self.comand_message.text = 'last comand = ' + self.comand[::2]

    def rotation_bez_animation(self, side_name, norm=True):
        self.action_trigger = False
        rotation_axis = self.rotation_axes_all_cube[side_name]
        positions = self.cubes_side_positons[side_name]

        self.reparent_to_scene()

        for cube in self.CUBES:
            if cube.position in positions:
                cube.parent = self.PARENT
                if (rotation_axis[0] == '1') == norm:
                    exec(f'self.PARENT.rotation_{rotation_axis[1]} = 90')
                else:
                    exec(f'self.PARENT.rotation_{rotation_axis[1]} =-90')

    def play_last_comand(self):
        if not self.action_trigger:
            return
        norm = True
        for elem in self.comand[::2]:
            if elem == 'l':
                self.rotation_bez_animation('LEFT', norm)
                norm = True
            elif elem == 'r':
                self.rotation_bez_animation('RIGHT', norm)
                norm = True
            elif elem == 't':
                self.rotation_bez_animation('TOP', norm)
                norm = True
            elif elem == 'b':
                self.rotation_bez_animation('BACK', norm)
                norm = True
            elif elem == 'd':
                self.rotation_bez_animation('BOTTOM', norm)
                norm = True
            elif elem == 'f':
                self.rotation_bez_animation('FRONT', norm)
                norm = True
            elif elem == '-':
                norm = not norm
        self.action_trigger = True

    def input(self, key, is_raw=False):
        if self.comand_trigger:
            if key == 'a':
                self.comand += 'l'
            elif key == 'd':
                self.comand += 'r'
            elif key == 'w':
                self.comand += 't'
            elif key == 's':
                self.comand += 'd'
            elif key == 'q':
                self.comand += 'f'
            elif key == 'e':
                self.comand += 'b'
            elif key == 'g':
                self.comand += '-'
            elif key == 'h':
                self.comand = self.comand[:len(self.comand) - 1]
            self.upd_text_message()
            if key == 'f':
                # print('inswitch')
                # print(self.comand)
                self.switch_command_trigger()
            super().input(key)
        else:
            if key in 'mouse1' and self.action_trigger:  # проверка на взаимодействие с сенсорами
                for hitinfo in mouse.collisions:
                    collider_name = hitinfo.entity.name
                    if key == 'mouse1' and collider_name == 'RANDOM':
                        self.randomizing()
                        break
                    elif key == 'mouse1' and collider_name == 'LEFT':
                        self.trans_to('LEFT')
                    elif key == 'mouse1' and collider_name == 'FRONT':
                        self.trans_to_front()
                    elif key == 'mouse1' and collider_name == 'RIGHT':
                        self.trans_to('RIGHT')
                    elif key == 'mouse1' and collider_name == 'BACK':
                        self.trans_to('BACK')
                        break

            if key == 'd' and self.action_trigger:  # вращение в зависимсости от нажатия клавиш
                self.rotation('RIGHT')
            if key == 'a' and self.action_trigger:
                self.rotation('LEFT')
            if key == 'w' and self.action_trigger:
                self.rotation('TOP')
            if key == 's' and self.action_trigger:
                self.rotation('BOTTOM')
            if key == 'q' and self.action_trigger:
                self.rotation('FRONT')
            if key == 'e' and self.action_trigger:
                self.rotation('BACK')

            if key == 'r' and self.action_trigger:  # сообщение - теперь вы вводите команду
                # print('switch')
                self.comand = ''
                self.switch_command_trigger()

            if key == 'mouse2':  # смена направления вращения
                self.switch_mode()
            super().input(key)


if __name__ == '__main__':
    game = Game()
    game.run()
