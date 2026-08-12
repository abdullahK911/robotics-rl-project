# Project Notes

## Week 5 — G1 Humanoid Joint Scoping Decision

**Model used:** Unitree G1 (23dof version) — `unitree_mujoco/unitree_robots/g1/g1_23dof.xml`

**Full joint list (30 joints total):**
- Joint 0: floating_base_joint (free-floating root, not directly controlled)
- Joints 1-12: legs (hips, knees, ankles) — locomotion
- Joints 13, 24, 25: waist (yaw, roll, pitch)
- Joints 14-18: left arm (shoulder pitch/roll/yaw, elbow, wrist roll)
- Joints 19-23: right arm (mirror of left)
- Joints 26-29: additional wrist joints (pitch/yaw), both arms

**Scoping decision:**
- **Controlling:** right arm only — joints 19, 20, 21, 22, 23, 28, 29 (shoulder pitch/roll/yaw, elbow, wrist roll/pitch/yaw) — 7 DOF total
- **Locking/ignoring:** legs (1-12), waist (13, 24, 25), left arm (14-18, 26-27), floating base (0)

**Rationale:** Isolating manipulation from locomotion/balance. This is a standard simplification in robot learning research — solving grasping/reaching independently before considering whole-body coordination.

**Open question for Week 6:** This 23dof model has no individual finger/hand joints — wrist is the distal joint. Need to decide whether to (a) attach a simple gripper at the wrist, or (b) switch to the g1_29dof.xml model, which includes hand articulation.

## Week 6 — Pivot to Locomotion + First Humanoid Result

**Decision:** Shifted focus from manipulation (Panda arm grasping) to locomotion — training a humanoid to walk, then sprint, for ~30 seconds without falling. This better aligns with the long-term humanoid robotics goal, and locomotion sim-to-real transfer (domain randomization, gait robustness) is a more central, well-known sim2real problem than manipulation.

**Task spec:** Train a humanoid policy (starting on Gymnasium's Humanoid-v5 benchmark, later applied to the Unitree G1 model) to walk forward, then transition into a sprint, sustaining forward locomotion for ~30 seconds without falling.

**Effect on Week 5 scoping:** Reverses the earlier "right arm only" decision — legs and waist are now the primary controlled joints; arms become secondary (balance/counter-swing); wrist/hand joints are no longer relevant for this phase.

**First result (Humanoid-v5, PPO, 1M timesteps):**
- episodic_return climbed from near-zero/random to a noisy range of ~400-1300 by the end of training
- No consistent collapse — policy is staying upright and moving for meaningfully longer episodes than random
- Curve is noisy, not converged — expected, since published Humanoid-v5 baselines typically need 5-10M+ steps to reach smoother 3000-6000+ returns
- Fixed a Gymnasium 1.x API compatibility issue in CleanRL's episode-info detection logic (`final_info` → `infos["episode"]` / `infos["_episode"]`)

**Next:** Week 7 — build a custom environment definition (reward shaping, domain randomization) for the actual G1 humanoid model, informed by this baseline result.