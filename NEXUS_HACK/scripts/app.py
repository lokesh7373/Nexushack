from isaacsim import SimulationApp

CONFIG = {
"width" : 1280,
"height" : 720,
"window_width" : 1920,
"window_height" : 1080,
"headless": False,
"hide_ui":False,
"renderer": "RaytracedLighting",
"display_options": 3286,
}
simulation_app = SimulationApp(launch_config=CONFIG)
# simulation_app = SimulationApp({"headless": False})

# from isaacsim.core.utils.extensions import enable_extension
# simulation_app.set_setting("/app/window/drawMouse",True)

# enable_extension("omni.kit.livestream.webrtc")
# simulation_app = SimulationApp({"headless": False})

import omni.kit.app
manager = omni.kit.app.get_app().get_extension_manager()
manager.set_extension_enabled_immediate("omni.isaac.ros2_bridge",True)

import numpy as np
import os
from isaacsim.core.api import World
from isaacsim.core.utils.prims import define_prim
from isaacsim.core.utils.stage import add_reference_to_stage,clear_stage
from isaacsim.robot.policy.examples.robots import SpotFlatTerrainPolicy
import omni.graph.core as og

from isaacsim.sensors.camera import Camera
import omni
import omni.usd
from pxr import UsdShade, Sdf, Usd


import socket
import json
import time 
import random 
import threading
from threading import Lock
request_lock = Lock()
from collections import deque
from queue import Queue

# NUMBERS_DIR = "/workspace/server_room/Lokesh/Server_Room_L40/Numbers/" 
# NUMBERS_DIR = "/home/surendra/Documents/Isaac_2/Isaac-5.0.0_bind/server_room/Lokesh/Server_Room_L40/Numbers"
NUMBERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "./Numbers")) 
CHECK_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "./check_file.txt")) 
SPOT_PRIM_PATH = "/World/spot"
CAM_PRIM = "/World/spot/base_link/Camera_01"
SPOT_POS = [0.0, 12.0, 0.7543]
LINEAR_SPEED_MULITIPLIER = 1.0
ANGULAR_SPEED_MULITIPLIER = 1.0
MAX_ALLOWED_TURN = 0.4

#######################################
######### GLOBAL VARIABLES ############
#######################################

SERVER_IP = "xxxxxxx"
PORT = xxxxx
ADDR = (SERVER_IP,PORT)
FORMAT = 'utf-8'

#node_path = "/World/server_room/spot/Graph/ActionGraph/ros2_subscribe_twist"
node_path = "/World/spot/Graph/ActionGraph/ros2_subscribe_twist"
random_points = {
    "machine_1_2": (0.04, 1.09),
    "machine_4_1": (4.37, -6.27),
    "machine_5_3": (8.49, -0.148),
    "machine_8_1": (12.3, -6.0)
    # "machine_1_2": (4.08, 5.16),
    # "machine_4_3": (8.71, -6.9),
    # "machine_5_1": (12.4, 5.9),
    # "machine_7_4": (16.5, -8.08)
}

#######################################
######### COMMUNICATION SERVER ########
#######################################

class CustomServer():

    def __init__(self):

        self.request_queue = deque()
        self.result_queue = Queue()
        self.connections = {}

        # Server 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_client(self,conn,addr):

        print()
        print('_________________________________________________________')
        print()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
        print(f' 🗄️  -- [SERVER] : {addr} Connected')
        

        data = conn.recv(4096)
        message = json.loads(data.decode()) # Will Recive the request as dict


        print(f' 🗄️  -- [SERVER] : Msg Recieved')
        print()
        print(f" --- 🔘 --- Msg Id   : {message['id']}")
        print(f" --- 🔘 --- Msg Type : {message['type']}")
        print(f" --- 🔘 --- Action   : {message['action']}")
        print(f" --- 🔘 --- Params   : {message['parameters']}")
        print(f" --- 🔘 --- Status   : {message['action_completed']}")
        print()
        print('_________________________________________________________')
        print()

        # Store The Action In Command Queue                                                                      
        request = {message['id']:message}
        with request_lock:
            self.request_queue.append(request)

        # Store The Active Connections in Connections Dict
        self.connections[message['id']] = (conn,addr)

        response = {
            'id' : message['id'],
            'status' : 'Request Accepted'
        }
        conn.send(json.dumps(response).encode())

    def send_response(self):

        req_status = self.result_queue.get()
        request = req_status['request']
       
        print()
        print('_________________________________________________________')
        print()
        print(" 🟢 -- [ISAAC] : Command Executed - ✅")
        print()
        print(f" --- ♻️ --- Action Id : {req_status['id']}")
        print(f" --- ♻️ --- Action    : {request[req_status['id']]['action']}")
        print(f" --- ♻️ --- Status    : {req_status['status']}")
        print()
        print('_________________________________________________________')
        print()

        if request[req_status['id']]['type'] == 'task':

            for id, conn in self.connections.items():
                if id == req_status['id']:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
                    print(f' 🗄️  -- [SERVER] : Sending Response -> {conn} ')
                    print()  
                    print('_________________________________________________________')

                    req_status.pop('request')
                    conn[0].send(json.dumps(req_status).encode())
                    conn[0].close()
                    self.connections.pop(req_status['id'])
                    break

    def start_server(self):

        self.server.bind(ADDR)
        self.server.listen()
        print()
        print('_________________________________________________________')
        print()
        print(f" 🗄️  -- [SERVER] : Custom Isaac Server Listening On - {ADDR}")
        print()
        print('_________________________________________________________')
        print()

        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.handle_client, args=(conn,addr), daemon=True).start()

    def stop_server(self):

        print()
        print('_________________________________________________________')
        print()
        print(f" 🗄️  -- [SERVER] : Closing Server .....⛔.......⛔........ ")
        print()
        print('_________________________________________________________')
        self.server.close()



