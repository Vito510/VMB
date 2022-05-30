# Vito's Music Bot
![image](https://user-images.githubusercontent.com/73427833/166977719-7c24f2a8-5cbe-40ee-b614-76a642f7e279.png)

Vito's music bot is definitely my biggest project to date.

It's another discord music bot BUT it's MINE and I can do with it whatever i want with it.


It contains:
- Youtube playback
- Local file playback
- Youtube playlists support
- Built in youtube search

<h2>Packs</h2>

Have you ever wanted your bot to say inapropriate stuff when joining/leaving a voice channel... Probably not, but now you can using packs!

![PackExample](https://user-images.githubusercontent.com/73427833/170971361-c5270c14-6ce9-43e1-8cf4-c96e7f88660f.png)

Packs allow you to use a text file with lots of different lines you want your bot to say which will then be randomly selected. You can also specify whether the file is for join messages or leave messages

<h3>How to use packs</h3>

- First create a new text file inside the packs folder (automatically created on first bot run)
- Now to the end of the text file name append _I or _O (for example "test_I.txt") this specifies if the file is for IN(join messages) or OUT(leave messages)
- Open the packs.json file (automatically created on first bot run) and add a json entry with 4 keys
- set "JoinLeaveMessages" to true in the config file

```json
{
  "name":"The name of your pack"
  "type":"(I,O,IO)"
  "weight":1
  "dir":"path to the .txt file exclude the _I / _O bit and also remove the extension (.txt)"
}
```

name - Name of your pack, doesen't have to be equal to the text file name

type - This signifies to the bot which files exist (**I** - there is one <name>_I.txt file, **O** - there is one <name>_O.txt file, **IO** - There is both a <name>_I.txt and a <name>_O.txt file)

weight - The precentage of the pack being selected if you add multiple packs. **Make sure that the sum of all weights are 1!**
  
dir - The path of the text files without the _I or _O part and without the extension
  
<h3>Example:</h3>
  
```json
[
    {
        "name": "example",
        "type": "IO",
        "weight": 0.5,
        "dir": "packs/example"
    },
    {
        "name": "example2",
        "type": "O",
        "weight": 0.5,
        "dir": "packs/example2"
    }
]
```
Files inside the pack folder:
  
- [example_I.txt](https://github.com/Vito510/VMB/files/8797688/example_I.txt)
- [example_O.txt](https://github.com/Vito510/VMB/files/8797693/example_O.txt)
- [example2_O.txt](https://github.com/Vito510/VMB/files/8797694/example2_O.txt)

  
