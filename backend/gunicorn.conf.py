import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 1
worker_class = "sync"
threads = 1
timeout = 120
loglevel = 'info'
accesslog = '-'
errorlog = '-'
preload_app = True