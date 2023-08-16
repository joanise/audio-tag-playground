import music_tag
import re
import taglib
from tinytag import TinyTag
from pathlib import Path

def split_path(path: Path) -> list[str]:
    if str(path) == ".":
        return list()
    if path.parent == path:
        return [str(path)]
    else:
        return split_path(path.parent) + [path.name]

FIELD_LIST = ("artist", "album", "tracknumber", "tracktitle")
def empty_file_info() -> dict:
    return {f: "" for f in FIELD_LIST}

def infer_from_path(path: Path) -> dict:
    path_elements = split_path(path)
    info = empty_file_info()
    if file.stem[0:2].isdigit() and file.stem[2:3] == " ":
        info["tracknumber"] = str(int(file.stem[0:2]))
        info["tracktitle"] = file.stem[3:]
    if len(path_elements) == 4:
        _, info["artist"], info["album"], _ = path_elements
    return info

def tinytag2musictag(tag):
    return {
        "tracknumber": tag.track,
        "tracktitle": tag.title,
        "album": tag.album,
        "artist": tag.artist,
    }

def looks_like_missing_tags(file_info, tags) -> bool:
    return (
       str(tags["artist"]) == "Unknown artist" and
       file_info["artist"] != "" and
       str(tags["album"]).startswith("Unknown album") and
       file_info["album"] != "" and
       re.fullmatch(r"\d\d*", file_info["tracknumber"]) and
       file_info["tracktitle"] != ""
    )
    
def looks_like_only_filename_is_wrong(file_info, tags) -> bool:
    return (
        str(tags["artist"]) == file_info["artist"] and
        str(tags["album"]) == file_info["album"] and
        file_info["tracknumber"] == "" and
        str(tags["tracknumber"]) != "" and
        file_info["tracktitle"] == "" and
        str(tags["tracktitle"]) != ""
    )

for file in Path("bad").glob("**/*.*"):
    print(file)
    file_info = infer_from_path(file)
    try:
        tags = music_tag.load_file(file)
        writable_tags = True
    except NotImplementedError:
        print(f"{file.suffix} format not supported by music-tag")
        tags = tinytag2musictag(TinyTag.get(file))
        writable_tags = False

    for f in FIELD_LIST:
        if str(file_info[f]) != str(tags[f]):
            print(f"Mismatched {f}: path: '{file_info[f]}' tags: '{tags[f]}'")

    # case 1: info from path looks ok but not info from tags
    if looks_like_missing_tags(file_info, tags):
        print(
            f"==== Action: update tags from filename and path to {file_info}" +
            ("" if writable_tags else " BUT tags not writable")
        )

    # case 2: filename only is wrong
    elif looks_like_only_filename_is_wrong(file_info, tags):
        new_file_name = "%02d %s%s" % (int(tags["tracknumber"]), tags["tracktitle"], file.suffix)
        print(f"==== Action: rename file to '{new_file_name}'")