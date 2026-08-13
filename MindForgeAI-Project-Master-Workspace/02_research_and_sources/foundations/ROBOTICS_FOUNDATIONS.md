# RoboPath AI Foundations: From Zero to the System

## 1. What is a robot navigation system?

A mobile robot is a physical or simulated machine that senses its surroundings, estimates where it is, chooses a safe route to a goal, and commands motors to follow that route. RoboPath AI models this loop in software:

```text
World → sensors → perception/costmap → localization → planner → controller → velocity command → robot motion
                         ↑                                                        │
                         └──────── safety monitor / telemetry ────────────────────┘
```

A **path** is a geometric sequence of positions from start to goal. A **trajectory** adds time, speed, and orientation. A **plan** is not safe merely because it exists: it must be checked against current sensor data and robot limits.

## 2. ROS 2 in plain language

ROS 2 is middleware and a set of conventions for composing a robot from small programs. A **node** has one focused responsibility: for example, publish laser scans, estimate pose, plan a path, or stop the robot. The running nodes and their connections are the ROS graph.

| ROS 2 mechanism | Plain-language use in RoboPath |
| --- | --- |
| Topic | Continuous stream: `/scan`, `/odom`, `/cmd_vel`, `/tf`. |
| Service | Short request/reply: reset a component or query a map. |
| Action | Long task with feedback/cancel: navigate to a goal. |
| Parameter | Configuration without editing code: robot radius, scan range, planner settings. |
| Launch file | One repeatable command that starts related nodes with the right parameters. |
| Package | Installable unit containing code, config, launch files, tests, and metadata. |

`colcon` builds a workspace of packages. `source /opt/ros/humble/setup.bash` puts ROS tools on the shell path; `source install/setup.bash` makes built RoboPath packages discoverable.

## 3. Ubuntu, WSL 2, virtual machines, and Docker

**Ubuntu** is the Linux operating system used because ROS 2 Humble targets Ubuntu 22.04. **WSL 2** runs a real Linux kernel and Ubuntu distribution alongside Windows; it is the selected development environment. A **virtual machine (VM)** emulates an entire computer with its own operating system; WSL 2 is VM-backed but integrated with Windows. Windows drives appear in WSL under `/mnt`, for example `D:` is `/mnt/d`.

**Docker** packages an application and its dependencies as an image; a running instance is a container. It gives reproducible runtime environments, but it does not replace understanding ROS or correct simulation configuration. It is deferred until the core simulation works.

## 4. Simulation: Gazebo, RViz, URDF, and SDF

**Gazebo** simulates a world, gravity, contacts, sensors, and robot motion. **RViz** visualizes ROS information: laser scans, maps, coordinate frames, paths, costmaps, and pose estimates. They serve different purposes: Gazebo is the simulated physics world; RViz is the ROS-data viewer.

A **URDF/Xacro** describes the robot’s links, joints, geometry, inertial values, and sensor placement. An **SDF/world** describes a simulation world and its models/plugins. A realistic model needs correct wheel radius/separation, mass/inertia, collision geometry, and sensor transforms; incorrect values can make localization/navigation appear broken.

## 5. Coordinate frames and TF

Robots use coordinate frames so every measurement has a known reference. TF is the time-stamped transform tree connecting them.

```text
map ──(global localization)──> odom ──(wheel/visual odometry)──> base_link ──> laser
```

- `base_link`: robot body reference.
- `odom`: smooth local estimate that drifts over time.
- `map`: globally consistent map reference; may jump slightly when localization corrects drift.
- `laser`/sensor frame: where a sensor is mounted relative to the robot.

A navigation stack requires this tree to be complete, timestamp-consistent, and physically plausible.

## 6. Perception, occupancy grids, and costmaps

A LiDAR emits range measurements. A **laser scan** lists distances at angles; returns near a wall are short, no return may mean out of range. An **occupancy grid** divides space into cells, usually unknown/free/occupied. It is a probabilistic model, not ground truth.

A navigation **costmap** converts obstacles into driving cost. It usually contains obstacle observations, an inflated safety buffer, and robot footprint information. A cell can be free yet unusable if it is within the inflation radius. The global costmap plans across the map; the local costmap responds near the robot.

## 7. Odometry and localization

**Odometry** estimates change in pose from wheel encoders (and possibly IMU/visual data). For a differential-drive robot, wheel movement estimates linear and angular motion. Wheel slip, unequal wheel radius, and integration error make odometry drift.

