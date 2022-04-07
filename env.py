import random
from copy import deepcopy
import json


class Env:
    def __init__(self, foodGrid, chance_map, **kwargs):
        if type(foodGrid) is State: self.state=foodGrid
        else: self.state = State(foodGrid, chance_map, **kwargs)

    def from_json(self, **kwargs):
        self.state.from_json(**kwargs)
        return self

    def add_agent(self, agent_class, spawn_point=None, **kwargs):
        ok = False
        if spawn_point is not None:
            i, j = spawn_point
            for other_snake in self.state.agent_list:
                if [i, j] in other_snake.body:
                    raise "agent spawn location is being used by another agent"
            ok = True

        while not ok:
            ok=True
            i = random.randint(0, len(self.state.foodGrid)-1)
            j = random.randint(0, len(self.state.foodGrid[0])-1)
            for other_snake in self.state.agent_list:
                if [i,j] in other_snake.body: ok = False

        self.state.agent_list.append(
            Snake(agent_class(self.perceive, len(self.state.agent_list), **kwargs), [i,j], env=self.state)
        )

        self.state.eat(len(self.state.agent_list)-1)

        return self.state.agent_list[-1].agent_type

    def take_action(self, action, agent):
        return self.state.update(action, agent)

    def perceive(self, agent):
        agent_data = self.state.agent_list[self.state.get_agent_index(agent)]
        return {
            "Current_Env": json.dumps(self, default=lambda o: o.__dict__, indent=4),
            "map": self.state.foodGrid,
            "chance map": self.state.chance_map,
            "agent body": agent_data.body,
            "score": agent_data.foodScore,
            "cost": agent_data.realCost,
            }

    def goal_test(self):
        for agent_idx in range(len(self.state.agent_list)):
            if self.state.get_team_score(agent_idx) >= self.state.winScore: return True
        return False

    def create_copy(self):
        return deepcopy(self)

    def __eq__(self, obj):
        return isinstance(obj, Env) and \
               obj.state == self.state

    def __deepcopy__(self, memo):
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(deepcopy(self.state, memo), None)
        return _copy


