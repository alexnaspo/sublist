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

    def run(self):
        curList = []
        if len(self.project_list) > 1:
            # multiple directories in project, add project select panel
            for List in self.project_list:
                curList.append(List.dir)
            self.window.show_quick_panel(curList, self.project, sublime.MONOSPACE_FONT)
        else:
            # one folder in project, skip project select panel
            if not self.project_list or (self.project_list[0].count() < 1):
                self.window.show_quick_panel(["No Items, Update List?"], self.update(), sublime.MONOSPACE_FONT)
                return
            # if(self.project_list[0].count() < 1):
            #     self.window.show_quick_panel(["No Items"], None, sublime.MONOSPACE_FONT)
            #     return
            for item in self.project_list[0].list:
                curList.append([item.text, item.filepath])
            self.window.show_quick_panel(curList, self.project_list[0].open, sublime.MONOSPACE_FONT)

    def project(self, index):
        # project select panel
        curList = []
        if(self.project_list[index].count() < 1):
            self.window.show_quick_panel(["No Items"], None, sublime.MONOSPACE_FONT)
            return

        for item in self.project_list[index].list:
            curList.append([item.text, item.filepath])
        self.window.show_quick_panel(curList, self.project_list[index].open, sublime.MONOSPACE_FONT)

    def update(self):
        dirs = self.window.folders()

        for i, x in enumerate(dirs):
            #spawn thread for each top-level directory in project
            self.project_list.append(List(x))
            self.project_list[i].start()


class ListItem():
    def __init__(self, filepath, text, lineNum):
        self.filepath = filepath
        self.text = text
        self.lineNum = lineNum


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
        try:
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
        # @TODO look into error handling
        except (4) as (e):
            e = "error"
            print e

    def add(self, item):
        self.list.append(item)

    def count(self):
        return len(self.list)

    def open(self, index):
        # User cancels panel
        if (index == -1):
            return
        window = sublime.active_window()
        window.open_file(self.list[index].filepath + ":" + str(self.list[index].lineNum + 1), sublime.ENCODED_POSITION)
