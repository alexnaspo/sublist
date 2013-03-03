import sublime
import sublime_plugin
import os
import threading
import re

toDoList = []

# @TODO auto creation/completion of github/bitbucket issues?


class UpdatelistCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        global toDoList
        toDoList = []
        dirs = sublime.active_window().folders()

        for i, x in enumerate(dirs):
            #spawn thread for each top-level directory in project
            toDoList.append(List(x))
            toDoList[i].start()
            if dirs < 1:
                # temporary fix, this should be re-done/re-thought properly
                break
        sublime.status_message('AutoListr successfully loaded your list')


class PanelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        window = sublime.active_window()
        curList = []

        if len(toDoList) > 1:
            # multiple directories in project, add project select panel
            for List in toDoList:
                curList.append(List.dir)
            window.show_quick_panel(curList, self.project, sublime.MONOSPACE_FONT)
        else:
            # one folder in project, skip project select panel
            if(toDoList[0].count() < 1):
                window.show_quick_panel(["No Items"], None, sublime.MONOSPACE_FONT)
                return
            for item in toDoList[0].list:
                curList.append([item.text, item.filepath])
            window.show_quick_panel(curList, toDoList[0].open, sublime.MONOSPACE_FONT)

    def project(self, index):
        #project select panel
        window = sublime.active_window()
        curList = []
        for item in toDoList[index].list:
            curList.append([item.text, item.filepath])
        window.show_quick_panel(curList, toDoList[index].open, sublime.MONOSPACE_FONT)


class ListItem():
    def __init__(self, filepath, text, lineNum):
        self.filepath = filepath
        self.text = text
        self.lineNum = lineNum


class List(threading.Thread):
    def __init__(self, directory):
        self.list = []
        self.dir = directory
        self.terms = []
        s = sublime.load_settings("sublist.sublime-settings")
        for x in s.get("terms"):
            self.terms.append(x.encode("ascii", "ignore"))
        threading.Thread.__init__(self)

    # creates a list
    def run(self):
        try:
            # search files for "@todo"
            for dirname, dirnames, filenames in os.walk(self.dir):
                for filename in filenames:
                    searchfile = open(os.path.join(dirname, filename), "r")
                    # @TODO create moving status bar
                    for num, line in enumerate(searchfile, 0):
                        #search each line for all strings defined in settings
                        if any(x in line for x in self.terms):
                            fullPath = os.path.join(dirname, filename)
                            # @TODO regex should be based on settings
                            line = re.search("(@todo.*|@return.*)", line, re.I | re.S)
                            item = ListItem(fullPath, line.group(1), num)
                            self.add(item)
                    searchfile.close()
            return
        # @TODO look into error handling
        except (4) as (e):
            e = "error"
            print e

    def add(self, item):
        print(item)
        self.list.append(item)

    def count(self):
        return len(self.list)

    def open(self, index):
        # User cancels panel
        if (index == -1):
            return
        window = sublime.active_window()
        window.open_file(self.list[index].filepath + ":" + str(self.list[index].lineNum + 1), sublime.ENCODED_POSITION)

    def panel(self):
        window = sublime.active_window()
        if(self.count() < 1):
            window.show_quick_panel(["No Items"], None, sublime.MONOSPACE_FONT)
            return
        curList = []

        for item in self.list:
            curList.append([item.text, item.filepath])
        window.show_quick_panel(curList, self.open, sublime.MONOSPACE_FONT)
