import sublime
import sublime_plugin
import os
import threading
import re

toDoList = []


class UpdatelistCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # @todo how to pass the directory?
        directory = '/Users/Alex/Sites/clients/Bothsider'
        global toDoList
        toDoList = List(directory)
        # creates the listObject in a thread
        toDoList.start()


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
                    for num, line in enumerate(searchfile, 0):
                        if "@todo" in line:
                            fullPath = os.path.join(dirname, filename)
                            line = re.search("(@todo\\s.*)", line, re.I | re.S)
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
        # @todo enable the ability to cancel panel
        window = sublime.active_window()
        window.open_file(self.list[index].filepath)
        view = window.active_view()
        # focus the todo note in the new view
        # @todo finish this concept - not always working
        pt = view.text_point(self.list[index].lineNum, 0)
        view.show(pt)

    def panel(self):
        curList = []
        # @todo return empty array message if self.list is empty
        # @todo if thread is currently searching for files, return message
        for item in self.list:
            curList.append([item.text, item.filepath])
            window = sublime.active_window()
        window.show_quick_panel(curList, self.open, sublime.MONOSPACE_FONT)
