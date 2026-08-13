# RoboPath AI — Research Report Working Draft

## Working title

**RoboPath AI: Safe Autonomous Mobile-Robot Navigation in a ROS 2 and Gazebo Simulation**

## Abstract (draft; update only with verified results)

This project develops a reproducible ROS 2 simulation for an autonomous mobile robot operating in an obstacle-filled indoor environment. The system will combine Gazebo-based sensing and motion simulation, map-based localization, navigation planning, telemetry collection, and an independently enforced safe-stop mechanism. The research evaluates route-planning behavior, localization quality, navigation success, and safety response under static and dynamic obstacle conditions. At the present baseline, the ROS 2 Humble and Gazebo environment has been verified, while the project-specific robot, navigation stack, and experiments remain under implementation. Therefore, no performance results are claimed in this draft.

## 1. Introduction (draft)

Autonomous mobile robots must transform uncertain sensor observations into safe motion. This requires perception, a reference frame and pose estimate, route planning, local collision avoidance, low-level motion control, and failure handling. The central research problem in RoboPath AI is not only whether a simulated robot reaches a goal, but whether it can stop safely and explainably when its route or input data becomes unsafe.

ROS 2 supports modular robot applications through nodes that communicate using topics, services, actions, and parameters [ROS2-interfaces; ROS2-nodes]. Gazebo provides a physics/sensor simulation environment, while RViz can visualize ROS maps, paths, transforms, and state. The proposed system uses these components to produce reproducible, inspectable experiments rather than an opaque demonstration.

## 2. Problem definition (draft)

In dynamic indoor environments, an apparently valid path can become unsafe because of a newly introduced obstacle, stale sensor message, missing transform, lost localization, or invalid planner output. A navigation pipeline that continues to emit motion commands under such conditions creates collision risk. RoboPath AI investigates a software architecture in which a safety monitor has authority to suppress nominal motion and command a zero-velocity safe-stop while recording the cause.

## 3. Objectives (draft)

1. Construct a reproducible ROS 2 Humble/Gazebo mobile-robot simulation.
2. Model sensing, odometry, coordinate transforms, and map-based pose localization.
3. Configure and evaluate an A*-related/Nav2 navigation baseline, with clearly named planner configuration.
4. Implement and test a fail-safe, independently enforced safe-stop channel.
5. Collect telemetry and repeatable evidence for success, failure, latency, path, and safety metrics.

## 4. Methodology outline (draft)

The study will build the system in increments: robot/sensor simulation, odometry and TF validation, AMCL map localization, Nav2 goal navigation, and safe-stop fault/dynamic-obstacle scenarios. Each scenario will define map/world, initial pose, goal, configuration version, repetitions, expected behavior, metrics, and saved evidence. Simulator ground truth may be used only to evaluate localization error.

## Claim-control table

| Statement | Status on 4 Aug 2026 | Evidence needed before final report |
| --- | --- | --- |
| ROS 2 Humble/Gazebo environment is available | Verified | Environment command output. |
| RoboPath robot spawns in Gazebo | Planned | Launch log + screenshot + topic/TF evidence. |
| AMCL localizes the robot | Planned | Map/particle cloud/pose/covariance + ground-truth comparison. |
| Nav2 performs safe navigation | Planned | Repeated scenario logs and outcome metrics. |
| Safe-stop protects against unsafe input | Planned | Trigger log, zero-velocity evidence, response-time metrics, failure trials. |

