workers = 1
threads = 8
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

accesslog = "-"
errorlog = "-"

bind = ["0.0.0.0:8080"]

reload = True
