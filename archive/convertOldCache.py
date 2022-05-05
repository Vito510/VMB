import os
import cache


x = os.listdir("cache/playlist")

for i in range(0,len(x)):
    x[i] = x[i].replace("-title.txt","").replace("-url.txt","")


for i in range(0,len(x),2):
    with open("cache/playlist/"+x[i]+"-title.txt", "r", encoding="utf-8") as f:
        title = f.readlines()

    with open("cache/playlist/"+x[i]+"-url.txt", "r", encoding="utf-8") as f:
        urls = f.readlines()

    for j in range(0,len(urls)):
        urls[j] = urls[j].replace("\n","")

    for j in range(0,len(title)):
        title[j] = title[j].replace("\n","")

    cache.save(x[i],urls,title,1)



