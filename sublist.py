import sublime
import sublime_plugin
import os
import threading
import re

# @TODO auto creation/completion of github/bitbucket issues?
# @TODO run updatelist command when sublime is opened?
# @TODO give user the ability to set "select_type" to true in settings
# if true, this will provide another menu step, to select @TODOs or @errors ETC.


class SublistPanelCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        self.window = window
        self.project_list = []
        self.dirs = self.window.folders()

    def run(self):
        options = []
        if not self.project_list or (len(self.project_list) < 1):
            options = ["No Items, Update List?"]
            method = self.update()
        elif len(self.project_list) > 1:
            options = self.getDirOptions()
            method = self.project
        else:
            # one folder in project, skip project select panel
            options = self.project_list[0].getOptions()
            method = self.project_list[0].open

        self.activate(options, method)

    def project(self, index):
        # project select panel
        # @TODO this can be reworked / more elegant
        if (index == -1):  # User cancels panel
            return
        options = self.project_list[index].getOptions()
        method = self.project_list[index].open
        self.activate(options, method)

    def update(self):
        for i, x in enumerate(self.dirs):
            #spawn thread for each top-level directory in project
            self.project_list.append(List(x))
            self.project_list[i].start()

    def getDirOptions(self):
        options = []
        emptyLists = []
        for index, List in enumerate(self.project_list):
            # don't show directory if it has 0 Items
            if (List.count() > 0):
                options.append([List.dir, str(List.count()) + " Items"])
            else:
                # remove the empty Lists from project_list
                # @TODO this can be more elgant
                emptyLists.append(index)
        for List in emptyLists:
            del self.project_list[List]
        return options

    def activate(self, options, method):
        # @TODO as of now this is not needed
        self.window.show_quick_panel(options, method, sublime.MONOSPACE_FONT)


class ListItem():
    def __init__(self, filepath, text, lineNum):
        self.filepath = filepath
        self.text = text
        self.lineNum = lineNum

    def open(self):
        sublime.active_window().open_file(self.filepath + ":" + str(self.lineNum + 1), sublime.ENCODED_POSITION)


class List(threading.Thread):
    def __init__(self, directory):
        self.list = []
        self.dir = directory
        self.ignore = []
        self.terms = []
        s = sublime.load_settings("sublist.sublime-settings")

        # convert settings to ascii from unicode, possibly another solution?
        for x in s.get("terms"):
            self.terms.append(x.encode("ascii", "ignore"))

        for x in s.get("ignore_dirs"):
            self.ignore.append(x.encode("ascii", "ignore"))

        threading.Thread.__init__(self)

    # creates a list
    def run(self):
        # @TODO Error handling
        # search files for terms defined in settings
        for dirname, dirnames, filenames in os.walk(self.dir):
            for filename in filenames:
                searchfile = open(os.path.join(dirname, filename), "r")
                for num, line in enumerate(searchfile, 0):
                    if any(x in line for x in self.terms):
                        fullPath = os.path.join(dirname, filename)
                        # @TODO regex should be based on settings
                        line = re.search("(@todo.*|@return.*)", line, re.I | re.S)
                        item = ListItem(fullPath, line.group(1), num)
                        self.add(item)
                searchfile.close()
            if any(dirname == self.dir + i for i in self.ignore):
                # ignore files defined in settings
                for i, x in enumerate(dirnames, 0):
                    del dirnames[i]
        return

    def add(self, item):
        self.list.append(item)

    def count(self):
        return len(self.list)

    def open(self, index):
        if (index == -1):  # User cancels panel
            return
        self.list[index].open()

    def getOptions(self):
        options = []
        for item in self.list:
            options.append([item.text, item.filepath])
        if len(options) < 1:
            # this is not needed as of now
            options = ["No Items"]
        return options
