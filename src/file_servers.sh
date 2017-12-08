#!/bin/bash
source config.cfg
python File_Server.py "$server_port_1" 'FS_1' &
python File_Server.py "$server_port_2" 'FS_2' &
python File_Server.py "$server_port_3" 'FS_3' &
python File_Server.py "$server_port_4" 'FS_4' 
