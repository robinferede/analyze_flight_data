import numpy as np
import cv2
from . import graphics
import time


# graphics
cam = graphics.Camera(
    pos=np.array([-5., 0., 0.]),
    theta=np.zeros(3),
    cameraMatrix=np.array([[1.e+3, 0., 432.], [0., 1.e+3, 432.], [0., 0., 1.]]),
    distCoeffs=np.array([0., 0., 0., 0., 0.])
)

cam.rotate([0., -np.pi/2, 0.])

# grid = graphics.create_grid(10, 10, 0.1)
big_grid = graphics.create_grid(6, 6, 1)

drone, forces = graphics.create_drone(0.08)

scl = 0.2
d = 0.8
b = 1

# options
follow=False
auto_play=False
draw_path=False
draw_forces=False
record=False

def nothing(x):
    pass


def animate(t, x, y, z, phi, theta, psi, u, autopilot_mode=[], target=[], waypoints=[], file='output.mp4', multiple_trajectories=False, simultaneous=False, colors=[], names=[], alpha=0, step=1, **kwargs):
    follow=False
    auto_play=False
    draw_path=False
    draw_forces=False
    record=False
    
    traj_index = 0
    
    if simultaneous:
        traj_index = np.argmax(np.array([ti[-1] for ti in t]))
    
    if multiple_trajectories:
        t_ = t[traj_index]
        pos = np.stack([x[traj_index],y[traj_index],z[traj_index]]).T
        ori = np.stack([phi[traj_index],theta[traj_index],psi[traj_index]]).T
        u_ = u[traj_index]
    else:
        t_ = t
        pos = np.stack([x,y,z]).T
        ori = np.stack([phi,theta,psi]).T
        u_ = u
    
    cv2.namedWindow('animation')
    cv2.setMouseCallback('animation', cam.mouse_control)
    cv2.createTrackbar('t', 'animation', 0, t_.shape[0]-1, nothing)
    
    paths = []
    if simultaneous:
        for i in range(len(t)):
            p = np.stack([x[i],y[i],z[i]]).T
            paths.append(graphics.create_path([pi for pi in p[0::5]]))
    
    path = graphics.create_path([p for p in pos[0::5]])
    
    waypoints = [graphics.create_path([v,v+[0,0,0.01]]) for v in waypoints]
    start_time = time.time()
    time_index = 0
    video_step = 1
    
    while True:
        if auto_play:
            if record:
                if time_index<len(t_)-video_step:
                    # temporary #################################
                    #if t_[time_index] > 16:
                    #    print('recording ended')
                    #    out.release()
                    #    record = False
                    #    print('recording saved in ' + file)
                    #############################################
                    time_index+=video_step

            else:
                current_time = time.time() - start_time
                for i in range(len(t_)):
                    if t_[i] > current_time:
                        time_index = i
                        break
                if time_index == -1:
                    current_time = t_[time_index]
        else:
            time_index = cv2.getTrackbarPos('t', 'animation')
            current_time = t_[time_index]

        
        drone.translate(pos[time_index] - drone.pos)
        drone.rotate(ori[time_index])

        T = u_[time_index]                     # T = (T1, T2, T3, T4)
        graphics.set_thrust(drone, forces, T*scl)

        if follow:
            cam.set_center(drone.pos)
        else:
            cam.set_center(np.zeros(3))

        # using screen resolution of 1536x864
        frame = 255*np.ones((864, 864, 3), dtype=np.uint8)

        # text
        cv2.putText(frame, "t = " + str(round(t_[time_index], 2)), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))
        if multiple_trajectories:
            cv2.putText(frame, "i = " + str(traj_index), (100, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))

        # drawing
        big_grid.draw(frame, cam, color=(200, 200, 200), pt=1)
