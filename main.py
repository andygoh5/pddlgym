import gym
import random
from pathlib import Path
import imageio
import random
import pddlgym

def get_adjacent_location(s, num_rows, num_cols):
    if s[0] > 1:
        loc = (s[0] - 1, s[1])
        yield (loc, "dir-left")
    if s[1] > 1:
        loc = (s[0], s[1] - 1)
        yield (loc, "dir-up")
    if s[0] < num_cols:
        loc = (s[0] + 1, s[1])
        yield (loc, "dir-right")
    if s[1] < num_rows:
        loc = (s[0], s[1] + 1)
        yield (loc, "dir-down")

# TODO: clean up this function to automatically generate pddl problem file
def generate_problem_file(num_rows, num_cols, agent_loc_initial, stove, board, counters):
    f = open("pddlgym/pddl/kitchen/problem0.pddl", "w")

    # initializing the four directions and the current "things" (includes agents and objects)
    f.write('''(define (problem kitchen-01) (:domain kitchen)
    (:objects
        dir-down - direction
        dir-left - direction
        dir-right - direction
        dir-up - direction
        player-01 - thing
        lettuce-01 - thing
        tomato-01 - thing
    ''')

    # places down the counters in the map
    counter_predicates = ""
    for i in range(len(counters)):
        loc = counters[i]
        counter_predicates += f"(is-counter pos-{loc[0]}-{loc[1]})\n"

    locations = ""      # mark each coordinate as a location 
    adjacents = ""      # mark which pair of coordinates is adjacent
    directions = ""     # for each adjacent pair, mark the direction from a to b
    clears = ""         # mark which coordinates are clear for the agent to move to

    filled_squares = counters + [agent_loc_initial] + [stove] + [board]
    for i in range(1, num_cols + 1):
        for j in range(1, num_rows + 1):
            locations += f"pos-{i}-{j} - location\n"
            for ((ad_i, ad_j), dir) in get_adjacent_location((i,j),num_rows,num_cols):
                adjacents += f"(adjacent pos-{i}-{j} pos-{ad_i}-{ad_j})\n"
                directions += f"(move-dir pos-{i}-{j} pos-{ad_i}-{ad_j} {dir})\n"
            if (i,j) not in filled_squares:
                clears += f"(clear pos-{i}-{j})\n"
    f.write(locations + ")\n")

    f.write("""
    (:goal (and
        (cooked tomato-01)
        (cooked lettuce-01)))
    """)

    # initialize the four movement actions, set the agent as handsfree, and mark the agent
    # as an agent, and the objects as objects (instead of just "things")
    f.write("""
    (:init
        (move dir-down)
        (move dir-left)
        (move dir-right)
        (move dir-up)
        (handsfree player-01)
        (is-agent player-01)
        (is-object tomato-01)
        (is-object lettuce-01)
    """)

    # initialize agent, stove, board locations
    # note that the agent uses the (at agent loc) predicate because it is mutable,
    # while the stove and board use the (is-stove loc) format  as they are immutable
    f.write(f"(at player-01 pos-{agent_loc_initial[0]}-{agent_loc_initial[1]})\n")
    f.write(f"(is-stove pos-{stove[0]}-{stove[1]})\n")
    f.write(f"(is-board pos-{board[0]}-{board[1]})\n")

    # choose a random counter to put the objects (tomato and lettuce for now)
    object_locations = random.sample(range(0, len(counters)), 2)
    f.write(f"(at lettuce-01 pos-{counters[object_locations[0]][0]}-{counters[object_locations[0]][1]})\n")
    f.write(f"(at tomato-01 pos-{counters[object_locations[1]][0]}-{counters[object_locations[1]][1]})\n")

    f.write(counter_predicates)
    f.write(adjacents)
    f.write(clears)
    f.write(directions)
    f.write("))")
    f.close()
    return None


def run(env_name, verbose, render):
    env = pddlgym.make(env_name, raise_error_on_invalid_action = True)
    obs, _ = env.reset()

    # a policy is a function that takes the state (i.e., observation) and returns an action
    # TODO: connect this policy function to the planner instead of just random sampling
    policy = lambda s : env.action_space.sample(s)

    images = []

    valid_actions = 0
    while valid_actions < 20:    
        action = policy(obs)

        # if an action is invalid (e.g,, try to pick up an object that the agent is not next to), the
        # env.step() function will throw an exception. In that case, just resample for a different action
        try:
            obs, reward, done, _ = env.step(action)
        except:
            continue
        
        valid_actions += 1
        
        if verbose:
            print(f'Action {valid_actions} observation: {obs}')
        if render:
            images.append(env.render())

        print(f"-- Action {valid_actions}: {action}")

        if done:
            break

    # output the render into a video
    if render:
        cur_dir = Path().absolute().parent.absolute()
        video_path = str(cur_dir) + "/demos/{}_random_demo.mp4".format(env_name)
        images.append(env.render())
        imageio.mimwrite(video_path, images, fps=2)
        print("Wrote out video to", video_path)

if __name__ == "__main__":
    """
    The grid layout for this environment is
    (1,1)           (2,1)           ...    (1, NUM_COLS)
    (1,2)           (2,2)           ...    (2, NUM_COLS)
    ...
    (NUM_ROWS, 1),  (NUM_ROWS, 2)   ...    (NUM_ROWS, NUM_COLS)
    """
    generate_problem_file(num_rows = 5,
                         num_cols = 5,
                         agent_loc_initial = (2,5),
                         stove = (1,1),
                         board = (1,5),
                         counters = [(1,3),(2,3),(3,3),(4,3)])
    env_name = "PDDLEnvKitchen-v0"

    # verbose will output the observation state along with the action
    # render will output the demo video to pddlgym/demos/
    run(env_name, verbose=False, render=True)