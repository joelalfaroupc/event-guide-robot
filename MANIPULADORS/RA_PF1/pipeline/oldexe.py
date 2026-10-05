#!/usr/bin/env python3
"""Run the full pipeline and execute the resulting robot trajectory."""

from __future__ import annotations

import argparse
import socket
import subprocess
import time
from pathlib import Path

from update_problem_goal import update_problem
from battery_check import analyze_batteries

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = Path(__file__).resolve().parent

SCENARIO_DIR = (
    WORKSPACE_ROOT
    / "RA_PF1"
    / "battery_replacer"
)
TASKFILE_PATH = SCENARIO_DIR / "taskfile_tampconfig_batteryreplacer.xml"
TEST_TASKFILE = WORKSPACE_ROOT / "RA_PF1" / "unk_unk.xml"
PARSE_SCRIPT = PIPELINE_DIR / "parse_taskfile.py"
PATHS_FILE = PIPELINE_DIR / "paths.py"

# Robot connection settings
HOST = "10.10.73.236"
PORT = 30002
DASHBOARD_PORT = 29999

# Gripper scripts
ABRIR_PINZA = PIPELINE_DIR / "pinza40UR3.py"
CERRAR_PINZA = PIPELINE_DIR / "pinza10UR3.py"

def send_joint_path(path, sock):
    for joint_config in path:
        # print(joint_config)
        sock.send(f"movej({joint_config}, a=0.5, v=0.5)".encode() + "\n".encode())
        time.sleep(1)


def run_ros2_launch() -> None:
    subprocess.run(
        [
            "ros2",
            "launch",
            "ktmpb_client",
            "ktmpb_full.launch.py",
            "models_folder_path:=/usr/share/kautham/demos/models",
            f"scenario_folder_path:={SCENARIO_DIR}",
            "tamp_config_filename:=tampconfig_batteryreplacer.xml",
        ],
        check=True,
        cwd=WORKSPACE_ROOT,
    )


def generate_paths(taskfile_path) -> None:
    result = subprocess.run(
        ["python3", str(PARSE_SCRIPT), str(taskfile_path), "--pretty"],
        check=True,
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    PATHS_FILE.write_text(result.stdout, encoding="utf-8")


def load_sequence():
    data = {}
    exec(PATHS_FILE.read_text(encoding="utf-8"), data)
    return data["sequence"]


def execute_sequence(sequence) -> None:
    if not sequence:
        print("Batteries are good.No sequence to execute.")
        return
    print("Ejecutando trayectoria...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    # Conexión via socket al Dashboard Server del robot
    dash_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dash_sock.connect((HOST, DASHBOARD_PORT))


    for item in range(len(sequence)):
        send_joint_path(sequence[item]["confs"], sock)
        if item < len(sequence) - 1:
            if sequence[item + 1]["type"] == "transfer":
                with open(CERRAR_PINZA, "rb") as f:
                    sock.sendall(f.read())
            else:
                with open(ABRIR_PINZA, "rb") as f:
                    sock.sendall(f.read())
        time.sleep(3)




    print("Trayectoria finalizada")
    sock.recv(1024)
    sock.close()


def main() -> int:
    VALID_STATUSES = ["unknown", "good", "defective"]

    parser = argparse.ArgumentParser(
        description="Update problem init block based on battery position statuses."
    )
    parser.add_argument(
        "pos1", 
        choices=VALID_STATUSES, 
        help="Status of pos1: unknown, good, or defective"
    )
    parser.add_argument(
        "pos2", 
        choices=VALID_STATUSES, 
        help="Status of pos2: unknown, good, or defective"
    )
    parser.add_argument(
        "--skip-execution",
        action="store_true",
        help="Skip robot execution of the generated sequence",
    )   
    parser.add_argument(
        "--skip-pddl-ros2",
        action="store_true",
        help="Skip PDDL generation and ROS2 launch",
    )
    parser.add_argument(
        "--use_battery_check",
        action="store_true",
        help="Skip camera battery check and use provided statuses",
    )
    parser.add_argument(
        "--only-move-robot",
        action="store_true",
        help="Skip path generation and execution, just apply the sequence to the robot",
    )
    args = parser.parse_args()

    # decide the statuses of pos1 and pos2 based on camera analysis or provided arguments
    if args.use_battery_check:
        pos1, pos2 = analyze_batteries()
        print(f"Camera analysis results: pos1={pos1}, pos2={pos2}")
    else:
        pos1, pos2 = args.pos1, args.pos2
        print(f"Using provided statuses: pos1={pos1}, pos2={pos2}")
    

    # problem modeling in pddl and ros2 launch 
    if not args.skip_pddl_ros2:
        update_problem(args.pos1, args.pos2)
        run_ros2_launch()
        # print the content on sas_plan on src folder
        print("\n=========================\nCONTENT OF SAS_PLAN:")
        print((WORKSPACE_ROOT / "sas_plan").read_text(encoding="utf-8"),end="")
        print("=========================\n")
        generate_paths(TASKFILE_PATH)
    else:
        print("Skipping PDDL generation and ROS2 launch as per user request.")
        generate_paths(TEST_TASKFILE) 
        # as ros2 launch is skipped, we generate path from the desired test taskfile instead of the one generated by ros2 launch


    # execute the generated sequence on the robot unless --skip-execution is specified
    if not args.skip_execution:
        sequence = load_sequence()
        # print("Loaded sequence:", sequence)
        # print the number of steps in each type
        for item in sequence:
            print(f"Type: {item['type']}, Number of steps: {len(item['confs'])}")
        execute_sequence(sequence)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())