class QuadrupedController():

    def __init__(self,quadruped_prim_path,quadruped_pos,quadruped_name):

        self.quaduped_command = np.zeros(3)
        self._name = quadruped_name

         # Initializing Robots
        self.quadruped = SpotFlatTerrainPolicy(
            prim_path=quadruped_prim_path,
            name=quadruped_name,
            position=quadruped_pos,
        )

        self.current_location = 'home'
        self.previous_location = None
        self.goal_threshold = 0.18

    def quadruped_callback(self,step_size):
        self.quadruped.forward(step_size, self.quaduped_command)

class CameraTracker:
    def __init__(self, cam_path):
        self.cam_path = cam_path
        self.camera = Camera(prim_path = self.cam_path)
        self.camera.initialize()
        self.camera.pause()

    def get_raw_frame(self):
        self.camera.resume()
        return self.camera.get_current_frame().get_rgb()

# How many "reading planes" per group inside each Meter_XX
METER_PLANE_COUNTS = {
    "A_01": 4,
    "A_02": 3,
    "A_03": 4,
    "A_04": 4,
    "A_05": 3,
}

MACHINE_ROOTS = ["/World/Machine_01","/World/Machine_02","/World/Machine_03","/World/Machine_04","/World/Machine_05","/World/Machine_06","/World/Machine_07","/World/Machine_08"]
METER_BLOCKS  = ["Meter_01", "Meter_02", "Meter_03", "Meter_04"]

# Timing: rightmost plane updates ~5s, leftmost ~25-30s (with jitter)
RIGHTMOST_RANGE = (4.5, 5.5)     # seconds
LEFTMOST_RANGE  = (25.0, 30.0)   # seconds

# OmniPBR texture input
TEXTURE_INPUT_NAME = "diffuse_texture"
# --------------------------------------------

GROUPS_IN_METER = METER_PLANE_COUNTS


# ---------- Helpers ----------
def lerp(a, b, t):
    return a + (b - a) * t

def rand_range(rng):
    return random.uniform(rng[0], rng[1])

def compute_interval_for_index(i_left_to_right, n):
    if n <= 1:
        return rand_range(LEFTMOST_RANGE)
    t = i_left_to_right / (n - 1)  # 0..1 left->right
    lo = lerp(LEFTMOST_RANGE[0], RIGHTMOST_RANGE[0], t)
    hi = lerp(LEFTMOST_RANGE[1], RIGHTMOST_RANGE[1], t)
    return random.uniform(lo, hi)

def build_planes_under_group(stage, group_root: str, count: int):
    paths = [f"{group_root}/Plane"]
    for i in range(1, count):
        p1 = f"{group_root}/Plane_{i:02d}"  # Plane_01
        p2 = f"{group_root}/Plane_{i}"      # Plane_1
        paths.append(p1 if stage.GetPrimAtPath(p1).IsValid() else p2)

    for p in paths:
        if not stage.GetPrimAtPath(p).IsValid():
            raise RuntimeError(f"Plane prim not found: {p}")
    return paths

