# nav_hub

Pacote ROS 2 que concentra a parte de navegacao baseada no projeto Oregon.

No fluxo atual, o `nav_hub` e usado pelo simulador `sim_bot` como a camada de
navegacao. O `sim_bot` sobe Gazebo, robo, bridge e RViz; o `nav_hub` fornece
Nav2, mapa, grafo, Behavior Tree e speed filter.

Para esse fluxo funcionar, este pacote deve estar no mesmo workspace ROS 2 do
`sim_bot`, por exemplo:

```text
~/sim_ws/src/sim_bot
~/sim_ws/src/nav_hub
```

```text
sim_bot
  -> simulacao
  -> Gazebo
  -> robot_state_publisher
  -> spawn do robo
  -> ros_gz_bridge
  -> RViz

nav_hub
  -> navegacao
  -> Nav2 params
  -> mapa
  -> speed mask
  -> grafo
  -> Behavior Tree
  -> route_server
  -> speed_filter
```

## Integracao Com O sim_bot

O fluxo principal no simulador e:

```text
sim_bot/launch/sim_manager.launch.py
  -> sim_bot/launch/sim_essentials.launch.py
  -> sim_bot/launch/sim_navigation.launch.py
      -> nav_hub/launch/route_graph/sim_nav_graph.launch.py
```

Ou seja, o `sim_bot` nao chama mais um launch proprio de Nav2. Ele chama o
launch de navegacao da simulacao que fica neste pacote:

```text
nav_hub/launch/route_graph/sim_nav_graph.launch.py
```

O arquivo de parametros usado por esse launch e:

```text
nav_hub/config/sim_nav_params.yaml
```

## Arquivos Principais

### Launch De Simulacao

```text
launch/route_graph/sim_nav_graph.launch.py
```

Sobe a pilha Nav2 adaptada para Gazebo:

```text
map_server
amcl
controller_server
smoother_server
planner_server
behavior_server
bt_navigator
waypoint_follower
velocity_smoother
route_server
speed_filter_mask_server
speed_costmap_filter_info_server
lifecycle managers
```

Esse launch e inspirado no `launch/route_graph/nav_graph.launch.py`, mas evita
dependencias de hardware real e usa `use_sim_time:=true`.

### Parametros Nav2

```text
config/sim_nav_params.yaml
```

Define:

```text
BT Navigator
AMCL
map_server
costmaps
controller_server
planner_server
smoother_server
velocity_smoother
route_server
speed_filter
```

Tambem aponta para os arquivos de mapa, grafo e Behavior Tree:

```yaml
default_nav_to_pose_bt_xml: "$(find-pkg-share nav_hub)/btree/nav_on_route_graph_oregon.xml"
yaml_filename: "$(find-pkg-share nav_hub)/maps/aceleradora.yaml"
graph_filepath: "$(find-pkg-share nav_hub)/graphs/aceleradoras.json"
yaml_filename: "$(find-pkg-share nav_hub)/maps/aceleradora_speed_mask.yaml"
```

### Mapa E Mascara De Velocidade

```text
maps/aceleradora.yaml
maps/aceleradora.pgm
maps/aceleradora_speed_mask.yaml
maps/aceleradora_speed_mask.pgm
```

O mapa e usado pelo `map_server`.

A speed mask e usada pelo speed filter do Nav2 para limitar velocidade em regioes
especificas do mapa.

### Grafo De Rotas

```text
graphs/aceleradoras.json
```

Grafo usado pelo `nav2_route/route_server`.

Esse arquivo define os nos e arestas que o robo deve seguir quando o Behavior
Tree usa rota por grafo.

### Behavior Tree

```text
btree/nav_on_route_graph_oregon.xml
```

Behavior Tree usada pelo `bt_navigator` para calcular rota pelo grafo, suavizar
o caminho e mandar o controller seguir.

Fluxo esperado:

```text
RViz 2D Goal Pose
  -> bt_navigator
  -> ComputeRoute
  -> route_server
  -> graphs/aceleradoras.json
  -> SmoothPath
  -> FollowPath
  -> /cmd_vel
```

## Fluxo De Velocidade

O fluxo atual segue o padrao usado na Oregon, passando pelo
`velocity_smoother`:

```text
controller_server
  -> /controller_cmd_vel
  -> velocity_smoother
  -> /cmd_vel
  -> sim_bot/Gazebo
```

No launch:

```text
controller_server
  cmd_vel -> controller_cmd_vel

velocity_smoother
  cmd_vel -> controller_cmd_vel
  cmd_vel_smoothed -> cmd_vel
```

Assim, o controller nao publica direto no comando final do robo. O comando final
em `/cmd_vel` vem do `velocity_smoother`.

## Como Compilar

Na raiz do workspace:

```bash
cd ~/sim_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select nav_hub sim_bot
source install/setup.bash
```

Esse build assume que os dois pacotes estao no mesmo workspace:

```text
src/sim_bot
src/nav_hub
```

## Como Executar Pelo sim_bot

O uso normal deste pacote e por meio do `sim_bot`:

```bash
cd ~/sim_ws
source install/setup.bash
ros2 launch sim_bot sim_manager.launch.py
```

Esse comando sobe o Gazebo pelo `sim_bot` e a navegacao pelo `nav_hub`.

## Como Testar O Launch Do nav_hub Isolado

Para listar os argumentos do launch de navegacao:

```bash
cd ~/sim_ws
source install/setup.bash
ros2 launch ~/sim_ws/install/nav_hub/share/nav_hub/launch/route_graph/sim_nav_graph.launch.py --show-args
```

Observacao: esse launch isolado sobe apenas a navegacao. Para o robo existir no
Gazebo, use o fluxo completo pelo `sim_bot`.

## Visualizar O Grafo No RViz

O visualizador fica no pacote `sim_bot`, mas usa o grafo deste pacote:

```bash
cd ~/sim_ws
source install/setup.bash
ros2 run sim_bot graph_visualizer
```

No RViz:

```text
Add -> By topic -> /route_graph_markers -> MarkerArray
```

Por padrao, o visualizador usa:

```text
nav_hub/graphs/aceleradoras.json
```

## Testar Rota Por ID

O script tambem fica no `sim_bot`, mas chama o `route_server` configurado pelo
`nav_hub`:

```bash
cd ~/sim_ws
source install/setup.bash

ros2 run sim_bot route_to_poses --ros-args \
  -p use_start:=False \
  -p start_id:=1 \
  -p goal_id:=17
```

Esse teste chama:

```text
/compute_route
/follow_path
```

## Estrutura Relevante

```text
nav_hub/
  launch/
    route_graph/
      sim_nav_graph.launch.py   Launch Nav2 adaptado para simulacao.
      nav_graph.launch.py       Launch original/base da Oregon.

  config/
    sim_nav_params.yaml         Parametros Nav2 usados na simulacao.
    nav_routegraph.yaml         Referencia da Oregon.

  maps/
    aceleradora.yaml
    aceleradora.pgm
    aceleradora_speed_mask.yaml
    aceleradora_speed_mask.pgm

  graphs/
    aceleradoras.json

  btree/
    nav_on_route_graph_oregon.xml

  src/
    main_route_graph.cpp
    botoeira_ponto_linear.cpp
    stop_obstacle.cpp
    outros nos de referencia/importacao da Oregon
```

## O Que Ainda Nao Esta Integrado Na Simulacao

Alguns arquivos vieram da estrutura real da Oregon, mas ainda nao sao usados no
fluxo principal da simulacao:

```text
main_route_graph
botoeira_ponto_linear
collision_monitor
controller custom
ground_segmentation_ros2
launches de hardware real
ToF real
canopen real
ldlidar real
```

Esses itens devem ser migrados por etapas, sempre mantendo o fluxo do simulador
funcionando.

## Ordem Recomendada Para Evolucao

1. Manter `sim_nav_graph.launch.py` funcionando como baseline.
2. Comparar `sim_nav_graph.launch.py` com `nav_graph.launch.py`.
3. Aproximar o lifecycle do padrao Oregon.
4. Avaliar integracao do `main_route_graph`.
5. Avaliar `collision_monitor`.
6. Avaliar controller custom.
7. Avaliar `ground_segmentation_ros2` apenas se houver sensor/pointcloud que
   justifique isso na simulacao.