**Localization** estimates pose `(x, y, yaw)` in a map and expresses uncertainty. Localization corrects odometry rather than replacing it. The main method for this project is AMCL.

### Monte Carlo Localization / AMCL

Monte Carlo Localization represents many possible robot poses as particles. Each cycle:

1. Move particles according to odometry plus motion noise.
2. Compare expected sensor readings for each particle against actual LiDAR scans.
3. Give likely particles larger weights.
4. Resample, concentrating particles around likely poses while retaining enough diversity to recover.

AMCL is Adaptive Monte Carlo Localization: it varies particle count based on uncertainty. It needs a usable static map, laser-to-base TF, reasonable odometry, an initial pose, and parameters matched to the sensor/map. The particle cloud and pose covariance are evidence of confidence; a pose estimate without uncertainty should not be over-trusted.

## 8. Path planning algorithms

Model a grid/map as a graph: traversable cells are nodes; legal moves are edges with costs.

| Algorithm | Rule | Strength | Limitation |
| --- | --- | --- | --- |
| BFS | Explore layer by layer | Shortest path when every step has equal cost | Does not handle weighted terrain efficiently. |
| Dijkstra | Expand lowest known path cost `g(n)` | Optimal for non-negative weighted edges | Searches broadly; can be slow. |
| A* | Expand lowest `f(n) = g(n) + h(n)` | Efficient and optimal when `h` is admissible/consistent | Quality depends on heuristic and map quality. |
| D* family | Reuse prior search after map/cost changes | Useful for replanning dynamic/partially known maps | More complex; separate from initial A* baseline. |

`g(n)` is cost so far. `h(n)` estimates remaining cost. On a four-connected grid, Manhattan distance is a common admissible heuristic; with diagonal moves, use a compatible Euclidean/octile heuristic. A* does not guarantee a safe drive by itself: collision checking, inflation, controller limits, and fresh sensing still matter.

## 9. Nav2 and control

Navigation2 (Nav2) is the ROS 2 navigation framework. At a high level it receives a goal, uses maps/costmaps and TF, produces a global path, chooses short-horizon velocity commands, performs recovery/replanning, and reports action feedback/results. A controller turns the path into `/cmd_vel` commands. The robot model/controller or simulator acts on those commands.

RoboPath must make explicit which planner plugin is used. If Nav2 is configured with an A*-based planner, report that configuration and version rather than claiming all Nav2 behavior is “A*.” If D* is studied, label it as a separate experimental planner/replanning comparison.

## 10. Safety and safe-stop

A **safe-stop** is a defined system state that commands zero motion when continuing cannot be justified. Triggers can include: obstacle within stopping distance, stale/missing scan, missing/invalid TF, localization covariance over a threshold, no valid path, or a watchdog timeout.

The design must be fail-safe: loss of critical data should stop or prevent motion. A suggested finite-state model is `IDLE → READY → NAVIGATING → SAFE_STOP`, with recovery only through an explicit validation/reset path. The safety component must have control priority over normal navigation commands and log trigger reason, timestamps, relevant readings, and command output.

## 11. Telemetry, rosbag, and evaluation

**Telemetry** is time-stamped operational data: pose, scan health, velocity, planner status, latency, safe-stop state, and error reasons. `rosbag2` records selected ROS topics so an experiment can be replayed or audited.

Minimum metrics:

- planning time and navigation completion time;
- path length and final goal error;
- collisions / near-obstacle minimum clearance;
- localization error (against simulator ground truth when available);
- safe-stop reaction time and false-stop count;
- CPU/memory where relevant;
- success rate across repeated, pre-defined scenarios.

Never delete failed trials. Define conditions, repetitions, and acceptance thresholds before collecting final results.

## 12. Vocabulary checkpoints

- **Mapping:** build a map from sensor data (SLAM is simultaneous localization and mapping).
- **Localization:** estimate pose in an existing map.
- **Global plan:** route through the overall map.
- **Local plan/controller:** immediate safe motion that follows/adjusts the route.
- **Costmap inflation:** turn obstacle proximity into increasing cost/safety clearance.
- **Dynamic obstacle:** object whose occupancy changes after planning.
- **Ground truth:** simulator’s true pose/world state, used only for evaluation—not an input a real robot would have.

