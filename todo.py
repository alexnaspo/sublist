import sublime
import sublime_plugin
import os
import threading
import re

toDoList = []


class UpdatelistCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # @todo how to pass the directory?
        directory = '/Users/Alex/Sites/clients/Bothsider/application'
        global toDoList
        toDoList = List(directory)
        # creates the listObject in a thread
        toDoList.start()
        sublime.status_message('AutoListr successfully loaded your list')


class PanelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        toDoList.panel()


class ListItem():
    def __init__(self, filepath, text, lineNum):
        self.filepath = filepath
        self.text = text
        self.lineNum = lineNum


class List(threading.Thread):
    def __init__(self, directory):
        self.list = []
        self.dir = directory
        threading.Thread.__init__(self)

    # creates a list
    def run(self):
        try:
            # search files for "@todo"
            for dirname, dirnames, filenames in os.walk(self.dir):
                for filename in filenames:
                    searchfile = open(os.path.join(dirname, filename), "r")
                    # @todo create moving status bar
                    for num, line in enumerate(searchfile, 0):
                        if "@todo" in line:
                            fullPath = os.path.join(dirname, filename)
                            line = re.search("(@todo.*)", line, re.I | re.S)
                            item = ListItem(fullPath, line.group(1), num)
                            self.add(item)
                    searchfile.close()
            return
        # @todo look into error handling
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
