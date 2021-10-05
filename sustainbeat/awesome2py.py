from markdown import markdownFromFile, markdown
from bs4 import BeautifulSoup, element, Tag
from pprint import pprint

import sys

class AwesomeListRubric(object):
    def __init__(self, key, rubricEntries):
        super(AwesomeListRubric, self).__init__()
        self.key = key
        self.entries = []
        #pprint(rubricEntries)
        for entry in rubricEntries:
            new = AwesomeListEntry(entry)
            if new:
                self.entries.append(new)

    def __str__(self):
        s = "%s\n" % (self.key)
        for e in self.entries:
            s += "%s" % (e)
        return s
    def __repr__(self):
        return str(self)

class AwesomeListEntry(object):
    def __init__(self, entry, depth=0):
        super(AwesomeListEntry, self).__init__()
        me, children = entry

        self.depth = depth
        htmldata = me.find("a", href=True).extract()
        self.url = htmldata["href"].strip()
        self.name = htmldata.get_text().strip()
        self.text = me.get_text().strip()

        self.children = []
        for subentry in children:
            self.children.append(AwesomeListEntry(subentry, depth=self.depth+1))

    def __str__(self):
        s = " " * self.depth*2 + " - %s %s [%s]\n" % (self.name, self.text, self.url)
        for child in self.children:
            s += str(child)
        return s
    def __repr__(self):
        return str(self)

class AwesomeList(object):
    def __init__(self, path):
        super().__init__()
        self.rubrics = []
        soup = self.convertFromHtml(path)
        contents, d = self.generateDict(soup)
        self.createStructure(contents, d)

    def convertFromHtml(self, path):
        html = markdown(open(path).read())
        soup = BeautifulSoup(html, features='html.parser')
        #print(soup.prettify())
        return soup

    def generateDict(self, soup):
        ### crawl though all categories and extract information
        d = self.findLists(soup)
        ### ...
        ### well specifically fetch the contents entry
        contentKey = "Contents"
        contents = d[contentKey]
        if contentKey in d:
            del d[contentKey]
        return contents, d

    def createStructure(self, contents, d):
        children = self.findListItems(contents, ignoreSubLists=True)
        for c in children:
            rubricKey = c.get_text()
            rubricEntries = d.get(rubricKey, None)
            if rubricEntries:
                entries = self.findListItems(rubricEntries)
                self.rubrics.append(AwesomeListRubric(rubricKey, entries))

    ########################################################
    def findLists(self, soup):
        d = {}
        while True:
            toc = soup.find("h2")
            if toc:
                toc.extract() ## extract will consume the item
                aList = self.findList(soup)
                if aList:
                    d[toc.get_text()] = aList
            else:
                break
        return d
    def findList(self, parent):
        ul = parent.find("ul")
        if ul:
            ul.extract()
        return ul

    def findListItems(self, parent,  ignoreSubLists=False, depth=0):
        children = parent.findChildren("li", recursive=True)
        if ignoreSubLists == False:
            tree = []
            tree.extend([(child, []) for child in children])
            for i, data in enumerate(tree):
                child, subChilds = data
                ### does this item has subitems?
                subList = self.findList(child)
                if subList:
                    ### sublist found ... now add it
                    ###recursion
                    recursiveSubLists = self.findListItems(subList, depth=depth+2)
                    tree[i] = (child, recursiveSubLists)
                #print(" " * depth + "+" +str(tree[i]).replace("\n", ""))
            ### overwrite the normal children list with the special tupled treelist containing subs and stuff
            children = tree
        return children

    def __str__(self):
        s = ""
        for e in self.rubrics:
            s += "%s" % (e)
        return s
    def __repr__(self):
        return str(self)



def main():
    path = "samples/awesomeListSample.md"
    if(len(sys.argv) > 1):
        path = sys.argv[1]

    alc = AwesomeList(path)
    print("===============================================")

    print(alc)
    #for r in alc.rubrics:
    #    for e in r.entries:
    #        ### e.name
    #        ### e.url
    #        ### e.text
    #        print(e)


if __name__ == "__main__":
    main()
