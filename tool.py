import json
def loadcfg():
    with open('./config.json','r') as f:
        return json.load(f)
def savecfg(arg):
    with open('./config.json', 'w') as f:
        json.dump(arg, f)