import re
import taglib
from pathlib import Path

def split_path(path: Path) -> list[str]:
    if str(path) == ".":
        return list()
    if path.parent == path:
        return [str(path)]
    else:
        return split_path(path.parent) + [path.name]

FIELD_LIST = ("ARTIST", "ALBUM", "TRACKNUMBER", "TITLE")
def empty_file_info() -> dict:
    return {f: "" for f in FIELD_LIST}

def infer_from_path(path: Path) -> dict:
    path_elements = split_path(path)
    info = empty_file_info()
    if file.stem[0:2].isdigit() and file.stem[2:3] == " ":
        info["TRACKNUMBER"] = str(int(file.stem[0:2]))
        info["TITLE"] = file.stem[3:]
    if len(path_elements) == 4:
        _, info["ARTIST"], info["ALBUM"], _ = path_elements
    return info

def looks_like_missing_tags(file_info, tags) -> bool:
    return (
       tags["ARTIST"][0] == "Unknown artist" and
       file_info["ARTIST"] != "" and
       tags["ALBUM"][0].startswith("Unknown album") and
       file_info["ALBUM"] != "" and
       re.fullmatch(r"\d\d*", file_info["TRACKNUMBER"]) and
       file_info["TITLE"] != ""
    )
    
def looks_like_only_filename_is_wrong(file_info, tags) -> bool:
    return (
        tags["ARTIST"][0] == file_info["ARTIST"] and
        tags["ALBUM"][0] == file_info["ALBUM"] and
        file_info["TRACKNUMBER"] == "" and
        tags["TRACKNUMBER"][0] != "" and
        file_info["TITLE"] == "" and
        tags["TITLE"][0] != ""
    )

def update_tag(song, tag, value):
    del song.tags[tag]
    song.tags[tag] = [value]

for file in Path("bad").glob("**/*.*"):
    if file.name == "desktop.ini": continue
    print(file)
    file_info = infer_from_path(file)
    with taglib.File(file) as song:

        for f in FIELD_LIST:
            if str(file_info[f]) != str(song.tags[f][0]):
                print(f"Mismatched {f}: path: '{file_info[f]}' tags: '{song.tags[f][0]}'")

        # case 1: info from path looks ok but not info from tags
        if looks_like_missing_tags(file_info, song.tags):
            print(f"==== Action: update tags from filename and path to {file_info}")
            print(song.tags)
            update_tag(song, "TITLE", file_info["TITLE"])
            update_tag(song, "TRACKNUMBER", file_info["TRACKNUMBER"])
            print(song.tags)

        # case 2: filename only is wrong
        elif looks_like_only_filename_is_wrong(file_info, song.tags):
            new_file_name = "%02d %s%s" % (int(song.tags["TRACKNUMBER"][0]), song.tags["TITLE"][0], file.suffix)
            print(f"==== Action: rename file to '{new_file_name}'")
