import numpy as np
import mujoco
import gymnasium as gym
from gymnasium import spaces

class G1LocomotionEnv(gym.Env):
    def __init__(self, xml_path="unitree_mujoco/unitree_robots/g1/g1_23dof.xml"):
        super().__init__()
        self.model = mujoco.MjModel.from_xml_path(xml_path)
        self.data = mujoco.MjData(self.model)

        self.fall_height_threshold = 0.5
        self.max_episode_steps = 1000
        self.current_step = 0

        # Action space: torques for all actuated joints (excluding the free-floating base)
        self.n_actuators = self.model.nu
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(self.n_actuators,), dtype=np.float32
        )

        # Observation space: joint positions + velocities + pelvis height/orientation
        obs_dim = self.model.nq + self.model.nv
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

    def _get_obs(self):
        return np.concatenate([self.data.qpos, self.data.qvel]).astype(np.float32)

    def _get_pelvis_height(self):
        pelvis_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "pelvis")
        return self.data.xpos[pelvis_id][2]

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        mujoco.mj_forward(self.model, self.data)
        self.current_step = 0
        return self._get_obs(), {}

    def step(self, action):
        # Scale action from [-1, 1] to actuator control range
        self.data.ctrl[:] = action
        mujoco.mj_step(self.model, self.data)
        self.current_step += 1

        obs = self._get_obs()
        pelvis_height = self._get_pelvis_height()

        # Reward: forward velocity (x-direction) minus a small effort penalty
        forward_velocity = self.data.qvel[0]
        effort_penalty = 0.001 * np.sum(np.square(action))
        reward = forward_velocity - effort_penalty

        # Termination: fell over
        terminated = pelvis_height < self.fall_height_threshold
        truncated = self.current_step >= self.max_episode_steps

        return obs, reward, terminated, truncated, {}