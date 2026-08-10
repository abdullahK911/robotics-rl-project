import robosuite as suite
from robosuite.wrappers import GymWrapper
from stable_baselines3 import PPO

env = suite.make(
    env_name="Lift",
    robots="Panda",
    has_renderer=True,
    has_offscreen_renderer=False,
    use_camera_obs=False,
    reward_shaping=True,
    control_freq=20,
)
env = GymWrapper(env)

policy = PPO.load("ppo_lift_panda")   # renamed from "model" to avoid mjpython/MuJoCo name collision

obs, _ = env.reset()
for _ in range(500):
    action, _ = policy.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    env.render()
    if terminated or truncated:
        obs, _ = env.reset()