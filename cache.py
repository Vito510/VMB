import datetime
import json
import logging

import click


def timestamp():
    now = datetime.datetime.now()
    return ('['+str(now.hour)+':'+str(now.minute)+':'+str(now.second)+'] ')

def clear(age):
    '''Clears cache older than age(days)'''
    d_count = 0
    with open('cache/playlist.json') as f:
        data = json.load(f)

    for item in data:
        if get_age_in_days(data[item]) > age:
            del data[item]
            d_count += 1

    with open('cache/playlist.json', 'w') as f:
        json.dump(data, f, indent=4)

    
    with open('cache/search.json') as f:
        data = json.load(f)

    for item in data:
        if get_age_in_days(data[item]) > age:
            del data[item]
            d_count += 1
        
    with open('cache/search.json', 'w') as f:
        json.dump(data, f, indent=4)


    click.echo(timestamp()+"cache.clear() - Cleared "+str(d_count)+" items from cache")

def get_age_in_days(data):
    now = datetime.datetime.now()
    created_at = datetime.datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
    age_in_days = (now - created_at).days
    return age_in_days

def save(x,url,title,t):
    click.echo(timestamp()+"cache.save() - Writing to cache")
    logging.info("cache.save() - Writing to cache")

    d = {}

    if t == 0:
        path = 'cache/search.json'
    elif t == 1:
        path = 'cache/playlist.json'

    try:
        with open(path) as f:
            data = json.load(f)
    except:
        data = {}
    
    d["url"] = url
    d["title"] = title
    d["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data[x] = d
        
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def load(x,t):
    '''Loads cache from file'''
    if t == 0:
        path = 'cache/search.json'
    elif t == 1:
        path = 'cache/playlist.json'

    with open(path) as f:
        data = json.load(f)
        if x in data:
            click.echo(timestamp()+"cache.load() - Reading from cache")
            logging.info("cache.load() - Reading from cache")
            return data[x]
        else:
            return None


# u = "https://www.youtube.com/watch?v=sck4_Vhr-H4"
# t = "gumdrops"
# save("nelward gumdrops",{"url":u,"title":t},0)

# i = "PLmeBqWgbwZgi48Y-VnhmCJbFob06Rc1p8"
# url = [
#         "https://www.youtube.com/watch?v=68LWlLgHzAI","https://www.youtube.com/watch?v=i_-wXT0zERc","https://www.youtube.com/watch?v=sDLsSQf3Hc0","https://www.youtube.com/watch?v=MgXDWIYEV3Y","https://www.youtube.com/watch?v=4Q_qAwTiJ-w","https://www.youtube.com/watch?v=zJKiBZqHO5o"
#     ]

# title = [
#         "smle - It'll Be Okay","smle - Haunted (feat Seann Bowe) (Official Music Video)","SMLE - 2 Me (feat. Kiddo Ai & Nick Smith) [Monstercat Release]","SMLE - Halo (feat. Helen Tess) [Monstercat Release]","WRLD x SMLE - Stranded (feat. Kiddo AI)","smle - Just 5 More Minutes"
#     ]

# save(i,{"url":url,"title":title},1)
