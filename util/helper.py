'''Recommended 3.7+'''
import json
from datetime import datetime
# parameterize later:

def validURL(url:str|list[int])->(str, str|list[int]):
    '''Attempts to guess the type and validity of url passed'''
    if url == "":
        return ("empty", url)
    if type(url) == list:
        for link in url:
            link = link.split('.')[-1]
            if link != 'jpg' or link != 'png' or link != 'jpeg':
                raise FileNotFoundError('Possibly bad image extension')
        return ("urlarray", url)
    if len(url) == 7:
        return ("imgur", url)
    if len(url) == 11:
        return ("imgchest", url)
    if "imgur" in url.split('.')[0]:
        url = url.split('/')
        return ("imgur", url[url.index('a') + 1])
    if "imgchest" in url.split('.')[0]:
        url = url.split('/')
        return ("imgchest", url[url.index('p') + 1])
    else:
        raise FileNotFoundError('Unknown type')

class Chapter(object):
    '''Models a chapter, is a dict'''
    def __init__(self, title:str="", volume:str="",
                 groups:dict[str, str|list[str]]={"": ""},
                 last_updated:str|None=None, force:bool=False):
        try:
            for k, v in groups.items():
                typ, id = validURL(v)
                if typ == "urlarray" or typ == "empty":
                    continue
                groups[k] = "/proxy/api/%s/chapter/%s" % (typ, id)
        except FileNotFoundError as fe:
            print("File Error,", fe)
            if not force:
                quit()
        if last_updated is None:
            last_updated = str(datetime.now().timestamp())
        self.title = title
        self.volume = volume
        self.groups = groups
        self.last_updated = last_updated
    def publish(self):
        return dict(title=self.title, volume=self.volume,
                    groups=self.groups, last_updated=self.last_updated)

class Manga(object):
    '''Models a manga, is a json'''
    def __init__(self, title:str="", description:str="",
                 artist:str="", author:str="", cover:str="",
                 chapters:dict[str, Chapter] = {'0': Chapter().publish()}):
        self.title = title
        self.description = description
        self.artist = artist
        self.author = author
        self.cover = cover
        self.chapters = chapters
    def publish(self):
        return dict(title=self.title, description=self.description,
                    artist=self.artist, author=self.author, cover=self.cover,
                    chapters=dict(sorted(self.chapters.items(),
                                         key=lambda t: int(t[0]), reverse=True)))
    def chset(self, chapter:Chapter, ordinal:int, save:bool=True):
        if save:
            self._undo = self.chapters.copy()
        ordinal = str(ordinal)
        if ordinal in self.chapters.keys():
            print("Replacing: Chapter", ordinal)
        self.chapters[ordinal] = chapter.publish()
    def chadd(self, *chapters:Chapter, ordinal:int|None=None, save:bool=True):
        if save:
            self._undo = self.chapters.copy()
        if ordinal is None:
            ordinal = max(self.chapters.keys(), key=int)
        for chapter in chapters:
            self.chset(chapter, ordinal, False)
            ordinal += 1
    def chundo(self):
        try:
            self._undo
        except AttributeError:
            print("Can't undo without doing something first")
            return False
        self._redo = self.chapters.copy()
        self.chapters = self._undo
        return True
    def chredo(self):
        try:
            self._redo
        except AttributeError:
            print("Can't redo without undoing something first")
            return False
        self._undo = self.chapters.copy()
        self.chatpers = self._redo
        return True
    @staticmethod
    def fromjson(infile: str):
        with open(infile, 'r') as f:
            manga = Manga(**json.load(f))
        return manga
    @staticmethod
    def tojson(outfile:str, manga:object):
        with open(outfile, 'w') as f:
            json.dump(manga.publish(), f, indent=2)

if __name__ == '__main__':
    import os
    path = os.path.split(os.path.abspath(__file__))[0]
    m = Manga.fromjson(os.path.join(path, "t.json"))
    m.chset(Chapter(groups={"Placeholder": "m9yxklre67q"}),3)
    Manga.tojson(os.path.join(path, "t.json"), m)