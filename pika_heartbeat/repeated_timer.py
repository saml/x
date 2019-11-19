'''
Creates background thread which runs task regularly
'''
from threading import Timer

class RepeatedTimer(object):
    '''
    Class for repeat timer
    '''
    def __init__(self, interval, task, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        '''
        start the timer again and call the function
        '''
        self.is_running = False
        self.start()
        self.task(*self.args, **self.kwargs)

    def start(self):
        '''
        start timer thread
        '''
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        '''
        stop timer thread
        '''
        self._timer.cancel()
        self.is_running = False
