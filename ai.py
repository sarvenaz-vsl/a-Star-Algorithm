import random
from collections import deque
import json
from modeled_env import ModeledEnv, set_constants
from time import time
import heapq

class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=False, mode='bfs'):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        self.predicted_actions = []
        self.actions_list = ['up', 'right', 'down', 'left']

        self.optimized = optimized
        self.alg = eval('self.' + mode)
        print('running ' + mode)

    def act(self):
        sensor_data = self.perceive_func(self)
        if self.optimized:
            set_constants(json.loads(sensor_data['Current_Env'])['state'])
            sensor_data['Current_Env'] = ModeledEnv()
        else:
            from env import Env
            sensor_data['Current_Env'] = Env([1], [1]).from_json(
                **json.loads(sensor_data['Current_Env'])['state'])

        if self.predicted_actions == []:
            t0 = time()
            self.predicted_actions = self.alg(sensor_data['Current_Env'])
            print(time()-t0)

        action = self.predicted_actions.pop()

        return action

    def bfs(self, root_game):
        q = []
        q.append([root_game, []])

        while q:
            # pop first element from queue
            node = q.pop(0)

            if random.random() < 0.2:
                random.shuffle(self.actions_list)
            for action in self.actions_list:
                # add children to queue
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])
                # goal test
                if child_game.goal_test():
                    return [action] + node[1]

    def ucs(self, root_game):
        x = 0
        states_queue = [(0, x, root_game,[])]

        while states_queue:
            new_action = heapq.heappop(states_queue)
            for action in self.actions_list:
                child_game = new_action[2].create_copy()
                if 'has died' not in child_game.take_action(action, self.my_id):
                    cost = child_game.state.agent_list[0].realCost + self.heuristic(child_game.state)
                    x -= cost
                    heapq.heappush(states_queue, (cost, x, child_game, [action] + new_action[3]))
                if child_game.goal_test():
                    return [action] + new_action[3]

    def heuristic(self, state):
        h = state.winScore - state.get_team_score(self.my_id)
        return h

    def a_star(self, root_game):
        x = 0
        states_queue = [(0, x, root_game,[])]

        while states_queue:
            new_action = heapq.heappop(states_queue)            
            for action in self.actions_list:
                child_game = new_action[2].create_copy()
                if 'has died' not in child_game.take_action(action, self.my_id):
                    cost = child_game.state.agent_list[0].realCost + self.heuristic(child_game.state)
                    x -= cost
                    heapq.heappush(states_queue, (cost, x, child_game, [action] + new_action[3]))
                if child_game.goal_test():
                    return [action] + new_action[3]


