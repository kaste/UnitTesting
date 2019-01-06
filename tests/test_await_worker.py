from functools import partial
import time

import sublime

from unittesting import DeferrableTestCase, AWAIT_WORKER


def run_in_worker(fn, *args, **kwargs):
    sublime.set_timeout_async(partial(fn, *args, **kwargs))


class TestAwaitingWorkerInDeferredTestCase(DeferrableTestCase):

    def test_ensure_plain_yield_is_faster_than_the_worker_thread(self):
        messages = []
        TIME_FOR_WORK = 2

        def work(message, worktime=None):
            # simulate that a task might take some time
            # this will not yield back but block
            if worktime:
                time.sleep(worktime)

            messages.append(message)

        run_in_worker(work, 1, TIME_FOR_WORK)

        start = time.time()
        yield

        self.assertEqual(messages, [])

        yield lambda: len(messages) > 0
        end = time.time()

        print('awaiting took {}'.format(end - start))
        self.assertTrue(end - start > TIME_FOR_WORK)

    def test_await_worker(self):
        messages = []
        TIME_FOR_WORK = 1

        def work(message, worktime=None):
            # simulate that a task might take some time
            # this will not yield back but block
            if worktime:
                time.sleep(worktime)

            messages.append(message)

        run_in_worker(work, 1, TIME_FOR_WORK)

        start = time.time()
        yield AWAIT_WORKER
        end = time.time()

        print('awaiting took {}'.format(end - start))

        self.assertEqual(messages, [1])
        self.assertTrue(end - start > TIME_FOR_WORK)
