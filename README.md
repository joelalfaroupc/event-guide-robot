# Event Guide Robot — Semantic Navigation & Visual Search

**A TurtleBot3 guide that maps a requested event stand to a navigation goal and a visual target.**

University mobile-robotics project built with ROS 1. The system combines a semantic map, AMCL localization, `move_base` navigation and ArUco detection in a modular four-node architecture.

## What the project delivers

A command such as “quiero ir al stand de Qualcomm” resolves to a stand and a safe navigation pose. After navigation succeeds, the robot searches locally for the corresponding marker and uses its visual position to approach the target.

The semantic configuration contains **four zones and eight stands**. Aliases link ordinary stand names to explicit map coordinates and marker IDs.

## Architecture

```text
User command → Semantic planner → Navigation manager → move_base
                        ↓                 ↓ success
                 Target marker → Local search manager → /cmd_vel
                                        ↑
Camera → ArUco detector → stable target detections
```

| Node | Responsibility |
| --- | --- |
| Semantic planner | Parse configured aliases and publish the zone, navigation pose and marker target. |
| Navigation manager | Send goals through actionlib; handle success, failure and timeouts. |
| Local search manager | Wait for successful navigation, rotate to search, center and approach a stable target, then stop. |
| Vision detector | Detect ArUco markers with OpenCV and publish target identity, stability and geometric information. |

[Source nodes](catkin_ws/src/event_guide_robot/scripts/) are separated from [semantic and search configuration](catkin_ws/src/event_guide_robot/config/). The search logic waits for navigation to finish before commanding movement. Missing vision dependencies produce a warning rather than fabricated detections.

## Validation and results

The original project documentation records:

- Navigation on a real TurtleBot3 using the supplied map, AMCL and `move_base`.
- Successful resolution of semantic aliases and publication of navigation plans.
- 26 passing unit tests, plus Python, XML and YAML checks, at the documented validation stage.

**Camera/ArUco search and final approach still require validation on the physical robot.** The complete command-to-visual-target sequence is implemented, but an end-to-end hardware demonstration is not established by the current record. The navigation between additional local-search waypoints is also pending.

These are documented project results, not tests rerun during this presentation update.

## Build and run

Use a configured ROS 1 environment with catkin, TurtleBot3 navigation, AMCL, `move_base`, camera support and OpenCV ArUco functionality. The project targets TurtleBot3 Waffle/Waffle Pi.

From the repository root, with the ROS environment sourced:

```bash
cd catkin_ws
catkin_make
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
```

Follow the [real-robot runbook](docs/real-robot-runbook.md) to configure networking, start the robot and camera, and set the initial pose. On physical hardware, use `/use_sim_time=false`.

After bringup, launch the integrated system:

```bash
roslaunch event_guide_robot navigation_with_guide.launch
```

In another terminal with the workspace sourced:

```bash
rostopic pub /guide/command std_msgs/String "data: 'quiero ir al stand de Qualcomm'"
rostopic echo /guide/state
rostopic echo /guide/result
```

The detector expects raw `sensor_msgs/Image` on `/raspicam_node/image`. Marker IDs are defined in the semantic map; the launch defaults to a printed marker size of 0.16 m. Match the configuration to the actual markers before testing visual approach.

## Tests and documentation

From the repository root:

```bash
python3 -m pytest catkin_ws/src/event_guide_robot/test -q
python3 -m py_compile catkin_ws/src/event_guide_robot/scripts/*.py
```

- [Preserved Spanish technical guide](docs/technical-guide-es.md)
- [Real-robot runbook](docs/real-robot-runbook.md)
- [Node explanations](docs/nodes-explanation.md)
- [Semantic labeling guide](docs/semantic-labeling-guide.md)
- [ROS package](catkin_ws/src/event_guide_robot/)

The Spanish guide retains the detailed implementation notes, ROS topics, state transitions, tuning and next steps.

## Project context

This repository preserves the university team's implementation and commit history from [daniupc/event-guide-robot](https://github.com/daniupc/event-guide-robot). This portfolio edition makes the system and its validation status easier to review.
