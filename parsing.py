# Possible improvements
# 1. Too much code in one .py file. Move helper class to another file
# 2. Can create GUI instead of using command line
# 3. To be continued...


import sys
import requests
import time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import webbrowser

from bs4 import BeautifulSoup

# path to the file that will store title, short version and current chapter of each book
file = '/home/aibek/Programming/PyCharm/scripts/parser/books.txt'

# path where pdf file will be generated
pdf_file = '/home/aibek/Programming/PyCharm/scripts/parser/'

# link from the website, where parsing happens
base_url = 'https://www.wuxiaworld.co/'


# helper class that generates PDF file
class Generate:
    def __init__(self, title, chapter):
        # initial conditions like title and chapter that passed
        self.title = title
        self.chapter = chapter
        # delay will be used during request
        self.delay = 1
        self.link = []
        self.text = ''

    def Run(self):
        # make get request to the url
        r = requests.get(base_url + self.title + '/')
        # parse it using BSoup
        soup = BeautifulSoup(r.content, 'html.parser')

        # if some error occurred and we couldn't get html page return error
        if len(soup.find_all('dd')) == 0:
            return -1, 'Connection error'

        # each chapter link placed inside <dd> tag
        # thus get all dd tags
        for dd in soup.find_all('dd'):
            s = dd.text.split(' ')
            # there high possibility that each tag will store chapter number and its name
            # so get chapter number and if it's >= current chapter that we are reading we need to
            # get it, and save inside PDF file
            for i in range(len(s)):
                if str(s[i]).isdigit() and int(s[i]) >= int(self.chapter):
                    # get link to the chapter
                    self.link.append(dd.find('a')['href'])

        # If current chapter, is incorrect number or given chapter is not released return
        # else start PDF file generation
        if len(self.link) > 0:
            path = self.CreatePdf()
            return 1, path
        else:
            return -1, 'Incorrect Initial Chapter. Please update'

    def CreatePdf(self):

        s = ''
        # get chapter using each link from array
        for i in range(len(self.link)):
            print(i + 1)
            # make request to the web app, and get html content
            r = requests.get(base_url + self.title + '/' + self.link[i])
            soup = BeautifulSoup(r.content, 'html.parser')
            div = soup.find('div', {'id': 'content'})
            # text is stored inside div, but it must be filtered
            self.text = str(div)
            self.GetText()
            # chapter text stored inside string
            s += self.text
            # add delay so as to not get banned
            time.sleep(self.delay)

        # start PDF file generation
        doc = SimpleDocTemplate(pdf_file + self.title + '.pdf', pagesize=A4,
                                rightMargin=2 * cm, leftMargin=2 * cm,
                                topMargin=2 * cm, bottomMargin=2 * cm)

        doc.build([Paragraph(s, getSampleStyleSheet()['Normal']), ])

        # return path to the pdf file
        return pdf_file + self.title + '.pdf'

    # filter string from unnecessary characters
    def GetText(self):
        self.text = self.text.replace('<script>', '')
        self.text = self.text.replace('</script>', '')
        self.text = self.text.replace('chaptererror();', '')
        self.text = self.text.replace('<div id="content">', '')
        self.text = self.text.replace('</div>', '')
        self.text = self.text.replace('ChapterMid();', '')


# main class
class Init:
    def __init__(self):
        # boolean variables that will be used later
        self.skip = False
        self.exist = False
        # check if file exist
        self.Check()
        # if there are arguments passed
        if len(sys.argv) >= 2:
            self.Run()

    @staticmethod
    def Check():
        # try to read file, if it does not exist, generate one
        try:
            open(file, 'r+')
        except FileNotFoundError:
            open(file, 'w+')

    def Run(self):
        # if first argument is GET, open file and print every line
        if str(sys.argv[1]).upper() == 'GET':
            with open(file, 'r') as f:
                for line in f.readlines():
                    print(line[:-1])

        # if first argument is ADD, check whether there is title of the novel
        if str(sys.argv[1]).upper() == 'ADD' and len(sys.argv) > 2:
            # check if given title exists in the file
            with open(file, 'a+') as f:
                for line in f.readlines():
                    if str(sys.argv[2]).lower in line:
                        self.skip = True
            # if title does not exist append it to the file
            if not self.skip:
                # string will consist of title, its shorter version for simplicity
                obj = str(sys.argv[2]).lower() + ' ' + self.ShortVersion(str(sys.argv[2])) + ' '
                # if there is 3 argument, it will be used as a current chapter, default = 1
                obj += str(sys.argv[3]) if (len(sys.argv) > 3 and str(sys.argv[3]).isdigit()) else '1'
                obj += '\n'
                # append string to file
                with open(file, 'a+') as f:
                    f.write(obj)
            else:
                print('Title is already in the collection')

        # if first argument is UPDATE, check if there are two additional arguments
        # which are: title and new chapter
        if str(sys.argv[1]).upper() == 'UPDATE' and len(sys.argv) > 3:
            obj = []
            # check if title exist in the novel
            with open(file, 'r+') as f:
                for line in f.readlines():
                    if str(sys.argv[2]).lower() in line and str(sys.argv[3]).isdigit():
                        rs = line.split(' ')
                        s = rs[0] + ' ' + rs[1] + ' '
                        s += str(sys.argv[3]) + '\n'
                        obj.append(s)
                        self.exist = True
                    else:
                        obj.append(line)

            # if it exists, rewrite file with the replacement of line that has given title
            if self.exist:
                with open(file, 'w') as f:
                    for line in obj:
                        f.writelines(line)
            else:
                print('Given title does not exist in the collection')

        # if first argument is GENERATE and there is additional argument that stores title of the novel
        if str(sys.argv[1]).upper() == 'GENERATE' and len(sys.argv) > 2:
            # search title original name and current chapter that will be used to generate pdf
            with open(file, 'r') as f:
                for line in f.readlines():
                    if str(sys.argv[2]).lower() in line:
                        self.exist = True
                        obj = line.split(' ')
                        helper = Generate(obj[0], obj[2][:-1])
                        pdf, result = helper.Run()

            # if title exists and we successfully generated pdf file, open it
            if self.exist:
                if pdf:
                    print('success')
                    webbrowser.open_new(result)
                else:
                    print(result)

    # method that takes first char of each word
    # to generate short version of the title
    @staticmethod
    def ShortVersion(title):
        val = title.split('-')
        s = ''
        for word in val:
            s += word[0].lower()
        print(s)
        return s


if __name__ == '__main__':
    # run class with all the necessary methods
    Init()
