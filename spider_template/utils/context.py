from threading import Thread


class Pool(object):

    def __init__(self, nums):
        self.nums = nums

    def __call__(self, func):
        def warpper(*args, **kwargs):
            for _ in range(self.nums):
                t = Thread(target=func, args=args, kwargs=kwargs)
                t.start()

        return warpper
