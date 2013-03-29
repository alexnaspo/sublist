Sublist
====
A Sublime Text plugin that searches the open directories for @notes such as @TODO or @ERROR and generates a list easily accessible by the quick panel. Selecting a list item will open that file and bring you to the line of that note.

Usage 
--------
A list is an instance of a window. The first time you run the command in a window, the panel will display an option to update your list, any subsequent time will display your list. The controls I have set are as follows, but feel free to change them to your liking.

+ **OSX** - ```control+option+l```
+ Still testing for Linux and Windows

Settings
-----------
+ **terms** - The list will be based on the value of the ```"terms"``` property in settings. I have defaulted this to @TODO, however this can be set to your preference. For example, if you would like @ERROR to be included, adjust the terms option in ```sublist.sublime-settings``` accordingly, like this ```  "terms": ["@TODO", "@ERROR"]```.
+ **priority** - You can set priority to an item by adding ```-(:num)-``` to any list item. One being the most important. Items without a set priority will default to 9. For example, ```@TODO -1- This item is important```.
+ **ignore_dirs** - In order to speed up the search and ignore unnecessary files, I have added the option to ignore any directories you may need. By default, I am ignoring the ```/.git``` directory. You can add more directories that you wish to ignore. For example, if using laravel you may wish to ignore the storage folder by doing something like this, ```"ignore_dirs": ["/.git", "/storage"]```.

Installation
---------------
 Clone the directory in the following location based on your OS
 + **OSX** - ```~/Library/Application\ Support/Sublime\ Text\ 2/Packages/```
 + **Linux** - ```~/.config/sublime-text-2/Packages/```
 + **Windows** - ```C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages```

After further testing I will make it available through package control.

