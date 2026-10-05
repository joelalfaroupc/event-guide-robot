from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.substitutions import FindPackageShare
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os


def launch_setup(context, *args, **kwargs):

    included_ktmpb_base_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare("ktmpb_client"),
                'launch',
                'ktmpb_base.launch.py'
            ])
        ]),
        launch_arguments={
            'tamp_config_filename': LaunchConfiguration('tamp_config_filename'),
            'rviz_config_file_path': LaunchConfiguration('rviz_config_file_path'),
        }.items()
    )

    return [
        included_ktmpb_base_launch,
    ]


def generate_launch_description():
    declared_arguments = []
    
    declared_arguments.append(
        DeclareLaunchArgument(
            'tamp_config_filename',
            default_value="OMPL_geometric_demos/chess_ur3_robotiq/tampconfig_chess_2_simple.xml",
            description='Launches the ktmpb client with the files set in the tampconfig file.',
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            'rviz_config_file_path',
            default_value=PathJoinSubstitution([
                    FindPackageShare("ktmpb_demos"),
                    'OMPL_geometric_demos/chess_ur3_robotiq/rviz',
                    'kautham_chess_2_simple.rviz'
                ]),
            description='Launches the ktmpb client with the RVIZ configuration file.',
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])