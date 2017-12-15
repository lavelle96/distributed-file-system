from format import format_state_request

import config as cf
import requests
url_1 = format_state_request(cf.server_port_1)
url_2 = format_state_request(cf.server_port_2)
url_3 = format_state_request(cf.server_port_3)
url_4 = format_state_request(cf.server_port_4)
requests.delete(url_1)
requests.delete(url_2)
requests.delete(url_3)
requests.delete(url_4)