import os

class finder(object): 
    def __init__(self, path, callback=None):
        self.path = path
        self.callback = callback
        self.types = set(['.shp', '.xls', '.csv'])

    def search(self):
        results = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if os.path.splitext(f)[1] in self.types:
                    fullpath = "%s%s%s\n" % (root, os.path.sep, f)
                    if not self.callback is None:
                        self.callback(fullpath)
                    results.append(fullpath)
        return results
