import sublime, sublime_plugin, os, threading
# @todo - Finish project

class TodoCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    window = sublime.active_window()
    view = window.active_view()
    print(view.file_name())

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
                item = AddListItem(filename, line, num)
                item.run()
            searchfile.close()
            # print os.path.join(dirname, filename)      
      return
    # @todo look into error handling
    except ( 4 ) as (e):
      err = "here"

class AddListItem():
  def __init__(self, filename, text, lineNum):
    self.filename = filename
    self.text = text
    self.lineNum = lineNum
  def run (self):
    print(self.lineNum)

