# -*- coding: utf-8 -*-
"""
Configuration Gunicorn pour la production (Render.com)
"""

import multiprocessing

# Nombre de workers (auto-adapte selon les ressources)
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5

# Bind sur le port Render (defini par la variable d'env PORT)
import os
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Securite
limit_request_line = 8190
limit_request_fields = 100
