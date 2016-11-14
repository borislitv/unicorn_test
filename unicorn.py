#!/usr/bin/env python

from cocaine.services import Service
from random import randint
from tornado import gen
from cocaine.worker import Worker
import msgpack

DEFAULT_HEADERS = [('Content-type', 'text/plain')]

unicorn = Service("unicorn")
node = "/unicorn_test/" + str(randint(0,100500))

@gen.coroutine
def create_delete_node(unicorn, data, response):
    node = "/unicorn_test/" + str(randint(0,100500))
    #response.write("Create node " + str(node) + "\n")
    try:
        chan = yield unicorn.create(node,str(data))
        result_put = yield chan.rx.get()
        yield chan.tx.close()
    except:
        chan = yield unicorn.get(node)
        result = yield chan.rx.get()
        yield chan.tx.close()
        chan = yield unicorn.put(node,str(data),result[1])
        result_put = yield chan.rx.get()
        yield chan.tx.close()

    #response.write("Get node " + str(node) + "\n")
    chan = yield unicorn.get(node)
    result = yield chan.rx.get()
    yield chan.tx.close()

    #response.write("Remove node " + str(node) + "\n")
    chan = yield unicorn.remove(node,result[1])
    result_remove = yield chan.rx.get()
    yield chan.tx.close()

def unicorn_tank(request, response):
    req = yield request.read()
    r = msgpack.unpackb(req)
    get = r[1].split("/")[1].split("_")
    size = int(get[0])
    count = int(get[1])
    f = open('/dev/urandom', 'rb')
    data = f.read(size*1024)

    response.write(msgpack.packb((200, DEFAULT_HEADERS)))
    #response.write("Create " + str(count) + " nodes with size: " + str(size) + "kb\n")

    error = 0
    i = 0
    futures = {}
    while i < count:
        i = i + 1
        futures[str(i)] = create_delete_node(unicorn, data, response)

    wait_iterator = gen.WaitIterator(**futures)
    while not wait_iterator.done():
        try:
            yield wait_iterator.next()
            #response.write(str(wait_iterator.current_index) + " done\n")
        except:
            error = error + 1
            #response.write(str(wait_iterator.current_index) + " failed\n")

    if error == 0:
        response.write(msgpack.packb((200, DEFAULT_HEADERS)))
    else:
        response.write(msgpack.packb((500, DEFAULT_HEADERS)))

    response.close()

def main():
    w = Worker()
    w.run({"http": unicorn_tank})

if __name__ == "__main__":
    main()
