import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 1
worker_class = "sync"  # Use sync workers for better stability
threads = 1
timeout = 120
loglevel = 'debug'
accesslog = '-'  
errorlog = '-'
preload_app = True  # Preload app before forking workers
max_requests = 1000
max_requests_jitter = 100