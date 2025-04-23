from controller import Supervisor

# Initialize Supervisor
supervisor = Supervisor()
timestep = int(supervisor.getBasicTimeStep())

# Get the robot node using DEF name
robot_node = supervisor.getFromDef("robot")
if robot_node is None:
    print("❌ ERROR: Could not find DEF 'robot'. Make sure your robot has 'DEF robot' in the .wbt world.")
    exit(1)

# Get the translation field of the robot
translation_field = robot_node.getField("translation")

# Setup emitter
emitter = supervisor.getDevice("emitter")
if emitter is None:
    print("❌ ERROR: Could not find emitter device. Make sure it’s added in the robot's .proto or .wbt.")
    exit(1)

print("🛰️ Supervisor initialized...")

# Load destination from file
destination_map = {
    'A': [42.8, 0.0, 0.441],
    #'B': [-103, 0.0, 0.718],
    'B': [-27.5, 0.0, 0.2734],# Replace with your real coordinates
    # 'C': [-40.7, 0.0, 10.1],  # Replace with your real coordinates
    'C': [-98, 0.0, 0.729],
    'D': [-72.2, 0.0, 0.273], 
}

try:
    with open("destination.txt", "r") as file:
        selected = file.read().strip().upper()
        if selected in destination_map:
            target = destination_map[selected]
            print(f"📍 Destination selected: {selected} -> {target}")
        else:
            print(f"⚠️ Invalid destination '{selected}' in destination.txt. Defaulting to A.")
            target = destination_map['A']
except Exception as e:
    print(f"⚠️ Could not read destination.txt: {e}")
    print("⚠️ Defaulting to destination A.")
    target = destination_map['A']

# Send every N simulation steps
SEND_INTERVAL = 10
step_counter = 0

while supervisor.step(timestep) != -1:
    step_counter += 1

    if step_counter % SEND_INTERVAL == 0:
        # Send selected destination instead of robot's current position
        x = target[0]
        z = target[2]

        message = f"{x:.6f},{z:.6f}"
        emitter.send(message)

        print(f"📡 Target position sent -> x: {x:.2f}, z: {z:.2f}")
