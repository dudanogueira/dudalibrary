from celery import task
from queue.models import ResourceQueue

@task()
def add_resource_to_queue(queue_object_id):
    logger = add_resource_to_queue.get_logger()
    queue = ResourceQueue.objects.get(pk=queue_object_id)
    logger.info(u"Executando Queue %d" % queue.id)
    return queue.run()

@task()
def add(x, y):
    print "Adding..."
    return x + y
    