def build_all_groups(stage):
    meters = {}
    for machine_root in MACHINE_ROOTS:
        for meter_block in METER_BLOCKS:
            meter_root = f"{machine_root}/{meter_block}"
            if not stage.GetPrimAtPath(meter_root).IsValid():
                # keep warn but don't crash
                print(f"[WARN] Missing meter block, skipping: {meter_root}")
                continue

            for group_name, plane_count in GROUPS_IN_METER.items():
                group_root = f"{meter_root}/{group_name}"
                if not stage.GetPrimAtPath(group_root).IsValid():
                    continue

                key = f"{machine_root}|{meter_block}|{group_name}"
                meters[key] = build_planes_under_group(stage, group_root, plane_count)

    return meters

def get_bound_shader_path_for_prim(stage, prim_path: str) -> str:
    prim = stage.GetPrimAtPath(prim_path)
    if not prim.IsValid():
        raise RuntimeError(f"Prim not found: {prim_path}")

    mat = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
    if not mat:
        raise RuntimeError(f"No material bound to {prim_path}")

    mat_prim = mat.GetPrim()

    shader_prim = None
    for p in Usd.PrimRange(mat_prim):
        if p.GetTypeName() == "Shader":
            shader_prim = p
            break

    if shader_prim is None:
        raise RuntimeError(f"No Shader found under material {mat.GetPath()} (bound to {prim_path})")

    return str(shader_prim.GetPath())

def set_shader_texture_by_path(stage, shader_path: str, texture_abs_path: str) -> bool:
    shader_prim = stage.GetPrimAtPath(shader_path)
    if not shader_prim.IsValid():
        return False

    shader = UsdShade.Shader(shader_prim)
    inp = shader.GetInput(TEXTURE_INPUT_NAME)
    if not inp:
        inp = shader.CreateInput(TEXTURE_INPUT_NAME, Sdf.ValueTypeNames.Asset)
    inp.Set(texture_abs_path)
    return True

