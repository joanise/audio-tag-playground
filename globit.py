import os
import taglib
from pathlib import Path


def split_path(path: Path) -> list[str]:
    """Break a file path into all its component directories"""
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
    """Get the song info from the path assuming it's in this format:
       music-library/artist/album/track title.ext
    """
    path_elements = split_path(path)
    info = empty_file_info()
    if path.stem[0:2].isdigit() and path.stem[2:3] == " ":
        info["TRACKNUMBER"] = str(int(path.stem[0:2]))
        info["TITLE"] = path.stem[3:]
    if len(path_elements) >= 4:
        *_, info["ARTIST"], info["ALBUM"], _ = path_elements
    return info


def update_tag(song, tag, value):
    """Update one tag in a pytaglib File song tags"""
    del song.tags[tag]
    song.tags[tag] = [value]


def read_list(filename):
    """Read the white or black list, assuming one file name per line"""
    try:
        with open(filename) as f:
            return [l.rstrip("\n\r") for l in f]
    except:
        return list()
black_list = read_list("whitelist.txt")
white_list = read_list("blacklist.txt")

def append_to_list(list, file):
    """Add a filename to the white and black list"""
    with open(f"{list}list.txt", mode="a") as f:
        print(file, file=f)


def skip_file(file):
    """Return True iff file should be skipped"""
    if split_path(file)[1].startswith("0-"):
        return True
    if str(file) in white_list or str(file) in black_list:
        return True
    try:
        with taglib.File(file):
            pass
    except:
        # Skip every file that taglib can't parse, most likely not music files
        return True
    return False


def has_mismatch(file, file_info, song):
    """Check if anything is mismatched between info inferred from file name and tags"""
    file_printed = False
    mismatch = False
    for f in FIELD_LIST:
        if str(file_info[f]) != str(song.tags[f][0]):
            if not file_printed:
                print(file)
                file_printed = True
            print(f"Mismatched {f}: path: '{file_info[f]}' tags: '{song.tags[f][0]}'")
            mismatch = True
    return mismatch


ACTIONS = {
    "b": "Add to blacklist",
    "w": "Add to whitelist",
    "t": "Update tags",
    "T": "Update tags and add to whitelist",
    "p": "Update file path",
    "P": "Update file path and add to whitelist",
    ".": "Do nothing",
    "q": "Quit program",
}
def prompt_user():
    for k, v in ACTIONS.items():
        print(f"{k}: {v}")
    choice = input("Choose action: [.] ")
    if choice == "":
        choice = "."
    if choice in ACTIONS:
        return choice
    else:
        print("Invalid choice")
        return prompt_user()

def confirm():
    answer = input("Proceed (y/n)? [y] ")
    return answer == "" or answer[0].lower() == "y"


def print_tags(song):
    """Print the tags, but only the ones we care about"""
    print({f: song.tags[f] for f in FIELD_LIST})


def main():
    # MUSIC_LIBRARY = "bad"
    # MUSIC_LIBRARY = "c:\\users\\sylva\\Music"
    MUSIC_LIBRARY = "c:\\users\\joanise\\sandboxes\\mp3edit\\bad"
    for file in Path(MUSIC_LIBRARY).glob("**/*.*"):
        if skip_file(file):
            continue
        file_info = infer_from_path(file)
        try:
            song = taglib.File(file)

            if not has_mismatch(file, file_info, song):
                continue

            user_choice = prompt_user()
            if user_choice == "b":
                append_to_list("black", file)
            elif user_choice == "w":
                append_to_list("white", file)
            elif user_choice.lower() == "t":
                print_tags(song)
                print(f"==== Action: update tags to {file_info}")
                if confirm():
                    for f in FIELD_LIST:
                        update_tag(song, f, file_info[f])
                    song.save()
                    print("Tags updated")
                if user_choice == user_choice.upper():
                    append_to_list("white", file)
            elif user_choice.lower() == "p":
                new_file_name = "%02d %s%s" % (int(song.tags["TRACKNUMBER"][0]), song.tags["TITLE"][0], file.suffix)
                print(f"==== Action: rename file to '{new_file_name}'")
                if confirm():
                    song.close()
                    try:
                        os.rename(file, file.parent / new_file_name)
                        print("File renamed")
                    except Exception as e:
                        print(f"Failed: {e}")
                # print(f"==== Action: move file to '{MUSIC_LIBRARY}\\{song.tags['ARTIST'][0]}\\{song.tags['ALBUM'][0]}")
                if user_choice == user_choice.upper():
                    append_to_list("white", file)
            elif user_choice == ".":
                pass
            else:
                break

        finally:
            # We have to use try/finally because the context manage variant breaks if we close the file
            # inside the with statement, which we need to do before calling os.rename() in the "p" option.
            try:
                song.close()
            except ValueError:
                pass  # we really don't care if it got closed twice


if __name__ == "__main__":
    main()
