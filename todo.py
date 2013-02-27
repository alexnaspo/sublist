import sublime, sublime_plugin, os
# @todo - Finish project
class TodoCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    #ensure copy functionality still remains
    self.view.run_command('copy')
    window = sublime.active_window()
    view = window.active_view()
    print(view.file_name())

    for dirname, dirnames, filenames in os.walk('/Users/Alex/Sites/clients/Bothsider/application'):
      # print path to all subdirectories first.
      # for subdirname in dirnames:
      #     print os.path.join(dirname, subdirname)

      # print path to all filenames.
      for filename in filenames:
          searchfile = open(os.path.join(dirname, filename), "r")
          for line in searchfile:
            if "@todo" in line: print line
          searchfile.close()
          print os.path.join(dirname, filename)