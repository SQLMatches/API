from os import walk
from os.path import join, realpath, dirname


CURRENT_DIR = dirname(realpath(__file__))

ENCODING = "utf-8"

IGNORE = [
    ".git",
    ".github",
    "build",
    "dist",
    "nginx",
    "SQLMatches.egg-info",
    ".env"
]


def loop_and_replace(pathway: str = ""):
    if pathway:
        pathway = join(CURRENT_DIR, pathway)
    else:
        pathway = CURRENT_DIR

    for root, directories, files in walk(pathway):
        for dir in directories:
            loop_and_replace(dir)

        for file_ in files:
            if file_ not in IGNORE and ".py" in file_ and ".pyc" not in file_:
                with open(join(root, file_), "r", encoding=ENCODING) as f_:
                    text = f_.read().replace("2020-2021", "2020-2021")

                with open(join(root, file_), "w+", encoding=ENCODING) as f_:
                    f_.write(text)


loop_and_replace()
