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
