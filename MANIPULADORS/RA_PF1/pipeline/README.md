executar-ho tot fora de visual studio, en una terminal apart

executar els següents commands a la carpeta ws_tamp/src

(només el primer cop que s'entra)
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc

(cada cop que s'entra a la terminal)
colcon build --symlink-install
source install/setup.bash

el exe també s'ha dexecutar a la mateixa terminal on s'ha fet el colcon