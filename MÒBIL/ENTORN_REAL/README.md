
## Requisits

- ROS 1 amb workspace `catkin_ws`.
- TurtleBot3 Waffle configurat.
- Paquets de navegacio de TurtleBot3 disponibles.
- Camera del robot publicant imatges.
- El PC i el robot han d'estar a la mateixa xarxa.
- Les variables de ROS han d'apuntar correctament al PC que fa de master.

En els exemples seguents:

- `IP_PC` es la IP del portatil/PC que executa `roscore` i la navegacio.
- `IP_ROBOT` es la IP del TurtleBot3.

## Preparacio del workspace

En una terminal del PC:

```bash
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

Si el paquet no es troba, comprova que esta dins de:

```bash
~/catkin_ws/src/event_guide_robot
```

## Configuracio de xarxa ROS

Al PC, el `.bashrc` ha de tenir el master apuntant al mateix PC:

```bash
export ROS_MASTER_URI=http://IP_PC:11311
export ROS_IP=IP_PC
```

Al robot, connectant per SSH, el `.bashrc` ha d'apuntar al master del PC:

```bash
export ROS_MASTER_URI=http://IP_PC:11311
export ROS_IP=IP_ROBOT
```

Despres de canviar el `.bashrc`, cal aplicar-lo:

```bash
source ~/.bashrc
```

Important: cada terminal nova ha de tenir aquestes variables carregades. Si alguna cosa no connecta, comprova primer `ROS_MASTER_URI` i `ROS_IP`.

## Llançament en robot real

Cal mantenir diverses terminals obertes alhora, perque tots aquests processos han d'estar corrent simultaniament.

### Terminal 1 - PC: ROS master

```bash
source ~/catkin_ws/devel/setup.bash
roscore
```

Aquesta terminal ha de quedar oberta. Es el nucli de comunicacio de ROS.

### Terminal 2 - Robot per SSH: bringup del TurtleBot3

Des del PC:

```bash
ssh ubuntu@IP_ROBOT
source ~/.bashrc
roslaunch turtlebot3_bringup turtlebot3_robot.launch
```

Aixo arrenca la base del robot, sensors principals i comunicacio amb la placa del TurtleBot3.

### Terminal 3 - Robot per SSH: camera

En una altra connexio SSH al robot:

```bash
ssh ubuntu@IP_ROBOT
source ~/.bashrc
roslaunch turtlebot3_bringup turtlebot3_rpicamera.launch
```

Aixo ha de publicar el topic d'imatge de la camera. En el nostre cas, per al llançament del paquet fem servir:

```text
/camera/image
```

Si la camera publica en un altre topic, cal canviar el parametre `image_topic`.

### Terminal 4 - PC: navegacio i sistema guia

En el PC:

```bash
source ~/catkin_ws/devel/setup.bash
roslaunch event_guide_robot navigation_with_guide.launch image_topic:=/camera/image
```

Aquest launch arrenca dues parts:

- `turtlebot3_navigation.launch`, que carrega el mapa i `move_base`.
- `guide_system.launch`, que arrenca els nodes propis del paquet:
  - `semantic_planner_node`
  - `navigation_manager_node`
  - `local_search_manager_node`
  - `vision_detector_node`

El fitxer de mapa utilitzat per defecte es:

```text
maps/map.yaml
```

## Terminals de monitoritzacio

Aquestes terminals son opcionals, pero molt recomanables durant la demo.

### Estat general del sistema

```bash
rostopic echo /guide/state
```

Exemples d'estats:

- `PARSE_TARGET`
- `TARGET_RESOLVED`
- `NAVIGATE_TO_ZONE`
- `NAVIGATION_SUCCEEDED`
- `LOCAL_VISUAL_SEARCH`
- `APPROACH_TARGET`
- `FOUND_TARGET`
- `NAVIGATION_FAILED`
- `SEARCH_FAILED`

### Resultats per a l'usuari

```bash
rostopic echo /guide/result
```

Aquest topic mostra missatges com el desti seleccionat, navegacio completada o errors.

### Deteccions visuals

```bash
rostopic echo /vision/detections
```

Aquest topic publica deteccions ArUco en format JSON. Camps habituals:

- `marker_id`: ID numeric del marcador.
- `label_id`: identificador intern del stand.
- `stable`: indica si el marcador s'ha vist durant prou frames consecutius.
- `distance_m`: distancia estimada al marcador.
- `center_offset_x`: desviacio horitzontal del marcador dins la imatge.

## Enviar comandes al robot

Les comandes es publiquen al topic:

```text
/guide/command
```

Exemples:

```bash
rostopic pub -1 /guide/command std_msgs/String "data: 'qualcomm'"
```

```bash
rostopic pub -1 /guide/command std_msgs/String "data: 'nokia'"
```

```bash
rostopic pub -1 /guide/command std_msgs/String "data: 'ericsson'"
```

```bash
rostopic pub -1 /guide/command std_msgs/String "data: 'nvidia'"
```

També funcionen aliases mes llargs, per exemple:

```bash
rostopic pub -1 /guide/command std_msgs/String "data: 'stand qualcomm'"
rostopic pub -1 /guide/command std_msgs/String "data: 'zona izquierda'"
```

## Destins configurats

Els destins estan definits a:

```text
config/semantic_map.yaml
```

Stands disponibles:

| Stand | Zona | Marker ID |
| --- | --- | --- |
| Qualcomm AI Hub | zona_arriba | 11 |
| Samsung Galaxy Experience | zona_arriba | 12 |
| Telefonica Open Gateway | zona_izquierda | 21 |
| Nokia Networks Lab | zona_izquierda | 22 |
| Ericsson 5G Arena | zona_abajo | 31 |
| GSMA Innovation City | zona_abajo | 32 |
| Meta XR Showcase | zona_derecha | 41 |
| NVIDIA Edge AI | zona_derecha | 42 |

## Que fa el sistema internament

1. `semantic_planner_node` escolta `/guide/command`.
2. Busca el text rebut dins dels aliases de `semantic_map.yaml`.
3. Publica un pla JSON a `/guide/plan` amb zona, stand, coordenades i `marker_id`.
4. `navigation_manager_node` rep el pla i envia un goal a `/move_base`.
5. Quan `move_base` arriba a la zona, es publica `NAVIGATION_SUCCEEDED`.
6. `local_search_manager_node` comença la cerca local i gira el robot amb `/cmd_vel`.
7. `vision_detector_node` detecta marcadors ArUco a partir de la camera.
8. Quan es detecta el marcador correcte de forma estable, el robot s'hi acosta lentament.
9. Quan arriba a la distancia objectiu, publica `FOUND_TARGET`.
