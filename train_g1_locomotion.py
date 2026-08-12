from g1_locomotion_env import G1LocomotionEnv
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

env = G1LocomotionEnv()
env = Monitor(env)

policy = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./runs_g1_locomotion/")
policy.learn(total_timesteps=500_000)

policy.save("ppo_g1_locomotion_v1")
print("Training complete. Model saved as ppo_g1_locomotion_v1.zip")