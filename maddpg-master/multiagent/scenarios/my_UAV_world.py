import numpy as np
from multiagent.core_UAV import World, Agent, Landmark
from multiagent.scenario import BaseScenario
import copy
from matplotlib import pyplot as plt
import matplotlib.patches as mpathes

# hard constraints for dynamic and no-flying-zone


class Scenario(BaseScenario):
    def make_world(self):
        world = World()
        # set any world properties first
        world.dim_c = 2
        num_agents = 1
        self.num_district = np.int(18 / 6)
        self.num_landmarks_district = [np.int(np.random.uniform(8, 10)) for i in range(self.num_district)]
        self.num_landmarks = np.sum(self.num_landmarks_district) + 1
        world.observing_range = 5
        world.min_corridor = 0.15
        world.collaborative = True
        # add agents
        world.agents = [Agent() for _ in range(num_agents)]
        for i, agent in enumerate(world.agents):
            agent.name = 'agent %d' % i
            agent.type = 'UAV'
            agent.collide = True
            agent.silent = True
            agent.size = np.random.uniform(0.03, 0.07)
            agent.done = False
        # add landmarks
        world.landmarks = [Landmark() for _ in range(self.num_landmarks)]
        for i, landmark in enumerate(world.landmarks):
            landmark.name = 'landmark %d' % i
            landmark.collide = False
            landmark.movable = False
            if i == (len(world.landmarks) - 1):
                landmark.sizea = 0.1
                landmark.sizeb = 0.1
                landmark.direction = 0
        # make initial conditions
        self.reset_world(world)
        return world

    def reset_world(self, world):
        for i, landmark in enumerate(world.landmarks):
            landmark.name = 'landmark %d' % i
            landmark.collide = False
            landmark.movable = False
            if i == (len(world.landmarks) - 1):
                landmark.sizea = 0.1
                landmark.sizeb = 0.1
                landmark.direction = 0
        # random properties for agents
        for i, agent in enumerate(world.agents):
            agent.color = np.array([0.35, 0.35, 0.85])
            agent.size = np.random.uniform(0.03, 0.07)
        # random properties for landmarks
        for i, landmark in enumerate(world.landmarks):
            if i == len(world.landmarks) - 1:
                landmark.color = np.array([0.21, 0.105, 0.30])
            else:
                landmark.color = np.array([0.25, 0.25, 0.25])
        # set random initial states
        for agent in world.agents:
            # initialize x and y
            agent.state.p_pos = np.squeeze(np.array([np.random.uniform(-1, -0.9, 1), np.random.uniform(-0.1, +0.1, 1)]))
            agent.state.start = copy.deepcopy(agent.state.p_pos)
            # initialize v
            agent.state.p_vel = np.array([0.2])  # np.zeros(1)  # because the velocity is along the flying direction
            # initialize theta
            agent.state.theta = np.random.uniform(-np.pi/3, np.pi/3, 1)
            agent.state.omega = np.array([0.0])
            agent.state.c = np.zeros(world.dim_c)
            agent.done = False
        landmark = world.landmarks[-1]
        landmark.state.p_pos = np.squeeze(np.array([np.random.uniform(6, 18), np.random.uniform(-0.1, +0.1, 1)]))
        landmark.state.p_vel = np.zeros(world.dim_p)
        for num_d in range(self.num_district):
            done = 0
            while not done:
                fail = 0
                temp = np.int(np.sum(self.num_landmarks_district[0:num_d]))
                temp1 = np.int(np.sum(self.num_landmarks_district[0:num_d + 1]))
                for i, landmark in enumerate(world.landmarks[temp: temp1]):
                    if fail:
                        break
                    flag = 1  # to set landmarks separately
                    max_num = 0
                    while flag:
                        max_num = max_num + 1
                        if max_num > 10:
                            fail = 1
                            break
                        landmark.state.p_pos = np.squeeze(np.array([np.random.uniform(num_d * 6 + 0.5,
                                                                                      (num_d + 1) * 6 + 1.5, 1),
                                                                    np.random.uniform(-8, +8, 1)]))
                        landmark.sizea = np.random.uniform(0.90, 1.55)
                        landmark.sizeb = np.random.uniform(0.90, 1.55)
                        landmark.direction = np.random.uniform(0, 0)
                        temp1 = []
                        temp2 = []
                        temp1.append(np.sqrt(np.sum(np.square(world.agents[0].state.p_pos - landmark.state.p_pos))))
                        temp2.append(world.agents[0].size + landmark.size + world.min_corridor)
                        k = i + temp
                        temp3 = np.int(np.sum(self.num_landmarks_district[0:(num_d - 1 if num_d > 0 else 0)]))
                        for j in range(temp3, k + 1):
                            if j == k:
                                j_ = -1
                            else:
                                j_ = j
                            temp1.append(np.sqrt(np.sum(np.square(world.landmarks[j_].state.p_pos - landmark.state.p_pos))))
                            temp1_  = np.sqrt(np.sum(np.square(world.landmarks[j_].state.p_pos - landmark.state.p_pos)))
                            if j_ == -1:
                                temp2.append(world.landmarks[j_].sizea * 0.5 + world.landmarks[j_].sizeb * 0.5 +
                                             landmark.sizea * 0.5 + landmark.sizeb * 0.5 + world.min_corridor)
                                temp2_ = world.landmarks[j_].sizea * 0.5 + world.landmarks[j_].sizeb * 0.5 + \
                                         landmark.sizea * 0.5 + landmark.sizeb * 0.5 + world.min_corridor
                            else:
                                temp2.append(world.landmarks[j_].sizea * 0.5 + world.landmarks[j_].sizeb * 0.5 +
                                             landmark.sizea * 0.5 + landmark.sizeb * 0.5 + world.min_corridor)
                                temp2_ = world.landmarks[j_].sizea * 0.5 + world.landmarks[j_].sizeb * 0.5 + \
                                         landmark.sizea * 0.5 + landmark.sizeb * 0.5 + world.min_corridor
                            if temp1_ < temp2_:
                                break
                        if min(np.array(temp1) - np.array(temp2)) > 0:
                            flag = 0
                    landmark.state.p_vel = np.zeros(world.dim_p)
                if fail:
                    continue
                done = 1

    def benchmark_data(self, agent, world):
        rew = 0
        collisions = 0
        occupied_landmarks = 0
        min_dists = 0
        for l in world.landmarks:
            dists = [np.sqrt(np.sum(np.square(a.state.p_pos - l.state.p_pos))) for a in world.agents]
            min_dists += min(dists)
            rew -= min(dists)
            if min(dists) < 0.1:
                occupied_landmarks += 1
        if agent.collide:
            for a in world.agents:
                if self.is_collision(a, agent):
                    rew -= 1
                    collisions += 1
        return (rew, collisions, min_dists, occupied_landmarks)

    def is_collision(self, agent1, agent2):
        if isinstance(agent1, Agent) and isinstance(agent2, Agent):
            delta_pos = agent1.state.p_pos - agent2.state.p_pos
            dist = np.sqrt(np.sum(np.square(delta_pos)))
            dist_min = agent1.size + agent2.size
            return True if dist < dist_min else False
        elif isinstance(agent1, Agent) and isinstance(agent2, Landmark):
            theta = agent2.direction
            a = agent2.sizea + agent1.size
            b = agent2.sizeb + agent1.size
            x_ = (agent1.state.p_pos[0] - agent2.state.p_pos[0]) * np.cos(theta) + \
                 (agent1.state.p_pos[1] - agent2.state.p_pos[1]) * np.sin(theta)
            y_ = - (agent1.state.p_pos[0] - agent2.state.p_pos[0]) * np.sin(theta) + \
                 (agent1.state.p_pos[1] - agent2.state.p_pos[1]) * np.cos(theta)
            dist = x_ ** 2 / a ** 2 + y_ ** 2 / b ** 2
            return True if dist < 1 else False
        elif isinstance(agent1, Landmark) and isinstance(agent2, Agent):
            '''fig, ax0 = plt.subplots()
            landmark = agent1
            p_pos = landmark.state.p_pos
            theta = landmark.direction / np.pi * 180
            a = landmark.sizea
            b = landmark.sizeb
            ellipse = mpathes.Ellipse(p_pos, 2 * a, 2 * b, theta, facecolor='forestgreen')
            ax0.add_patch(ellipse)
            p_pos = np.array([agent2.state.p_pos[0], agent2.state.p_pos[1]])
            r = agent2.size
            circle = mpathes.Circle(p_pos, r, facecolor='darkgreen')
            ax0.add_patch(circle)
            ax0.set_xlim((-1, 10))
            ax0.set_ylim((-10, 10))
            ax0.axis('equal')
            ax0.set_title("x-y")
            x1 = [-1, 10]
            y1 = [10, 10]
            y2 = [-10, -10]
            ax0.plot(x1, y1, color='forestgreen', linestyle='-.')
            ax0.plot(x1, y2, color='forestgreen', linestyle='-.')
            plt.show()'''
            theta = agent1.direction
            a = agent1.sizea + agent2.size
            b = agent1.sizeb + agent2.size
            x_ = (agent2.state.p_pos[0] - agent1.state.p_pos[0]) * np.cos(theta) +\
                 (agent2.state.p_pos[1] - agent1.state.p_pos[1]) * np.sin(theta)
            y_ = - (agent2.state.p_pos[0] - agent1.state.p_pos[0]) * np.sin(theta) +\
                 (agent2.state.p_pos[1] - agent1.state.p_pos[1]) * np.cos(theta)
            dist = x_ ** 2 / a ** 2 + y_ ** 2 / b ** 2
            '''if dist < 1:
                print('aaa')
                fig, ax0 = plt.subplots()
                landmark = agent1
                p_pos = landmark.state.p_pos
                theta = landmark.direction / np.pi * 180
                a = landmark.sizea
                b = landmark.sizeb
                ellipse = mpathes.Ellipse(p_pos, 2 * a, 2 * b, theta, facecolor='forestgreen')
                ax0.add_patch(ellipse)
                p_pos = np.array([agent2.state.p_pos[0], agent2.state.p_pos[1]])
                r = agent2.size
                circle = mpathes.Circle(p_pos, r, facecolor='darkgreen')
                ax0.add_patch(circle)
                ax0.set_xlim((-1, 10))
                ax0.set_ylim((-10, 10))
                ax0.axis('equal')
                ax0.set_title("x-y")
                x1 = [-1, 10]
                y1 = [10, 10]
                y2 = [-10, -10]
                ax0.plot(x1, y1, color='forestgreen', linestyle='-.')
                ax0.plot(x1, y2, color='forestgreen', linestyle='-.')
                plt.show()'''
            return True if dist < 1 else False
        else:
            pass

    def reward(self, agent, world, dist_last, action):
        # Agents are rewarded based on minimum agent distance to each landmark, penalized for collisions
        l = world.landmarks[-1]
        dist = np.sqrt(np.sum(np.square(agent.state.p_pos - l.state.p_pos)))
        diff_dist = dist_last - dist
        # rew = -dist
        rew = -10 * (agent.state.p_vel - diff_dist)
        # rew -= agent.state.p_pos[1]
        # collision punishment
        if agent.collide:
            for a in world.landmarks[0:-1]:
                if self.is_collision(a, agent):
                    rew -= 7
        rew -= agent.action.u[1] * 20
        rew /= world.landmarks[-1].state.p_pos[0]
        return rew

    def observation(self, agent, world):
        # get positions of all entities in this agent's reference frame
        entity_pos_temp = []
        # min_observable_landmark = np.min([5, len(world.landmarks)])
        min_observable_landmark = 5
        for entity in world.landmarks:  # world.entities:
            distance = np.sqrt(np.sum(np.square([entity.state.p_pos - agent.state.p_pos])))
            if distance < world.observing_range and (not entity == world.landmarks[-1]):
                entity_pos_temp.append([np.append(entity.state.p_pos - agent.state.p_pos, [entity.sizea, entity.sizeb,
                                                  entity.direction]), distance])
        entity_pos_temp.sort(key=lambda pos: pos[1])
        entity_pos_temp = entity_pos_temp[0:min_observable_landmark]
        entity_pos = [entity_pos_temp[i][0] for i in range(len(entity_pos_temp))]  # position
        for i in range(len(entity_pos_temp), min_observable_landmark):
            entity_pos.append([-1, -1, -1, -1, -1])

        # target obs
        target = world.landmarks[-1]
        vector = (target.state.p_pos - agent.state.p_pos)/np.sqrt(np.sum(np.square(target.state.p_pos - agent.state.p_pos)))
        dis1 = np.sqrt(np.sum(np.square(agent.state.p_pos - world.landmarks[-1].state.p_pos)))
        dis2 = np.sqrt(np.sum(np.square(agent.state.start - world.landmarks[-1].state.p_pos)))
        if np.sqrt(np.sum(np.square(target.state.p_pos - agent.state.p_pos))) > 0:
            entity_pos.append(np.append(np.array([1, 0]), dis1/dis2))
        else:
            entity_pos.append(np.append(np.array([agent.state.p_pos[1], 0]), dis1/dis2))

        temp = np.concatenate([np.array([agent.size])] + [agent.state.p_vel] + [agent.state.p_pos] +
                              [agent.state.theta] + [agent.state.omega] + entity_pos + [vector])
        return temp

    def done(self, agent, world):
        target_landmark = world.landmarks[-1]
        dis = np.sqrt(np.sum(np.square(agent.state.p_pos - target_landmark.state.p_pos)))
        if dis <= agent.size + target_landmark.sizea + 0.10:  # should be 0.05
            return True
        return False

    def constraints_value(self, agent, world):
        constraints = []
        for i, landmark in enumerate(world.landmarks[0:-1]):
            constraints.append((-np.sum(np.square(agent.state.p_pos - landmark.state.p_pos)) +
                               np.square(landmark.size + agent.size - 0.01)) * 10)
        return constraints

    def is_any_collision(self, agent, world):
        for i, landmark in enumerate(world.landmarks[0:-1]):
            agent1 = landmark
            agent2 = agent
            theta = agent1.direction
            a = agent1.sizea + agent2.size - 0.09
            b = agent1.sizeb + agent2.size - 0.09
            x_ = (agent2.state.p_pos[0] - agent1.state.p_pos[0]) * np.cos(theta) + \
                 (agent2.state.p_pos[1] - agent1.state.p_pos[1]) * np.sin(theta)
            y_ = - (agent2.state.p_pos[0] - agent1.state.p_pos[0]) * np.sin(theta) + \
                 (agent2.state.p_pos[1] - agent1.state.p_pos[1]) * np.cos(theta)
            dist = x_ ** 2 / a ** 2 + y_ ** 2 / b ** 2
            if dist <= 1:
                return True
        return False


