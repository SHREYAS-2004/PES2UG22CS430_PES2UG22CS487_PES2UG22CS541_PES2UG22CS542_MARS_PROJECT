from controller import Robot, InertialUnit, Receiver, Camera, Keyboard
import math
import numpy as np

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Motors
left_motor = robot.getDevice("left_rear_wheel")
right_motor = robot.getDevice("right_rear_wheel")
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))

# Steering
left_steer = robot.getDevice("left_steer")
right_steer = robot.getDevice("right_steer")
left_steer.setPosition(0.0)
right_steer.setPosition(0.0)

# IMU
imu = robot.getDevice("inertial unit")
imu.enable(timestep)

# Receiver
receiver = robot.getDevice("receiver")
receiver.enable(timestep)

# Camera
camera = robot.getDevice("camera")
camera.enable(timestep)

# GPS
gps = robot.getDevice("gps")
gps.enable(timestep)

# Keyboard
keyboard = Keyboard()
keyboard.enable(timestep)

# Navigation config
arrived_threshold = 1.0
max_steering_angle = 0.25  # reduced sensitivity
base_speed = 30

print("🚗 TeslaModel3 with yellow line following + keyboard control initialized...")

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

target_received = False
target_pos = (0.0, 0.0)

# --- Main Loop ---
while robot.step(timestep) != -1:
    # Wait for supervisor to send destination
    if not target_received and receiver.getQueueLength() > 0:
        try:
            raw_data = receiver.getString()
            x_str, z_str = raw_data.strip().split(',')
            x = float(x_str)
            z = float(z_str)
            target_pos = (x, z)
            target_received = True
            print(f"🎯 Target received from supervisor: x={x:.2f}, z={z:.2f}")
        except Exception as e:
            print(f"⚠ Failed to parse position data: {e}")
        receiver.nextPacket()
        continue

    if not target_received:
        print("📡 Waiting for position data from supervisor...")
        continue

    # Read robot's actual GPS position
    current_x, _, current_z = gps.getValues()
    current_pos = (current_x, current_z)
    dist = distance(current_pos, target_pos)

    if dist < arrived_threshold:
        print("✅ Destination reached!")
        left_motor.setVelocity(0.0)
        right_motor.setVelocity(0.0)
        break

    # --- Keyboard Control ---
    key = keyboard.getKey()
    manual_mode = False
    steering = 0.0
    speed = base_speed

    while key != -1:
        if key in [Keyboard.UP, ord('W')]:
            speed = base_speed
            manual_mode = True
        elif key in [Keyboard.DOWN, ord('S')]:
            speed = -base_speed / 2
            manual_mode = True
        elif key in [Keyboard.LEFT, ord('A')]:
            steering = -max_steering_angle  # fixed: left is negative
            manual_mode = True
        elif key in [Keyboard.RIGHT, ord('D')]:
            steering = max_steering_angle   # fixed: right is positive
            manual_mode = True
        key = keyboard.getKey()

    if not manual_mode:
        # ---- Yellow Line Detection ----
        img = camera.getImage()
        width = camera.getWidth()
        height = camera.getHeight()

        line_position = 0
        count = 0
        scan_rows = 10  # Scan more rows for robustness

        for y in range(height - scan_rows, height):
            for x in range(width):
                r = Camera.imageGetRed(img, width, x, y)
                g = Camera.imageGetGreen(img, width, x, y)
                b = Camera.imageGetBlue(img, width, x, y)

                if r > 180 and g > 170 and b < 120 and abs(r - g) < 40:
                    line_position += x
                    count += 1

        if count > 0:
            avg_line_pos = line_position / count
            error = avg_line_pos - (width / 2)
            steering = -error / (width / 2) * max_steering_angle
        else:
            print("⚠ Yellow line not found. Going straight.")
            steering = 0.0

        steering = np.clip(steering, -max_steering_angle, max_steering_angle)
        speed = base_speed * (1 - 0.5 * abs(steering))

    # Apply steering and speed
    left_steer.setPosition(steering)
    right_steer.setPosition(steering)
    left_motor.setVelocity(speed)
    right_motor.setVelocity(speed)

    control_type = "🕹 Manual" if manual_mode else "🟡 Auto (Line)"
    print(f"{control_type} | Steering: {steering:.2f} | Speed: {speed:.2f} | Distance: {dist:.2f}")
