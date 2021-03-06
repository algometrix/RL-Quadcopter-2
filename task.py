import numpy as np
from physics_sim import PhysicsSim

class Task():
    """Task (environment) that defines the goal and provides feedback to the agent."""
    def __init__(self, init_pose=None, init_velocities=None, 
        init_angle_velocities=None, runtime=5., target_pos=None):
        """Initialize a Task object.
        Params
        ======
            init_pose: initial position of the quadcopter in (x,y,z) dimensions and the Euler angles
            init_velocities: initial velocity of the quadcopter in (x,y,z) dimensions
            init_angle_velocities: initial radians/second for each of the three Euler angles
            runtime: time limit for each episode
            target_pos: target/goal (x,y,z) position for the agent
        """
        # Simulation
        self.sim = PhysicsSim(init_pose, init_velocities, init_angle_velocities, runtime) 
        self.action_repeat = 1

        self.state_size = self.action_repeat * 2
        self.action_low = 390
        self.action_high = 420
        self.action_range = self.action_high - self.action_low 
        self.action_size = 1

        # Goal - hover at z=10, x,y=0        
        self.target_pos = target_pos if target_pos is not None else np.array([0., 0., 10.]) 

    def get_reward(self):
        """Uses current pose of sim to return reward."""
        reward = 0
        
        #reward = reward + 1.-0.3*(abs(self.sim.pose[2] - self.target_pos[2])).sum()
        reward = np.tanh(1 - 0.005*(abs(self.sim.pose[:3] - self.target_pos))).sum()
        
           
        # penalize too far from target position
        #distance = np.linalg.norm(self.target_pos[2] - self.sim.pose[2])
        #if (distance > 2):
        #    reward = reward - min(1,1/(distance + 1)**2)
        

        return reward 

    
    def step(self, rotor_speeds):
        """Uses action to obtain next state, reward, done."""
        reward = 0
        pose_all = []
        for _ in range(self.action_repeat):
            done = self.sim.next_timestep(rotor_speeds) # update the sim pose and velocities
   
            reward += self.get_reward()
            
            # update rotor speed to achieve target height
            # scale to +- 0.1, for input to the network
            z_norm = (self.sim.pose[2] - 10)/3
            z_v_norm = (self.sim.v[2]) / 3
            rotor_norm = (rotor_speeds[0] - self.action_low) / self.action_range * 2 - 1
            pose_all.append(z_norm)
            pose_all.append(z_v_norm)
            #print (z_norm, z_v_norm)
        next_state = np.array(pose_all)

        return next_state, reward, done

    def reset(self):
        """Reset the sim to start a new episode.
        Start each episode with the Quadcopyer a random distance (vertically) away from the target height
        """
        self.sim.reset()
        
        #perturb the start by +- one unit
        perturb_unit = 0.1
        self.sim.pose[2] += (2*np.random.random()-1) * perturb_unit

        z_norm = (self.sim.pose[2] - 10)/10
        z_v_norm = 0
        rotor_norm = 0
        
        state = np.array(([z_norm, z_v_norm]) * self.action_repeat)

        return state