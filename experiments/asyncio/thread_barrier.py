import sys
from threading import Thread, Barrier
import logging
import time

class WaitOnBarrierThread(Thread):

    def __init__(
            self,
            num,
            barrier: Barrier,
        ):
        super().__init__()
        self.num = num
        self.barrier = barrier
        self.log = logging.getLogger(f'nbw')

    def run(self):
        self.barrier.wait()
        for n in range(self.num):
            self.log.info(n)
            time.sleep(.2)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(threadName)10s %(name)18s: %(message)s',
        stream=sys.stderr,
    )

    main_barrier = Barrier(2)

    log = logging.getLogger('main')
    log.info('Before calling WaitOnBarrierThread')
    log.info(f'Num threads behind barrier: {main_barrier.n_waiting}')
    WaitOnBarrierThread(10, main_barrier).start()
    log.info(f'Num threads behind barrier: {main_barrier.n_waiting}')
    WaitOnBarrierThread(10, main_barrier).start()
    log.info(f'Num threads behind barrier: {main_barrier.n_waiting}')
    log.info('After calling WaitOnBarrierThread')