#         grid.draw(frame, cam, color=(100, 100, 100), pt=1)
        
        for w in waypoints:
            w.draw(frame, cam, color=(0,0,255),pt=4)
            
        if time_index < len(target):
            tt = target[time_index]
            tt_graphic = graphics.create_path([tt,tt+[0,0,0.01]])
            tt_graphic.draw(frame, cam, color=(0,0,255),pt=8)

        if draw_path and not simultaneous:
            path.draw(frame, cam, color=(0, 255, 0), pt=2)
            
        if simultaneous:
            if draw_path:
                for i in range(len(t)):
                    if len(colors)>i:
                         paths[i].draw(frame, cam, color=colors[i], pt=1)
                    else:
                         paths[i].draw(frame, cam, color=(0, 255, 0), pt=1)
            for i in range(len(t)):
                pos_i = np.stack([x[i],y[i],z[i]]).T
                ori_i = np.stack([phi[i],theta[i],psi[i]]).T
                u_i = u[i]
                time_index_i = 0
                for j in range(len(t[i])):
                    time_index_i = j
                    if t[i][j] > t_[time_index]:
                        break
                drone.translate(pos_i[time_index_i] - drone.pos)
                drone.rotate(ori_i[time_index_i])
                T_i = u_i[time_index_i]                     # T = (T1, T2, T3, T4)
                graphics.set_thrust(drone, forces, T_i*scl)
                if len(colors)>i:
                    drone.draw(frame, cam, color=colors[i], pt=2)
                else:
                    drone.draw(frame, cam, color=(255, 0, 0), pt=2)
                if draw_forces:
                    for force in forces:
                        force.draw(frame, cam, pt=2)
        elif multiple_trajectories and len(colors)> traj_index:
            drone.draw(frame, cam, color=colors[traj_index], pt=2)
        elif pos[time_index][2] > 0:
            drone.draw(frame, cam, color=(0, 0, 255), pt=2)
        elif len(autopilot_mode) > 0:
            if autopilot_mode[time_index] == 0 or True:
                drone.draw(frame, cam, color=(255, 0, 0), pt=2)
            else:
                drone.draw(frame, cam, color=(0, 255, 0), pt=2)
                cv2.putText(frame, '[gcnet active]', (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0))                
        else:
            drone.draw(frame, cam, color=(255, 0, 0), pt=2)
            
        if draw_forces and not simultaneous:
            for force in forces:
                force.draw(frame, cam, pt=2)
            
        for i in range(len(names)):
            if len(colors)>i:
                cv2.putText(frame, names[i], (700, 20*(i+1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], thickness=2)
            else:
                cv2.putText(frame, names[i], (700, 20*(i+1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), thickness=2)
        if record:
            out.write(frame)
            cv2.putText(frame, '[recording]', (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0))

        control = cv2.waitKeyEx(1)
        if control == 106 and multiple_trajectories:      # J KEY
            time_index = 0
            start_time = time.time() - t_[time_index]
            traj_index = max(0, traj_index-step)
            t_ = t[traj_index]
            pos = np.stack([x[traj_index],y[traj_index],z[traj_index]]).T
            ori = np.stack([phi[traj_index],theta[traj_index],psi[traj_index]]).T
            u_ = u[traj_index]
            path = graphics.create_path([p for p in pos[0::5]])
        if control == 108 and multiple_trajectories:      # L KEY
            time_index = 0
            start_time = time.time() - t_[time_index]
            traj_index = min(len(t)-1, traj_index+step)
            t_ = t[traj_index]
            pos = np.stack([x[traj_index],y[traj_index],z[traj_index]]).T
            ori = np.stack([phi[traj_index],theta[traj_index],psi[traj_index]]).T
            u_ = u[traj_index]
            path = graphics.create_path([p for p in pos[0::5]])
        if control == 114:      # R KEY
            if record:
                print('recording ended')
                out.release()
                print('recording saved in ' + file)
            else:
                print('recording started')
                # videowriter
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                
                # freq must be less than 100
                dt = np.mean(t_[1:]-t_[:-1])
                fps = 1/dt
                while fps>30:
                    video_step += 1
                    fps = 1/(dt*video_step)
                print(fps)                    
                out = cv2.VideoWriter(file, fourcc, fps=fps, frameSize=(864, 864))
            record = not record
        if control == 102:      # F KEY
            follow = not follow
        if control == 112:      # P KEY
            draw_path = not draw_path
        if control == 115:      # S KEY
            draw_forces = not draw_forces
        if control == 32:       # SPACE BAR
            auto_play = not auto_play
            start_time = time.time() - t_[time_index]
        if control == 49:       # 1
            cam.zoom(1.05)
        if control == 50:       # 2
            cam.zoom(1/1.05)
        if control == 27:       # ESCAPE
            break
        
        cv2.imshow('animation', frame)
    
    cv2.destroyAllWindows()
