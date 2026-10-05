# Event Guide Robot & Battery Manipulation

**A complete university robotics delivery combining a TurtleBot3 event guide with UR3 battery replacement.**

The mobile robot resolves a requested stand into a semantic navigation goal, navigates with `move_base`, and searches for the target ArUco marker. The manipulation project combines PDDL task planning, Kautham/OMPL motion planning and a UR3 execution pipeline for handling battery states.

This repository now contains the supplied **`ENTREGABLE_RA_PF` delivery**: separate real and simulated mobile-robot packages, the manipulation project, the group presentation and **eight original demonstration videos**. All 108 delivery files are preserved byte for byte; nested Git metadata and generated system caches are excluded. The previous edition remains in Git history.

## Explore the delivery

| Part | Contents | Entry point |
| --- | --- | --- |
| Mobile robot · real environment | Four ROS nodes, measured semantic map, navigation/search configuration, launch files and five recordings | [Real-robot guide](MO%CC%80BIL/ENTORN_REAL/README.md) |
| Mobile robot · Gazebo | ROS package, asymmetric fair world, eight marker models, maps, configuration, tests and a simulation recording | [Gazebo guide](MO%CC%80BIL/SIMULACIO_GAZEBO/README) |
| Manipulators · UR3 / Kautham | Battery-replacement scenarios, PDDL domain/problem, motion-planning configuration, Python pipeline, URScript gripper programs and two recordings | [Manipulation guide](MANIPULADORS/RA_PF1/README.md) |
| Group presentation | Twelve slides covering both problems, system flow, topics, planning and demos | [Presentation](Presentacio%CC%81.pdf) |

## Mobile robot: semantic navigation and visual search

```text
Stand command → semantic planner → navigation manager → move_base
                       ↓                  ↓ navigation succeeds
                 Target marker → local search manager → /cmd_vel
                                       ↑
Camera → ArUco detector → stable target detections
```

Four nodes separate command resolution, navigation, local search and perception. Four zones contain eight stands, including Qualcomm, Nokia and NVIDIA. Stand names are matched against configured aliases; the supplied implementation does not require a language model. The real and simulated semantic maps use different coordinates.

The system publishes `/guide/command`, `/guide/plan`, `/guide/state`, `/guide/result` and `/vision/detections`. The local search coordinates rotation, target centering and final approach after global navigation succeeds. Camera topics and search parameters are configurable.

**Use separate catkin workspaces for the real and Gazebo versions:** both directories define the same `event_guide_robot` package. Copy only the selected package into a ROS 1 workspace's `src/`, build it, source its environment and follow that version's original guide. Gazebo targets ROS Noetic and TurtleBot3 Waffle Pi; the real-robot guide describes its own bringup and networking. Check the selected launch file's camera topic against the actual camera setup.

## Manipulators: battery replacement

The manipulation delivery models two battery positions with `unknown`, `good` or `defective` states. The PDDL domain supplies `pick` and `place` actions; scenarios represent keeping correct batteries, replacing defective ones and filling a missing position. Kautham/OMPL provides motion planning, with RRT, RRT* and RRTConnect configuration files included.

[RA_PF1](MANIPULADORS/RA_PF1) belongs inside the `src/` folder of the existing ROS 2 Jazzy / Kautham workspace described by the original guide. It requires the external planning packages and Kautham model library. Its entry point is `RA_PF1/pipeline/exe.py <pos1> <pos2>`; `--skip-execution` skips sending the resulting sequence to the robot. The source retains the laboratory network address and workspace assumptions, which need to match a real deployment. The two `pinza*UR3.py` files contain **URScript**, despite their `.py` extension.

## Demonstration recordings

The following are original recordings supplied with the delivery, grouped by their source folders. Their presence is separate from a new execution or an end-to-end hardware certification.

| Recording | Environment | Original size |
| --- | --- | --- |
| [RA Manipuladors](MANIPULADORS/VIDEOS_DEMO/ENTORN_REAL/RA%20Manipuladors.mp4) | Manipulators · real | 89.3 MB |
| [RA Manipuladors Kautham](MANIPULADORS/VIDEOS_DEMO/SIMULACIO_KAUTHAM/RA%20Manipuladors%20Kautham.mp4) | Manipulators · Kautham | 2.2 MB |
| [Qualcomm_a_nokia](MO%CC%80BIL/ENTORN_REAL/VIDEOS_DEMO/MAPA_REAL/Qualcomm_a_nokia.mov) | Mobile · real | 57.3 MB |
| [Stand_Qualcomm](MO%CC%80BIL/ENTORN_REAL/VIDEOS_DEMO/MAPA_REAL/Stand_Qualcomm.mov) | Mobile · real | 46.2 MB |
| [Stand_nokia](MO%CC%80BIL/ENTORN_REAL/VIDEOS_DEMO/MAPA_REAL/Stand_nokia.mov) | Mobile · real | 51.1 MB |
| [Video_Stand_Nokia_RVIZ](MO%CC%80BIL/ENTORN_REAL/VIDEOS_DEMO/RVIZ/Video_Stand_Nokia_RVIZ.mp4) | Mobile · RViz | 201.0 MB |
| [Video_Stand_Qualcomm_RVIZ](MO%CC%80BIL/ENTORN_REAL/VIDEOS_DEMO/RVIZ/Video_Stand_Qualcomm_RVIZ.mp4) | Mobile · RViz | 169.2 MB |
| [simulacio_mobil](MO%CC%80BIL/SIMULACIO_GAZEBO/VIDEOS_DEMO/simulacio_mobil.mp4) | Mobile · Gazebo | 80.2 MB |

All eight videos use **Git LFS** so the original files remain complete, including the two larger than GitHub's regular-file limit. To retrieve them, install Git LFS before cloning, or run `git lfs pull` in an existing clone. GitHub-generated ZIP downloads may contain LFS pointers instead of videos; use an LFS-enabled clone for the full delivery. SHA-256 hashes and original byte sizes are recorded in the [delivery manifest](docs/delivery-manifest.json).

## Import checks and known limitations

The import checks confirmed all 108 source-file hashes, Python syntax for 23 actual Python files, 32 valid XML-family files, seven YAML files and three map-image references. The supplied mobile unit suite produced **33 passed and one failed**:

- `test_resolves_user_request_to_stand_and_zone` expects `nav_goal.x = -0.529138445854187`, while the delivered Gazebo configuration contains `-0.25`.
- `MANIPULADORS/RA_PF1/battery_replacer/connect_rrt.xml` is incomplete: its root `Problem` element is not closed. This alternative configuration does not pass XML parsing.

Both inconsistencies are retained and documented so this import stays faithful to the supplied delivery. Full ROS builds, Gazebo/Kautham execution, camera processing and physical hardware were **not rerun** in the import environment. The recordings do not establish that every code path or configuration was validated. See the [detailed import checks](docs/import-validation.json).

To reproduce the supplied unit suite, install `pytest` and `PyYAML`, then run `python3 -m pytest` against the `test/` directory of the Gazebo `event_guide_robot` package linked above.

## Credits and provenance

The group presentation credits **Joel Alfaro, Andreu López, Oriol Martí, Daniel Pastor and Elies Aragonès — Grup 3**. These credits describe the collective academic delivery; this portfolio does not assign individual contributions.

The mobile project's existing history comes from [daniupc/event-guide-robot](https://github.com/daniupc/event-guide-robot) and is preserved. The original Catalan/English guides, presentation, source files and media remain in their delivery structure. License declarations within the mobile package manifests are preserved; no additional license is assigned to the complete combined delivery.
