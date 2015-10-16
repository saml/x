from celeryexample.tasks import app
from celeryexample import configure_logging

if __name__ == '__main__':
    configure_logging()
    app.worker_main()
