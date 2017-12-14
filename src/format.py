def format_file_req(port_number):
    url = 'http://localhost:' + str(port_number) + '/api/file' 
    return url

def format_node_req(port_number, dir_port_number):
    url = 'http://localhost:' + str(dir_port_number) + '/api/node/' + str(port_number)
    return url

def format_lock_req(uuid, lock_port_number):
    url = 'http://localhost:' + str(lock_port_number) + '/api/lock/' + str(uuid)
    return url

def format_registry_req(dir_name, reg_port_number):
    url = 'http://localhost:' + str(reg_port_number) + '/api/dirs/' + dir_name
    return url

def format_ports_req(dir_port_number):
    url = 'http://localhost:' + str(dir_port_number) + '/api/ports' 
    return url

def format_replication_req(rep_port_num):
    url = 'http://localhost:' + str(rep_port_num) + '/api/replicate'
    return url

def format_show_files(dir_port):
    url = 'http://localhost:' + str(dir_port) + '/api/files'
    return url

def format_state_request(server_port):
    url = 'http://localhost:' + str(server_port) + '/api/state'
    return url

def format_version_req(dir_server_port):
    url = 'http://localhost:' + str(dir_server_port) + '/api/version'
    return url
    
  