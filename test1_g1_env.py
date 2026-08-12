from g1_locomotion_env import G1LocomotionEnv

env = G1LocomotionEnv()
obs, _ = env.reset()
print("Observation shape:", obs.shape)
print("Action space:", env.action_space)

for i in range(300):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"Step {i}: reward={reward:.4f}, terminated={terminated}, pelvis_height={env._get_pelvis_height():.3f}")
    if terminated or truncated:
        break