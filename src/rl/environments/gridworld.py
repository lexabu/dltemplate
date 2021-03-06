import itertools
import matplotlib.pyplot as plt
import numpy as np
from scipy.misc import imresize


class GameObj(object):

    def __init__(self, coords, size, intensity, channel, reward, name):
        self.x = coords[0]
        self.y = coords[1]
        self.size = size
        self.intensity = intensity
        self.channel = channel
        self.reward = reward
        self.name = name


class GameEnvironment(object):
    """
    In the environment the agent controls a blue square, and the goal is to navigate
    to the green squares (reward +1) while avoiding the red squares (reward -1). At
    the start of each episode all squares are randomly placed within a 5x5 grid-world.
    The agent has 50 steps to achieve as large a reward as possible. Because they are
    randomly positioned, the agent needs to do more than simply learn a fixed path,
    as is the case in the FrozenLake environment. Instead the agent must learn a
    notion of spatial relationships between the blocks.

    The game environment outputs 84x84x3 color images, and uses function calls as
    similar to the OpenAI gym as possible. In doing so, it should be easy to modify
    this code to work on any of the OpenAI Atari games.
    """

    def __init__(self, partial, size):
        """
        Initializing the game environment with True limits the field of view,
        resulting in a partially observable MDP. Initializing it with False
        provides the agent with the entire environment, resulting in a fully
        observable MDP.

        :param partial:
        :param size:
        """
        self.size_x = size
        self.size_y = size
        self.actions = 4
        self.objects = []
        self.partial = partial
        self.state = None
        a = self.reset()
        plt.imshow(a, interpolation='nearest')

    def reset(self):
        self.objects = []
        hero = GameObj(self.new_position(), 1, 1, 2, None, 'hero')
        self.objects.append(hero)
        bug = GameObj(self.new_position(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug)
        hole = GameObj(self.new_position(), 1, 1, 0, -1, 'fire')
        self.objects.append(hole)
        bug2 = GameObj(self.new_position(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug2)
        hole2 = GameObj(self.new_position(), 1, 1, 0, -1, 'fire')
        self.objects.append(hole2)
        bug3 = GameObj(self.new_position(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug3)
        bug4 = GameObj(self.new_position(), 1, 1, 1, 1, 'goal')
        self.objects.append(bug4)
        state = self.render()
        self.state = state
        return state

    def move(self, direction):
        # 0 - up, 1 - down, 2 - left, 3 - right
        hero = self.objects[0]
        hero_x = hero.x
        hero_y = hero.y
        penalize = 0.

        if direction == 0 and hero.y >= 1:
            hero.y -= 1

        elif direction == 1 and hero.y <= self.size_y - 2:
            hero.y += 1

        elif direction == 2 and hero.x >= 1:
            hero.x -= 1

        elif direction == 3 and hero.x <= self.size_x - 2:
            hero.x += 1

        if hero.x == hero_x and hero.y == hero_y:
            penalize = 0.

        self.objects[0] = hero

        return penalize

    def new_position(self):
        iterables = [range(self.size_x), range(self.size_y)]
        points = []
        for t in itertools.product(*iterables):
            points.append(t)

        current_positions = []
        for obj in self.objects:
            if (obj.x, obj.y) not in current_positions:
                current_positions.append((obj.x, obj.y))

        for pos in current_positions:
            points.remove(pos)

        location = np.random.choice(range(len(points)), replace=False)

        return points[location]

    def check_goal(self):
        others = []
        hero = None
        for obj in self.objects:
            if obj.name == 'hero':
                hero = obj
            else:
                others.append(obj)

        for other in others:
            if hero.x == other.x and hero.y == other.y:
                self.objects.remove(other)
                if other.reward == 1:
                    self.objects.append(GameObj(self.new_position(), 1, 1, 1, 1, 'goal'))
                else:
                    self.objects.append(GameObj(self.new_position(), 1, 1, 0, -1, 'fire'))

                return other.reward, False

        return 0., False

    def render(self):
        a = np.ones([self.size_y + 2, self.size_x + 2, 3])
        a[1:-1, 1:-1, :] = 0
        hero = None
        for obj in self.objects:
            a[obj.y + 1:obj.y + obj.size + 1, obj.x + 1:obj.x + obj.size + 1, obj.channel] = obj.intensity
            if obj.name == 'hero':
                hero = obj

        if self.partial:
            a = a[hero.y:hero.y + 3, hero.x:hero.x + 3]

        b = imresize(a[:, :, 0], [84, 84, 1], interp='nearest')
        c = imresize(a[:, :, 1], [84, 84, 1], interp='nearest')
        d = imresize(a[:, :, 2], [84, 84, 1], interp='nearest')
        a = np.stack([b, c, d], axis=2)

        return a

    def step(self, action):
        penalty = self.move(action)
        reward, done = self.check_goal()
        state = self.render()
        # if not reward:
        #     print('done:', done)
        #     print('reward:', reward)
        #     print('penalty:', penalty)

        return state, reward + penalty, done
