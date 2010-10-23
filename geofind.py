import os

import PyRTF as rtf

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
    def __init__(self):
        self.doc = rtf.Document()
        self.ss = self.doc.StyleSheet
        self.section = rtf.Section()
        self.doc.Sections.append(self.section)
        self.key_tps = rtf.TextPS(underline = True, bold = True)

    def begin(self):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Heading1)
        p.append('Geodata list')
        self.section.append(p)
        p = rtf.Paragraph(self.ss.ParagraphStyles.Normal)
        p.append("  cats!!  ")
        self.section.append(p)


    def end(self):
        pass

    def save(self, path):
        rend = rtf.Renderer()
        rend.Write(self.doc, file(path, 'wb'))
    
    def new_file(self, fname):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Heading2)
        p.append(fname)
        self.section.append(p)
        

    def add_attribute(self, key, val):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Normal)
        p.append(rtf.Text(key, self.key_tps))
        p.append("  ")
        p.append(val)
        self.section.append(p)

    

class saver(object):
    def __init__(self, files, reporter=rtf_report):
        self.files = files
        self.reporter = reporter()
        self.generateReport()

    def save(self, save_path):
        self.reporter.end()
        self.reporter.save(save_path)

    def generateReport(self):
        self.rep = self.reporter.begin()
        for f in self.files:
            self.reportOnFile(str(f))
        self.reporter.end()
        
    def reportOnFile(self, file):
        path, f = os.path.split(file)
        self.reporter.new_file(f)
        self.reporter.add_attribute("Path:", path)

        type_strs = {'.shp': 'ESRI Shapefile', '.csv': 'Comma separated values',
                 '.xls': 'Excel spreadsheet'}
        ext = os.path.splitext(f)[1].strip()
        try:
            type_str = type_strs[ext]
        except KeyError:
                        type_str = ext
        self.reporter.add_attribute("Type:", type_str)

if __name__ == "__main__":
    f = finder(os.path.expanduser('~'))
    items = f.search()
    s = saver(items)
    pth = '/home/fmark/Desktop/test.rtf'
    if os.path.exists(pth):
        os.unlink(pth)
    s.save(pth)
    
