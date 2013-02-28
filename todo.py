import sublime, sublime_plugin, os, threading

toDoList = []

class TodoCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    directory = '/Users/Alex/Sites/clients/Bothsider'
    thread = UpdateList(directory)
    thread.start()


class UpdateList(threading.Thread):
  def __init__(self, directory):
    self.dir = directory
    threading.Thread.__init__(self) 

  def run (self):
    try:
      for dirname, dirnames, filenames in os.walk(self.dir):
        # search files for "@todo"
        for filename in filenames:
            searchfile = open(os.path.join(dirname, filename), "r")
            for num, line in enumerate(searchfile, 0):
              if "@todo" in line:          
                fullPath = os.path.join(dirname, filename)       
                item = ListItem(fullPath, line, num)
                item.run()
            searchfile.close()
            # print os.path.join(dirname, filename)      
      return
    # @todo look into error handling
    except ( 4 ) as (e):
      err = "here"

class ListItem():
  def __init__(self, filepath, text, lineNum):
    self.filepath = filepath
    self.text = text
    self.lineNum = lineNum
  def run (self):
    print(self.filepath)
    #@todo need to check for max and handle error
    toDoList.append(self);



class TodolistCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    window = sublime.active_window()

    curList = []
    for item in toDoList:
      curList.append([item.text, item.filepath])
      
    window.show_quick_panel(curList, self.open, sublime.MONOSPACE_FONT)

  def open(self, index):

    window = sublime.active_window()
    window.open_file(toDoList[index].filepath)
    view = window.active_view()

    #focus the @todo note in the new view
    # @todo finish this concept - not always working
    pt = view.text_point(toDoList[index].lineNum, 0)
    view.show(pt);

    

