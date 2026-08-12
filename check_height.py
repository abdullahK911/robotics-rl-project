import mujoco

model = mujoco.MjModel.from_xml_path("unitree_mujoco/unitree_robots/g1/g1_23dof.xml")
data = mujoco.MjData(model)
mujoco.mj_forward(model, data)

# Find the torso/pelvis body and print its height (z-position)
for i in range(model.nbody):
    name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_BODY, i)
    print(i, name, data.xpos[i])