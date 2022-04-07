import random
from functools import lru_cache


def set_constants(c_json):
    global constant_dict
    constant_dict = c_json


class ModeledEnv:
    def __init__(self, copy=False):
        if not copy:
            self.state = ModeledState()

    def take_action(self, action, agent):
        return self.state.update(action, agent)

    def goal_test(self):
        for agent_idx in range(len(self.state.agent_list)):
            if self.state.get_team_score(agent_idx) >= self.state.winScore:
                return True
        return False

    def create_copy(self):
        _copy = type(self)(copy=True)
        _copy.state = self.state.create_copy()
        return _copy


class ModeledState:
    def __init__(self, copy=False):
        if not copy:
            # vv
            pass

    @lru_cache
    def __getattr__(self, item):
        global constant_dict
        return constant_dict[item]


class ModeledSnake:
    def __init__(self, snake_idx, copy=False):
        self.snake_idx = snake_idx
        if not copy:
            # vv
            pass

    @lru_cache
    def __getattr__(self, item):
        global constant_dict
        return constant_dict['agent_list'][self.snake_idx][item]
