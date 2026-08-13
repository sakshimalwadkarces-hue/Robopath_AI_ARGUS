# RoboPath AI: Four-Week Project Plan

## Project outcome

Deliver a reproducible ROS 2 Humble/Gazebo simulation of a mobile robot that localizes, plans, navigates, collects telemetry, and safely stops when critical navigation inputs or commanded movement are unsafe. The final demonstration must be reproducible from documented source and a single supported launch path.

## Milestones

| Week | Outcome | Acceptance gate |
| --- | --- | --- |
| 1 — Foundations and simulation | System design, source package skeleton, robot/world, sensing, TF, odometry, teleoperation | Robot demonstrably publishes valid `/tf`, `/odom`, `/scan`; report foundation and method are drafted. |
| 2 — Localization and navigation | Static map, AMCL, Nav2 goal navigation, baseline A* study/configuration | Five controlled goal trials with logged route/time/outcome; pose and TF evidence available. |
| 3 — Safety and measurement | Safe-stop priority, dynamic obstacle/input-fault scenarios, rosbag/CSV telemetry | Stop behavior forces zero velocity and records reason; repeated safety matrix completed. |
| 4 — Evaluation and handover | Analysis, figures, final report, demo, reproducibility packaging (Docker only if justified) | Fresh-environment-style launch instructions reproduce the demo; results include failures/limits. |

## Day 3 priority

1. Treat the ROS workspace as empty scaffold; create only the minimal valid simulation baseline.
2. Keep execution code in `~/robopath_ws`; use this repository for reviewed source, report, and evidence.
3. Complete foundational notes and report claim controls before implementation results are written.
4. Do not begin Docker, dashboard, ML, or D* integration before week-1 acceptance gate.