class State:
    def __init__(self, foodGrid, chance_map, consume_tile=False, turningCost=0,
                 foodAddScore=1, foodScoreMulti=2, winScore=30):
        self.consume_tile, self.winScore = consume_tile, winScore
        self.foodScoreMulti, self.foodAddScore, self.turningCost = foodScoreMulti, foodAddScore, turningCost
        self.foodGrid = foodGrid if foodGrid is not None else None
        self.chance_map = chance_map if chance_map is not None else None
        self.agent_list=[]

    def from_json(self, consume_tile, winScore, foodScoreMulti, foodAddScore,
                 turningCost, foodGrid, chance_map, agent_list):
        self.consume_tile, self.winScore = consume_tile, winScore
        self.foodScoreMulti, self.foodAddScore, self.turningCost = foodScoreMulti, foodAddScore, turningCost
        self.foodGrid = foodGrid
        self.chance_map = chance_map
        self.agent_list = [Snake(None,None,'','').from_json(**snake_json) for snake_json in agent_list]
        return self

    def get_agent_index(self, agent):
        agent_idxs = [idx for idx, ad in enumerate(self.agent_list) if ad.agent_type == agent]
        if len(agent_idxs) == 0: print("agent not found"); return None
        else: return agent_idxs[0]

    def update(self, action, agent):
        agent_idx = agent if type(agent) is int else self.get_agent_index(agent)
        if agent_idx is None: return "invalid agent"
        if not self.validate_action(action): return "invalid action"
        snake = self.agent_list[agent_idx]

        if snake.body==[]: return snake.name+' has died'

        # move snake
        snake.move(action.lower())

        # check if impacted
        impact=self.check_for_impact(agent_idx)
        if impact == 'exited map' or impact == 'hit its own body':
            snake.body=[]
            return snake.name+' has died'
        elif impact is not False: snake.foodScore -= 1

        # eat
        self.eat(agent_idx)

        # turning cost
        if snake.currentDir != action: snake.foodScore = max(snake.foodScore-self.turningCost, 0)
        snake.currentDir = action

        return "success"

    def validate_action(self, action):
        if type(action) is not str or action.lower() not in ["up", "down", "right", "left"]:
            print("the action '%s' is invalid" % action)
            return False
        return True

    def check_for_impact(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]
        if not (0 <= snake_head[0] <= len(self.foodGrid) - 1 and 0 <= snake_head[1] <= len(self.foodGrid[0]) - 1):
            return 'exited map'
        for part in snake.body[:-1]:
            if snake_head == part: return 'hit its own body'

        for other_snake in self.agent_list:
            for part in other_snake.body:
                if snake is other_snake: continue
                if snake_head == part: return "hit '%s' body" % other_snake.name
        return False

    def eat(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]

        if random.random() > self.chance_map[snake_head[0]][snake_head[1]]: return "nothing happened (stochastic)"

        tile=self.foodGrid[snake_head[0]][snake_head[1]]
        if len(snake.body) == 1 and snake.shekam == 0 and tile!=0:
            snake.foodScore += self.foodAddScore + self.foodScoreMulti * tile
            snake.shekam += tile

            if self.consume_tile:
                self.foodGrid[snake_head[0]][snake_head[1]] = \
                    round(tile * random.uniform(0.1, 0.9))

    def get_team_score(self, agent_idx):
        snake = self.agent_list[agent_idx]
        score = 0
        for other_snake in self.agent_list:
            if other_snake.team == snake.team: score += other_snake.foodScore
        return score

    def __eq__(self, obj):
        return isinstance(obj, State) and \
            obj.agent_list == self.agent_list and \
            obj.foodGrid == self.foodGrid and \
            obj.chance_map == self.chance_map and \
            obj.foodAddScore == self.foodAddScore and \
            obj.winScore == self.winScore and \
            obj.turningCost == self.turningCost and \
            obj.consume_tile == self.consume_tile and \
            obj.foodScoreMulti == self.foodScoreMulti

    def __deepcopy__(self, memo):
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(None, None)

            _copy.agent_list = []
            for snake in self.agent_list: _copy.agent_list.append(deepcopy(snake, memo))

            _copy.foodGrid = self.foodGrid
            _copy.chance_map = self.chance_map
            _copy.foodAddScore = self.foodAddScore
            _copy.winScore = self.winScore
            _copy.turningCost = self.turningCost
            _copy.consume_tile = self.consume_tile
            _copy.foodScoreMulti = self.foodScoreMulti

            memo[id_self] = _copy
        return _copy


class Snake:
    def __init__(self, agent_type, head_pos, name=None, team=None, env=None):
        self.name = name if name is not None else "agent "+str(len(env.agent_list))
        self.team = team if team is not None else str(len(env.agent_list))

        self.agent_type = agent_type
        self.shekam = 0
        self.foodScore = 0
        self.realCost = 0
        self.currentDir=None

        self.body = [head_pos]

    def from_json(self, name, team, agent_type, shekam, foodScore, realCost, currentDir, body):
        self.name = name
        self.team = team
        self.agent_type = agent_type
        self.shekam = shekam
        self.foodScore = foodScore
        self.realCost = realCost
        self.currentDir=currentDir
        self.body = body
        return self

    def move(self, action):
        delta_i, delta_j = {"up": (-1,0), "down": (+1,0), "right": (0,+1), "left": (0,-1)}[action]
        self.body.append([self.body[-1][0]+delta_i, self.body[-1][1]+delta_j])

        if self.shekam == 0:
            del self.body[0]
            if len(self.body) != 1: del self.body[0]
        else: self.shekam -= 1

        self.realCost += 1

    def __eq__(self, obj):
        return isinstance(obj, Snake) and \
               obj.name == self.name and \
               obj.team == self.team and \
               obj.shekam == self.shekam and \
               obj.body == self.body and \
               obj.foodScore == self.foodScore and \
               obj.realCost == self.realCost and \
               obj.snake_type == self.agent_type and \
               obj.currentDir == self.currentDir

    def __deepcopy__(self, memo):
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(None, list(self.body[-1]), name=self.name, team=self.team)

            _copy.body = [list(part) for part in self.body]
            _copy.name = self.name
            _copy.team = self.team
            _copy.shekam = self.shekam
            _copy.foodScore = self.foodScore
            _copy.realCost = self.realCost
            _copy.currentDir = self.currentDir

            memo[id_self] = _copy
        return _copy

