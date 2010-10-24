import os
import csv

import xlrd
import PyRTF as rtf
import dbfutil

class shp_info(object):

    type_map = {'C': 'Text', 'M': 'Text', 'D': 'Date and time', 'N': 'Numeric', 'L': 'Boolean'}
    
    def __init__(self, filename):
        dbf_f = filename[:-4] + '.dbf'
        if os.path.exists(dbf_f):
            self.dbfreader = dbfutil.dbfreader(open(dbf_f, 'rb'))
        else:
            self.dbfreader = None
        
    def get_fields(self):
        #print list(self.db)
        if self.dbfreader is None:
            return [[]]
        else:
            results = [["Name", "Type", "Description"]]
            names = self.dbfreader.next()
            types = self.dbfreader.next()
            assert len(names) == len(types)
            for i in range(len(names)):
                results.append([names[i], shp_info.type_map[types[i][0]], ""])
            return results

class csv_info(object):
    def __init__(self, f):
        self.f = open(f, 'rb')
        try:
            self.dialect = csv.Sniffer().sniff(self.f.read(1024))
        except csv.Error:
            self.dialect = csv.excel

    def get_fields(self):
        results = [["Name", "Description"]]
        self.f.seek(0)
        reader = csv.reader(self.f, self.dialect)
        header = reader.next()
        for cell in header:
            results.append([cell, ""])
        #print results
        return results


class xls_info(object):
    def __init__(self, f):
        self.wb = xlrd.open_workbook(f)
        self.ws = self.wb.sheet_by_index(0)

    def get_fields(self):
        results = [["Name", "Description"]]
        for i in xrange(self.ws.nrows):
            row = self.ws.row(i)
            row_results = []
            for j in xrange(self.ws.ncols):
                if row[j].ctype != xlrd.XL_CELL_EMPTY:
                    row_results.append([row[j].value, ""])
            if len(row_results) > 1:
                results.extend(row_results)
                break
        return results


report_types = {'.shp': ('ESRI Shapefile', shp_info), '.csv': ('Comma separated values', csv_info),
                '.xls': ('Excel spreadsheet', xls_info)}

class finder(object): 
    def __init__(self, path, callback=None):
        self.path = path
        self.callback = callback

    def search(self):
        results = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if os.path.splitext(f)[1] in report_types:
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
        self.header_tps = rtf.TextPS(bold = True)

    def escape(self, tainted):
        # the chars '\', '{', and '}' have a special meaning and must be
        # escaped with a backslash
        s = str(tainted)
        s = s.replace('\\', '\\\\')
        s = s.replace('{', '\\{')
        s = s.replace('}', '\\}')
        # rtf is a 7-bit encoding, so vals >= 128 must be encoded as hex strings
        s = ''.join([c if ord(c) < 128 else "\\'" + hex(ord(c))[2:] for c in s])
        return s
        
    def begin(self):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Heading1)
        p.append('Geodata list')
        self.section.append(p)
        p = rtf.Paragraph(self.ss.ParagraphStyles.Normal)
        p.append(" ")
        self.section.append(p)


    def end(self):
        pass

    def save(self, path):
        rend = rtf.Renderer()
        rend.Write(self.doc, file(path, 'wb'))
    
    def new_file(self, fname):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Heading2)
        p.append(self.escape(fname))
        self.section.append(p)

    def end_file(self, fname):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Normal)
        p.append("")
        self.section.append(p)

        

    def add_attribute(self, key, val):
        p = rtf.Paragraph(self.ss.ParagraphStyles.Normal)
        p.append(rtf.Text(self.escape(key), self.key_tps))
        p.append("  ")
        p.append(self.escape(val))
        self.section.append(p)

    def add_table(self, rows):
        thin_edge = rtf.BorderPS(width = 20, style = rtf.BorderPS.SINGLE)
        thin_frame = rtf.FramePS(thin_edge,  thin_edge,  thin_edge,  thin_edge)
        # header
        header = rows[0]
        widths = [2.6] * (len(header) - 1)
        widths.append(max(13 - sum(widths), 3))
        widths = [int(w * rtf.TabPS.DEFAULT_WIDTH) for w in widths]
        table = rtf.Table(*tuple(widths))
        cells = [rtf.Cell(rtf.Paragraph(rtf.Text(self.escape(cell), self.header_tps)), thin_frame)
                 for cell in header]
	table.AddRow(*cells)
        # body
        for row in rows[1:]:
            cells = [rtf.Cell(rtf.Paragraph(self.ss.ParagraphStyles.Normal, self.escape(cell)), thin_frame)
                     for cell in row]
            table.AddRow(*cells)
            
	self.section.append( table )

        
    
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
            self.reportOnFile(f.strip())
        self.reporter.end()
        
    def reportOnFile(self, file):
        path, f = os.path.split(file)
        self.reporter.new_file(f)
        self.reporter.add_attribute("Path:", path)
#        sys.exit("%s\n%s\n%s" % (file, path, f))
        ext = os.path.splitext(f)[1]
        try:
            type_str = report_types[ext][0]
        except KeyError:
            type_str = ext
        self.reporter.add_attribute("Type:", type_str)

        try:
            info = report_types[ext][1](file)
            table = info.get_fields()
            self.reporter.add_table(table)
        except KeyError:
            pass
        
        self.reporter.end_file(f)
        
if __name__ == "__main__":
    f = finder(os.path.expanduser('~'))
    items = f.search()
    s = saver(items)
    pth =  os.path.expanduser('~') + os.path.sep + 'geosaver.rtf'
    if os.path.exists(pth):
        os.unlink(pth)
    s.save(pth)
    
