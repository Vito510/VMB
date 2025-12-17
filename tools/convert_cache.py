import json



path = "./cache/playlist"

data = json.loads(open(path,"r",encoding='utf-8').read())

print(data)