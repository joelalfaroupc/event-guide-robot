The repository consists of 2 folders. the repo must be cloned inside the src folder of kautham project

to launch the executions, inside a terminal in ws_tamp/src folder, you must execute the following commands:

echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
colcon build --symlink-install
source install/setup.bash

inside that same terminal, you are ready to execute the command:

python3 RA_PF1/pipeline/exe.py <pos1> <pos2>
where pos1 and pos2 represent the state of each of the 2 batteries.



battery_replacer folder contains the problem modulation for kautham and ros2 planner, as well as pddl problem and domain files

pipeline folder contains a diverse number of files that take care of the execution of the whole automatization process, from the 
problem detetion to the planification modulation of the planner and the execution on the real robot
