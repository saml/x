from celeryexample.tasks import app

if __name__ == '__main__':
    app.worker_main()
