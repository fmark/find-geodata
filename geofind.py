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

class rtf_report(object):
    def __init(self):
        pass

    def begin(self):
        pass

    def end(self):
        pass
    
    def new_file(self, fname):
        pass

    def add_attribute(self, key, val):
        pass
    

class saver(object):
    def __init__(self, files, reporter=rtf_report):
        self.files = files
        self.reporter = reporter()
        self.generateReport()

    def save(self, save_path):
        print "saving"

    def generateReport(self):
        self.rep = self.reporter.begin()
        for f in self.files:
            self.reportOnFile(f)
        self.reporter.end()
        
    def reportOnFile(self, file):
        path, f = os.path.split(file)
        self.reporter.new_file(f)
        self.reporter.add_attribute("Path:", path)

        type_strs = {'.shp': 'ESRI Shapefile', '.csv': 'Comma separated values',
                 '.xls': 'Excel spreadsheet'}
        try:
            type_str = type_strs[os.path.splitext(f)[1]]
        except KeyError:
                        type_str = os.path.splitext(f)[1]
        self.reporter.add_attribute("Type:", type_str)
