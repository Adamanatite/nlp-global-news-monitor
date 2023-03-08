import eel
import threading

class TestClass:
    def __init__(self, n):
        self.number = n
        self.enabled = True
    def status(self):
        if self.enabled:
            print(self.number)
        else:
            print(self.number, "disabled")

test_list = [TestClass(1), TestClass(2), TestClass(3), TestClass(4), TestClass(5), TestClass(6)]
i = 0

@eel.expose
def get_no_sources():
    return 4

@eel.expose
def modify_list():
    del(test_list[0])
    return test_list

def print_list(t_list):
    while True:
        for l in t_list:
            l.status()
        if event.is_set():
            return

eel.init('dynamic_interface')
event = threading.Event()
t = threading.Thread(target=print_list, args=(test_list,))
t.start()
eel.start('index.html')
event.set()
t.join()
print(test_list)
