from .server_chan import ServerChan

chan = [ServerChan()]


def notify(title, content):
    for item in chan:
        if not item.deployed():
            continue
        item.send(title, content)
