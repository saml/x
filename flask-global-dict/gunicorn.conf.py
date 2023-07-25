bind = "0.0.0.0:5000"
forwarded_allow_ips = "*"
accesslog = '-'
access_log_format = 'gunicorn %({x-forwarded-for}i)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
timeout = 120
workers = 2