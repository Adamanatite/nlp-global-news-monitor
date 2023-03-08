import eel

test_list = [1, 2, 3]


@eel.expose
def modify_list():
    test_list[2] += 1

eel.init('dynamic_interface')
eel.start('index.html', blocking=False)

while True:
    for l in test_list:
        print(l)
