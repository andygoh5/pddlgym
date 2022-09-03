"""Gym environment registration"""

from . import tests

import matplotlib
# matplotlib.use("Agg")
from pddlgym.rendering import *
from gym.envs.registration import register
import gym

import os

# Save users from having to separately import gym
def make(*args, **kwargs):
    # env checker fails since obs is not an numpy array like object
    return gym.make(*args, disable_env_checker=True, **kwargs)

def register_pddl_env(name, is_test_env, other_args):
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pddl")
    domain_file = os.path.join(dir_path, "{}.pddl".format(name.lower()))
    gym_name = name.capitalize()
    problem_dirname = name.lower()
    if is_test_env:
        gym_name += 'Test'
        problem_dirname += '_test'
    problem_dir = os.path.join(dir_path, problem_dirname)

    register(
        id='PDDLEnv{}-v0'.format(gym_name),
        entry_point='pddlgym.core:PDDLEnv',
        kwargs=dict({'domain_file' : domain_file, 'problem_dir' : problem_dir,
                     **other_args}),
    )

# list of pddl environments we want to register as OpenAI Gym environments
for env_name, kwargs in [
        ("kitchen", {'render' : kitchen_render})
]:
    other_args = {
        "raise_error_on_invalid_action": False,
    }
    kwargs.update(other_args)
    for is_test in [False, True]:
        register_pddl_env(env_name, is_test, kwargs)

# Ignore certain files for pdoc documentation generation.
__pdoc__ = {'downward_translate': False, 'procedural_generation': False}

