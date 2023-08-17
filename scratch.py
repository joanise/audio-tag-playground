import music_tag
tag = music_tag.load_file("mp3/01 Politik.mp3")
print(tag)
#tag["artist"] = "foo"
#tag.save()

import taglib
with taglib.File("bad/Kevin Parent/Pigeon d'argile/Unknown Artist-Grand Parleur-01-Track 1_[1].wma", save_on_exit=True) as song:
    print(song.tags)
    del song.tags["TITLE"]
    #song.tags["TITLE"] = ["foo"]
    song.tags["TITLE"] = "La jasette"

with taglib.File("mp3/01 Politik.mp3", save_on_exit=True) as song:
    print(song.tags)
    del song.tags["ARTIST"]
    song.tags["artist"] = "jack"
