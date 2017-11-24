

def format_file_req(file_name, port_number):
    url = 'http://localhost:' + port_number + '/api/files/' + file_name
    return url

def format_node_req(port_number, dir_port_number):
    url = 'http://localhost:' + str(dir_port_number) + '/api/node/' + str(port_number)
    return url