def wait_for_any_prim(stage, prim_paths, timeout_s=30.0):
    """Wait until at least one prim path becomes valid (stage finished loading enough)."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        for p in prim_paths:
            if stage.GetPrimAtPath(p).IsValid():
                return True
        # step the app a bit so USD can load/resolve
        simulation_app.update()
        time.sleep(0.05)
    return False


class MeterDigitsManager:
    def __init__(self, stage, meters_dict):
        self.stage = stage
        self.meters_dict = meters_dict
        self.items = []  # {plane_path, shader_path, next_time, interval_fn}

    def build(self):
        numbers_dir_abs = os.path.abspath(NUMBERS_DIR)
        if not os.path.isdir(numbers_dir_abs):
            raise RuntimeError(f"NUMBERS_DIR not found: {numbers_dir_abs}")

        for d in range(10):
            p = os.path.join(numbers_dir_abs, f"{d}.png")
            if not os.path.exists(p):
                raise RuntimeError(f"Missing texture: {p}")

        now = time.time()

        for meter_name, plane_paths in self.meters_dict.items():
            n = len(plane_paths)
            for i, plane_path in enumerate(plane_paths):
                shader_path = get_bound_shader_path_for_prim(self.stage, plane_path)

                first_delay = random.uniform(0.1, 1.0)

                def make_interval_fn(ii=i, nn=n):
                    return lambda: compute_interval_for_index(ii, nn)

                self.items.append({
                    "meter": meter_name,
                    "plane_path": plane_path,
                    "shader_path": shader_path,
                    "next_time": now + first_delay,
                    "interval_fn": make_interval_fn(),
                })

        print(f"[MeterDigitsManager] Built {len(self.items)} plane timers.")

    def update(self):
        now = time.time()
        for it in self.items:
            if now < it["next_time"]:
                continue

            digit = random.randint(0, 9)
            tex = os.path.abspath(os.path.join(NUMBERS_DIR, f"{digit}.png"))

            ok = set_shader_texture_by_path(self.stage, it["shader_path"], tex)
            if not ok:
                # re-resolve shader path and retry once
                try:
                    it["shader_path"] = get_bound_shader_path_for_prim(self.stage, it["plane_path"])
                    set_shader_texture_by_path(self.stage, it["shader_path"], tex)
                except Exception:
                    pass

            it["next_time"] = now + it["interval_fn"]()

    
def main():

    # Staring Communication Server On Seperate Thread
    server = CustomServer()
    threading.Thread(target=server.start_server,daemon=True).start()

    # Active Action Variable
    commands_to_execute = deque()
    commands_executed = deque()
    
    usd_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./nexus.usd")) 

    clear_stage()
    define_prim("/World")
    dt = 500
    world = World(stage_units_in_meters=1.0, physics_dt=1 / dt, rendering_dt=10/dt)
    add_reference_to_stage(usd_path=usd_path, prim_path="/World")
    world.reset()

    spot = QuadrupedController(SPOT_PRIM_PATH,SPOT_POS,'spot_1')
    world.add_physics_callback("spot_callback", callback_fn=spot.quadruped_callback)
    spot.quadruped.initialize()

    for i in range(50):
        world.step(render=True)
        print(i)

    cam = CameraTracker(CAM_PRIM)
    print("Done with cam initialization")
    stage = omni.usd.get_context().get_stage()  # just get current stage (already loaded)
    METERS = build_all_groups(stage)
    mgr = MeterDigitsManager(stage, METERS)
    mgr.build()

    data_written = False

    while simulation_app.is_running():

        mgr .update()
        lin_xyz = og.Controller.get(og.Controller.attribute(f"{node_path}.outputs:linearVelocity"))
        ang_xyz = og.Controller.get(og.Controller.attribute(f"{node_path}.outputs:angularVelocity"))
        vx = lin_xyz[0]
        vy = lin_xyz[1]
        vyaw = ang_xyz[2]
        spot.quaduped_command = np.array([vx,vy,vyaw])
        # print("Lin,Ang :",spot.quaduped_command)

        with request_lock:

            # Check Whether Request Queue Has Any Requests
            if server.request_queue:
                commands_to_execute.append(server.request_queue.popleft())

            for request in commands_to_execute:
                for action in request:

                    if not request[action]['action_completed']:

                        print()
                        print(" 🟢 -- [ISAAC] : Executing Command - ⏳")
                        print()
                        print(f" --- ♻️ --- Action Id : {request[action]['id']}")
                        print(f" --- ♻️ --- Action    : {request[action]['action']}")
                        print(f" --- ♻️ --- Params    : {request[action]['parameters']}")
                        print(f" --- ♻️ --- Status    : {request[action]['action_completed']}")
                        print()

                        # Checking The Request Is Part OF A Task
                        if request[action]['type'] == 'task':

                            if request[action]['action'] == 'navigation':

                                params = request[action]['parameters']
                                machine, meter = params['machine'], params['meter']

                                print(f"      --- 🤖 --- Robot Velocity         : {spot.quaduped_command}")


                                if not data_written:
                                    print(f"      --- 🤖 --- Writing Data For Nav2 : True {random_points[f'machine_{machine}_{meter}'][0]} {random_points[f'machine_{machine}_{meter}'][1]} None")
                                    print("Writing data")
                                    with open(CHECK_FILE,"w") as f:
                                        f.write(f"True {random_points[f'machine_{machine}_{meter}'][0]} {random_points[f'machine_{machine}_{meter}'][1]} None")
                                    data_written = True 

                                with open(CHECK_FILE,"r") as f:
                                    data = f.read().strip().split()
                                    
                                    print(f"      --- 🤖 --- Reading Data From Nav2 : {data}")
                                    if data[3]=="True":
                                        status = True
                                        with open(CHECK_FILE,"w") as f:
                                            f.write(f"None None None None")

                                    else:
                                        status = False


                                request[action]['action_completed'] = status # Setting Flags to navigate

                                # # Setting Ack To False When Action Is Completed
                                request[action]['ack_after_action_completed'] = not request[action]['action_completed'] 
                            
                            if request[action]['action'] == 'get camera feed':
                            
                                params = request[action]['parameters']
                                machine, meter = params['machine'], params['meter']

                                # cam.resume()
                                a = cam.get_raw_frame()
                                print("Camera Frame: ",a)

                                request[action]['action_completed'] = True

                                # # Setting Ack To False When Action Is Completed
                                request[action]['ack_after_action_completed'] = not request[action]['action_completed'] 

                    else:
                    
                        if not request[action]['ack_after_action_completed']:
                        
                            # Resetting Flags
                            if request[action]['action'] == 'navigation':

                                response = {
                                'id' : request[action]['id'],
                                'status' : 'Navigation Command Executed',
                                'request' : request
                                }

                            elif request[action]['action'] == 'get camera feed':

                                response = {
                                'id' : request[action]['id'],
                                'status' : 'Camera Feed Command Executed',
                                'request' : request
                                }    

                            # Adding Status To Result Queue
                            server.result_queue.put(response)

                            # Server Send Response Back To Client
                            server.send_response()

                            # Setting Ack To True When Its Acknowledged To Client
                            request[action]['ack_after_action_completed'] = True  

                        commands_executed.append(request) 

        world.step(render = True)

        # Removing Executed Commands
        for req in commands_executed:
            if req in commands_to_execute:
                commands_to_execute.remove(req)
        

       
    simulation_app.close()


    
if __name__ == '__main__':
    main()
