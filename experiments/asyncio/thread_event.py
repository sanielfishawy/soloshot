from threading import Thread, Event
import logging
import time
import sys

class EventSenderThread(Thread):

    def __init__(
            self,
    ):
        super().__init__()
        self.is_running_event = Event()
        self.stop_request_event = Event()
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.is_running_event.set()
        for n in range(5):
            self.log.info(n)
            time.sleep(.2)

        self.stop_request_event.wait()

        log.info('Stopping')

class EventWaiterThread(Thread):
    def __init__(
            self,
            wait_on_event: Event,
    ):
        super().__init__()
        self.wait_on_event = wait_on_event

        self.stop_request_event = Event()
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        self.log.info('Waiting on event')
        self.wait_on_event.wait()
        self.log.info('Got event now running')

        for n in range(5):
            self.log.info(n)
            time.sleep(.2)

        self.stop_request_event.wait()

        log.info('Stopping')

if __name__ == '__main__':

    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr,
    )

    event_sender = EventSenderThread()
    event_waiter = EventWaiterThread(
        wait_on_event=event_sender.is_running_event,
    )

    log = logging.getLogger()

    log.info('Starting waiter')
    event_waiter.start()
    time.sleep(1)

    log.info('Starting sender')
    event_sender.start()
    time.sleep(3)

    log.info('Attempting to stop event_sender')
    event_sender.stop_request_event.set()

    log.info('Attempting to stop event_waiter')
    event_waiter.stop_request_event.set()

