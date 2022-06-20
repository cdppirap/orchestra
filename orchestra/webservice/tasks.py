from celery import shared_task

@shared_task
def sleepy(t):
    import time
    t0 = time.time()
    time.sleep(t)
    return time.time() - t0
