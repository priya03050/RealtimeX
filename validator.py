def is_valid_ws_handshake_request(method, http_version, headers_map):
    is_get = method == 'GET'
    http_version_number = float(http_version.split('/')[1])
    http_version_enough = http_version_number >= 1.1
    headers_valid = (
        ('upgrade' in headers_map and
         headers_map.get('upgrade') == 'websocket') and
        ('connection' in headers_map and
         headers_map.get('connection') == 'Upgrade') and
        ('sec-websocket-key' in headers_map)
    )
    return (is_get and http_version_enough and headers_valid)