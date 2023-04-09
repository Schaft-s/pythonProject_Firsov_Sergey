from ursina import *


class Game(Ursina):
    def __init__(self):
        super().__init__()
        # window.fullscreen = True
        Entity(model='sphere', scale=400, texture='sky_sunset', double_sided=True)  # задаёт внешнюю сферу
        Entity(model='quad', scale=50, texture='white_cube', texture_scale=(50, 50), rotation_x=90, y=-5,
               color=color.light_gray)  # задаёт плоскость, важна для наглядности
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
        self.CUBES = [Entity(model='models/custom_cube', texture='textures/rubik_texture', position=pos) for pos
                      in self.SIDE_POSITIONS]  # создание самих кубиков

        self.trans_to_front()   # задание отсчёта для поворотов

        self.animation_time = 0.3

        self.action_trigger = True  # для отсутствия наложения действий друг на друга
        self.mode_of_spin = False  # для смены направления вращения сторон

        self.message = Text(origin=(-0.5, 19), color=color.black)  # подсказка для смены направления вращения
        self.switch_mode()
        Text.default_resolution = 1080 * Text.size

        alfa = dedent('''
              To rotate side -> push\n
              Right          ->     d
              Left            ->     a
              Upp           ->     w
              Down        ->     s
              Front         ->     q
              Bottom     ->     s''').strip()
        self.instuction = Text(text=alfa, x=0.6, y=0.4, color=color.black)  # подсказка клавиш для поворотов

        self.create_sensors()  # создание точек для смены стороны вращения

    def randomizing(self, k=50):  # случайное перемешивание кубика
        [self.rand_func(random.choice(list(self.rotation_axes_all_cube))) for i in range(k)]

    def rand_func(self, side_name):
        rotation_axis = self.rotation_axes_all_cube[side_name]
        cube_positions = self.cubes_side_positons[side_name]

        self.reparent_to_scene()
        for cube in self.CUBES:
            if cube.position in cube_positions:
                cube.parent = self.PARENT
                exec(f'self.PARENT.rotation_{rotation_axis[1]} = 90')

    def create_sensors(self): # создание сенсоров для смены стороны вращения + перемешивание

        create_sensor = lambda name, pos, scale, texture: Entity(name=name, position=pos, model='sphere', texture=texture,
                                                                 scale=scale, collider='box')
        self.random_st_sensor = create_sensor(name='LEFT', pos=(-6, -2, 0), scale=(0.5, 0.5, 0.5),
                                              texture='textures/blue')
        self.random_st_sensor = create_sensor(name='FRONT', pos=(0, -2, -6), scale=(0.5, 0.5, 0.5),
                                              texture='textures/red')
        self.random_st_sensor = create_sensor(name='RIGHT', pos=(6, -2, 0), scale=(0.5, 0.5, 0.5),
                                              texture='textures/green')
        self.random_st_sensor = create_sensor(name='BACK', pos=(0, -2, 6), scale=(0.5, 0.5, 0.5),
                                              texture='textures/orange')

        self.random_st_sensor = Entity(name='RANDOM', position=(0, -4.99, 0), rotation_x=90, model='quad',
                                       texture='textures/random',
                                       scale=(1, 1), collider='box')

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

    def trans_to_left(self):  # смена центра вращения
        self.rotation_axes_all_cube = {'LEFT': '0z', 'RIGHT': '1z', 'TOP': '1y', 'BOTTOM': '0y', 'FRONT': '0x',
                                       'BACK': '1x'}
        self.cubes_side_positons = {'BACK': self.RIGHT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.FRONT, 'FRONT': self.LEFT,
                                    'LEFT': self.BACK, 'TOP': self.TOP}

    def trans_to_right(self):  # смена центра вращения
        self.rotation_axes_all_cube = {'LEFT': '1z', 'RIGHT': '0z', 'TOP': '1y', 'BOTTOM': '0y', 'FRONT': '1x',
                                       'BACK': '0x'}
        self.cubes_side_positons = {'LEFT': self.FRONT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.BACK, 'FRONT': self.RIGHT,
                                    'BACK': self.LEFT, 'TOP': self.TOP}

    def trans_to_front(self):  # смена центра вращения
        self.rotation_axes_all_cube = {'LEFT': '0x', 'RIGHT': '1x', 'TOP': '1y', 'BOTTOM': '0y', 'FRONT': '1z',
                                       'BACK': '0z'}
        self.cubes_side_positons = {'LEFT': self.LEFT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.RIGHT, 'FRONT': self.FRONT,
                                    'BACK': self.BACK, 'TOP': self.TOP}

    def trans_to_back(self):  # смена центра вращения
        self.rotation_axes_all_cube = {'LEFT': '1x', 'RIGHT': '0x', 'TOP': '1y', 'BOTTOM': '0y', 'FRONT': '0z',
                                       'BACK': '1z'}
        self.cubes_side_positons = {'BACK': self.FRONT, 'BOTTOM': self.BOTTOM, 'RIGHT': self.LEFT, 'FRONT': self.BACK,
                                    'LEFT': self.RIGHT, 'TOP': self.TOP}

    def reparent_to_scene(self):  # привязка к мировой сцене для поворотов
        for cube in self.CUBES:
            if cube.parent == self.PARENT:
                world_pos = round(cube.world_position, 1)
                world_rot = cube.world_rotation
                cube.parent = scene
                cube.position = world_pos
                cube.rotation = world_rot
        self.PARENT.rotation = 0

    def input(self, key, is_raw=False):
        if key in 'mouse1' and self.action_trigger:  # проверка на взаимодействие с сенсорами
            for hitinfo in mouse.collisions:
                collider_name = hitinfo.entity.name
                if key == 'mouse1' and collider_name == 'RANDOM':
                    self.randomizing()
                    break
                elif key == 'mouse1' and collider_name == 'LEFT':
                    self.trans_to_left()
                elif key == 'mouse1' and collider_name == 'FRONT':
                    self.trans_to_front()
                elif key == 'mouse1' and collider_name == 'RIGHT':
                    self.trans_to_right()
                elif key == 'mouse1' and collider_name == 'BACK':
                    self.trans_to_back()
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

        if key == 'mouse2':  # смена направления вращения
            self.switch_mode()
        super().input(key)


if __name__ == '__main__':
    game = Game()
    game.run()
