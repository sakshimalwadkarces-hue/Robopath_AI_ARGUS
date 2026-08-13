# RoboPath AI: ROS 2 Working Protocol

## Purpose

This is the repeatable start, run, inspect, stop, and record procedure for RoboPath AI. Follow it before changing code. The project is a ROS 2 Humble mobile-robot simulation: perceive obstacles, localize, plan a route, execute safely, and stop on invalid data or an unsafe command.

## Confirmed local baseline (4 August 2026)

| Component | Status | Decision |
| --- | --- | --- |
| Windows host | Available | Documentation/report vault lives in this repository. |
| WSL 2 | Ubuntu 22.04.5 registered | Use as the ROS execution environment. |
| ROS 2 | Humble installed at `/opt/ros/humble` | Source it in every new shell. |
| Build tool | `colcon` installed | Use for workspace builds. |
| Simulator | Gazebo Classic 11 and `gazebo_ros` installed | Initial simulator target. |
| Docker | Not installed | Not required for week 1; defer until a reproducible deployment image is needed. |
| Current RoboPath source | Scaffold only; no package files yet | Build the minimal packages in Linux-native storage. |

## Storage rule: Windows vault, Linux build workspace

The repository is mounted in Ubuntu as `/mnt/d/Project_Legacy/MindForgeAI-Project-Master-Workspace`. Do **not** run `colcon build` there. It is NTFS-mounted and may be slow or have Linux permission/symlink edge cases.

Use this layout instead:

```text
Windows repository (documents, exports, backups)
└── D:\Project_Legacy\MindForgeAI-Project-Master-Workspace

Linux-native execution workspace (source + build output)
└── ~/robopath_ws
    ├── src/                 # active ROS packages
    ├── build/               # generated; never copy to report
    ├── install/             # generated
    └── log/                 # generated test/build evidence
```

Sync source deliberately; do not blindly synchronize generated folders. Suggested initial copy (run in Ubuntu):

```bash
mkdir -p ~/robopath_ws/src
cp -a /mnt/d/Project_Legacy/MindForgeAI-Project-Master-Workspace/04_active_workspaces/RoboPath_AI/src/. ~/robopath_ws/src/
```

When packages are created, make the Linux workspace the active build location and copy reviewed source files back to `06_code/ros2_ws/src/` (create it when first source exists). Keep logs/screenshots in the repository.

## Initiation protocol (every work session)

Open Ubuntu WSL from PowerShell:

```powershell
wsl -d Ubuntu-22.04
```

Then run in Ubuntu:

```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42             # RoboPath team namespace; use the same value for the team
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
cd ~/robopath_ws
test -f install/setup.bash && source install/setup.bash
ros2 doctor --report
```

The last `source` overlays built RoboPath packages only after a successful build. Do not source a stale `install/setup.bash` after changing interfaces; rebuild first.

## Standard build and test loop

```bash
cd ~/robopath_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --event-handlers console_direct+
source install/setup.bash
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

For a single package, substitute `colcon build --packages-select <package_name> --symlink-install`. Record the exact command, Git commit, map/world, parameters, result, and failure in `09_project_diaries/Experiment_Log.md`.

## Bring-up protocol (target architecture)

Once implemented, the only supported project entry point will be:

```bash
ros2 launch robot_bringup simulation.launch.py use_sim_time:=true
```

It must start the world, robot description/state publisher, Gazebo bridge/plugins, localization, Nav2, safe-stop node, telemetry logger, and RViz configuration as appropriate. Do not rely on a sequence of undocumented manual terminals for the final demo.

Before issuing a navigation goal, verify:

```bash
ros2 node list
ros2 topic list
ros2 topic echo /odom --once
ros2 topic echo /scan --once
ros2 run tf2_ros tf2_echo map base_link
```

Expected critical frames are `map → odom → base_link` (with sensor frames below `base_link`). A missing transform, missing `/scan`, invalid covariance, or no localization pose is a no-go condition, not something to work around by driving blindly.

## Safe-stop test protocol

1. Start with a static known map and valid pose.
2. Send one navigation goal and record success, elapsed time, path length, and minimum obstacle clearance.
3. Introduce a dynamic obstacle or intentionally invalidate scan/path input.
4. Verify the safety node publishes zero velocity, cancels/prevents the unsafe motion, emits a timestamped reason, and preserves evidence in telemetry.
5. Repeat at least five times; report successes and failures, never just the best run.

The safe-stop channel must take precedence over nominal navigation. In the final design this is normally enforced by a velocity arbiter/mux or a safety controller, not merely a visual warning.

## Fast diagnosis

| Symptom | First checks |
| --- | --- |
| `ros2: command not found` | `source /opt/ros/humble/setup.bash` |
| Package not found | Build, then `source install/setup.bash`; check package name in `package.xml`. |
| Robot does not move | Check `/cmd_vel`, controller, `/scan`, TF, and Nav2 lifecycle state. |
| RViz/Gazebo GUI cannot open | Check WSLg/display support; run headless tests first. |
| Colcon errors on `/mnt/d` | Move active workspace to `~/robopath_ws`; build there. |
| Robot pose drifts | Inspect wheel/odometry parameters, TF timestamps, and localization particle cloud/covariance. |
| Robot ignores obstacle | Inspect scan range/frame, costmap layers, footprint/inflation, and safety-node priority. |

## Session closure

1. Stop launched processes with `Ctrl+C`; do not leave simulation servers running.
2. Save terminal output or rosbag evidence for significant runs.
3. Update experiment and daily logs.
4. Copy only reviewed source/parameter/launch files to the repository, not `build/`, `install/`, or `log/`.
5. Commit a small, descriptive change with test evidence.

