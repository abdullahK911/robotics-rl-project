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

## Week 7 — G1 Locomotion Environment: Root Cause Debugging & Resolution

**Status: COMPLETE**

### Deliverables
- Working custom Gym-style environment (`g1_locomotion_env.py`) for the Unitree G1 humanoid, with:
  - Reset logic using a hand-crafted stable standing pose (bent knees, compensating hip/ankle angles)
  - PD position control (target = current angle + bounded delta, converted to torque via Kp/Kd)
  - Reward function: forward velocity + alive bonus − effort penalty − height-sag penalty − fall penalty
  - Fall detection based on pelvis height threshold (0.5m)
- Validated via an isolated, policy-free PD-holds-pose test before any training
- A trained PPO policy (`ppo_g1_locomotion_v10.zip`) that reliably survives ~435-627 steps per episode (up from ~120-129 steps across 9 earlier versions)
- Confirmed live in the MuJoCo viewer: matches training statistics almost exactly (no train/inference mismatch)

### The core bug (versions 1-9)
Every version — different reward shaping, torque scaling, PD control, stable starting pose, parallelized training, 6M-step runs — plateaued at the exact same ~110-129 step survival time, regardless of the fix applied. 

**Root cause: the robot model file (`g1_23dof.xml`) has no ground plane.** It's a bare robot definition, not a full "scene." The correct file to load is `scene_23dof.xml`, which combines the robot with an actual floor, lighting, and world setup. Without it, the robot was in pure free-fall the entire time — confirmed via an isolated PD-holds-pose test showing pelvis height accelerating into negative numbers (0.79 → 0.004 → -2.35 → -6.28 → ... ), the signature of unopposed gravity, not a balance failure.

Once fixed (switching to `scene_23dof.xml`), the very next training run jumped from ep_len_mean ~123 to ~460 — a ~4x improvement — with no other code changes.

### Other real fixes made along the way (all still necessary, just not sufficient alone)
1. **Action/torque scaling** — policy actions in [-1, 1] were being sent directly as torque commands, when real actuator ranges go up to ±139 N·m. Fixed by scaling actions to each actuator's real `ctrlrange`.
2. **PD position control** — switched from raw torque control to target-position + PD (Kp/Kd) control, standard practice for humanoid RL, since raw torque exploration is notoriously hard to learn from.
3. **Bounded delta actions** — changed the policy's target from an absolute position across the full joint range to a small bounded delta from the current position, fixing PPO's `approx_kl`/`clip_fraction` instability (both were far above healthy values before this fix).
4. **Stable starting pose** — the model has no predefined keyframe; resetting to all-zero joint angles produced an unnaturally rigid, unstable stance. Replaced with a hand-crafted bent-knee standing pose.
5. **PD gain tuning** — increased Kp (80→180) and Kd (5→8) after an isolation test showed the original gains couldn't hold the standing pose against gravity for more than ~600 steps even with zero policy noise.

### Current limitation (carried into Week 8)
The trained policy survives ~435-627 steps but does so by staying in a low, crouched, largely static position — not by walking. This is a reward-shaping issue, not an environment bug: `alive_bonus` and the fall/height penalties currently dominate over `forward_velocity`, so the policy found "survive by staying low and rigid" as a local optimum rather than being pushed to actually walk. Fixing this (stronger forward-velocity weighting, possibly a standing-still penalty) is Week 8's problem, not Week 7's.

### Key lesson
When multiple independent, reasonable fixes all fail to move the same metric in the same way, stop iterating on secondary hypotheses and look for a shared, structural assumption underneath all of them. Here, that assumption — "the robot is standing on a floor" — was silently false the entire time, and every other diagnosis (reward, control scheme, training duration, parallelization) was solving real but secondary problems on top of a fundamentally broken physical setup.