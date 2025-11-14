import os

# Railway-specific Gunicorn configuration
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
workers = 1
worker_class = "sync"
threads = 2
timeout = 120
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "ai-chat-memory"

# Server mechanics
preload_app = True
max_requests = 1000
max_requests_jitter = 100