import music_tag
tag = music_tag.load_file("mp3/01 Politik.mp3")
print(tag)
tag["artist"] = "foo"
tag.save()

import taglib
with taglib.File("bad/Kevin Parent/Pigeon d'argile/Unknown Artist-Grand Parleur-01-Track 1_[1].wma") as song:
    print(song.tags)
    