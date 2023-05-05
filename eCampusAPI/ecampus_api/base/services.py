
# Get hostname

def get_hostname(request):
    http_protocal = request.is_secure() and 'https' or 'http'
    hostname = http_protocal + "://"  + request.get_host()
    return hostname