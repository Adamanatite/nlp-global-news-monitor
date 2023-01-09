import eel

@eel.expose
def get_no_sources():
    return 206

eel.init('interface')
eel.start('index.html')