import sublime
import sublime_plugin
import os
import threading
import re

# @TODO -9- run updatelist command when sublime is opened?
# @TODO -8- give user the ability to set "select_type" to true in settings
# @TODO -5- documentation


class SublistPanelCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.window = window
        self.project_list = []
        self.terms = []
        self.ignore = []
        self.dirs = self.window.folders()
        s = sublime.load_settings("sublist.sublime-settings")

        # convert settings to ascii from unicode, possibly another solution?
        for x in s.get("terms"):
            self.terms.append(x.encode("ascii", "ignore"))

        for x in s.get("ignore_dirs"):
            self.ignore.append(x.encode("ascii", "ignore"))

        self.regex = self.createRegEx()

    def run(self):
        self.removeEmptyListFromProjectList()
        response = self.getPanelOptions()
        if(response):
            self.activate(response[0], response[1])

    def selectProject(self, index):
        if (index == -1):  # User cancels panel
            return
        options = self.project_list[index].getOptions()
        method = self.project_list[index].open
        self.activate(options, method)

    def createProjectList(self, index):
        for i, directory in enumerate(self.dirs):
            #spawn thread for each top-level directory in project
            self.project_list.append(Sublist(directory, self))
            self.project_list[i].start()

    def getPanelOptions(self):
        options = []
        if not self.project_list or (len(self.project_list) < 1):
            # Project List is Empty - ask to update
            options = ["No Items, Update List?"]
            method = self.createProjectList
        elif len(self.project_list) > 1:
            # Multiple directories - show project List
            for index, List in enumerate(self.project_list):
                options.append([List.dir, str(List.count()) + " Items"])
            method = self.selectProject
        else:
            # Single Directory - skip project list and show sublist
            self.selectProject(0)
            return None
        return [options, method]

    def getItemTypeOptions(self, index):
        options = []
        for x in self.terms:
            options.append(x)
        self.activate(options, None)

    def removeEmptyListFromProjectList(self):
        emptyLists = []
        for index, List in enumerate(self.project_list):
            # don't show directory if it has 0 Items
            if (List.count() < 1):
                emptyLists.append(index)
        for index in emptyLists:
            del self.project_list[index]

    def activate(self, options, method):
        # @TODO as of now this is not needed
        self.window.show_quick_panel(options, method, sublime.MONOSPACE_FONT)

    def createRegEx(self):
        regex = "("
        for count, term in enumerate(self.terms):
            regex += term + ".*"
            if count < len(self.terms) - 1:
                # no pipe after final term
                regex += "|"
        regex += ")"
        return regex


class ListItem():
    def __init__(self, filepath, text, lineNum, priority, itemType):
        self.filepath = filepath
        self.text = text
        self.lineNum = lineNum
        self.priority = priority
        self.itemType = itemType

    def open(self):
        sublime.active_window().open_file(self.filepath + ":" + str(self.lineNum + 1), sublime.ENCODED_POSITION)


class Sublist(threading.Thread):
    def __init__(self, directory, parent):
        self.list = []
        self.dir = directory
        self.parent = parent

        threading.Thread.__init__(self)

    def run(self):
        """ Search local directory in a thread for terms defined in settings

            Ignores directories defined in settings

            @return None
        """
        # search files for terms defined in settings
        for dirname, dirnames, filenames in os.walk(self.dir):
            for filename in filenames:
                searchfile = open(os.path.join(dirname, filename), "r")
                for num, line in enumerate(searchfile, 0):
                    if any(x in line for x in self.parent.terms):
                        fullPath = os.path.join(dirname, filename)
                        line = re.search(self.parent.regex, line, re.I | re.S)
                        itemType = re.search("@([A-Z]+).*", line.group(1), re.I | re.S)
                        itemType = itemType.group(1)
                        # @TODO add the syntax for priority to settings for user controll
                        priority = re.search("-([0-9])-", line.group(1), re.I | re.S)
                        # set priority to 9 if not defined in line
                        priority = int(priority.group(1)) if priority else int(9)
                        item = ListItem(fullPath, line.group(1), num, priority, itemType)
                        self.add(item)
                searchfile.close()
            if any(dirname == self.dir + i for i in self.parent.ignore):
                # ignore files defined in settings
                for i, x in enumerate(dirnames, 0):
                    del dirnames[i]
        return None

    def add(self, item):
        self.list.append(item)

    def count(self):
        return len(self.list)

    def open(self, index):
        if (index == -1):  # User cancels panel
            return
        self.list[index].open()

    def sortList(self):
        self.list = sorted(self.list, key=lambda ListItem: ListItem.priority, reverse=False)

    def getOptions(self):
        self.sortList()
        if len(self.list) < 1:
            return ['No Items']
        options = []
        for item in self.list:
            options.append([item.text, item.filepath])

        return options
