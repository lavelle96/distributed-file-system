

def format_file_req(file_name, port_number):
    url = 'http://localhost:' + str(port_number) + '/api/files/' + file_name
    return url

def format_node_req(port_number, dir_port_number):
    url = 'http://localhost:' + str(dir_port_number) + '/api/node/' + str(port_number)
    return url

def format_lock_req(file_name, uuid, lock_port_number):
    url = 'http://localhost:' + str(lock_port_number) + '/api/lock/' + file_name + '/' + str(uuid)
    return url

def format_registry_req(dir_name, reg_port_number):
    url = 'http://localhost:' + str(reg_port_number) + '/api/dirs/' + dir_name
    return url

def format_ports_req(dir_name, dir_port_number):
    url = 'http://localhost:' + str(dir_port_number) + '/api/ports/' + dir_name
    return url

def format_replication_req(rep_port_num):
    url = 'http://localhost:' + str(rep_port_num) + '/api/replicate'
    return url