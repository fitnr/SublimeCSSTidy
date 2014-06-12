#!/usr/bin/env python
#coding: utf8
# adapted from csstidy.py in the Sublime Text 1 webdevelopment package
from os.path import join
import subprocess
import sublime
import sublime_plugin


### CONSTANTS ###
supported_options = [
    "compress_colors",
    "compress_font-weight",
    "discard_invalid_properties",
    "discard_invalid_selectors",
    "lowercase_s",
    "preserve_css",
    "remove_bslash",
    "remove_last_;",
    "sort_properties",
    "sort_selectors",
    "timestamp",
    "merge_selectors",
    "case_properties",
    "optimise_shorthands",
    "template"
]

### COMMAND ##
class CssTidyCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        # Get current selection(s).
        print('CSSTidy: tidying {0} with args: {1}'.format(self.view.file_name(), args))

        self.packagepath = join(sublime.packages_path(), 'CSSTidy')
        self.scriptpath = join(self.packagepath, 'csstidy.php')
        self.startupinfo = None

        if sublime.platform() == 'windows':
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.startupinfo.wShowWindow = subprocess.SW_HIDE

        try:
            # executable will usually be "php".
            # If php isn't available, it will revert to "<package path>/win/csstidy.exe" on Windows
            executable = self.find_tidier()
        except OSError:
            print("CSSTidy: Couldn't find csstidy.exe or PHP. Stopping without Tidying anything.")
            return

        if self.view.sel()[0].empty():
            # If no selection, get the entire view.
            self.view.sel().add(sublime.Region(0, self.view.size()))

            """
            # If selection, then make sure not to add body tags and the like.
            # Not sure how to bring this into st2, or if it ever worked.

            if self.view.match_selector(0, 'source.css.embedded.html'):
                self.view.run_command('select_inside_tag')
            """

        # Fetch arguments from prefs files.
        args = self.get_args(args, executable)

        shell = self.set_shell(executable)

        # Tidy each selection.
        for sel in self.view.sel():
            #print('CSSTIdy: Sending this to Tidy:\n', self.view.substr(sel))
            tidied, err, retval = self.tidy_string(self.view.substr(sel), args, shell)
            #print('CSSTIdy: Got these tidied styles back:\n', tidied)

            if err or retval != 0:
                print('CSSTidy returned {0}'.format(retval))
                print("CSSTidy experienced an error. Opening up a new window to show you more.")

                # Again, adapted from the Sublime Text 1 webdevelopment package
                nv = self.view.window().new_file()

                # Append the given command to the error message.
                nv.insert(edit, 0, err + "\nCommand sent to Tidy:\n" + " ".join(x for x in args))
                nv.set_name('CSSTidy Errors')

            else:
                if self.view.settings().get('translate_tabs_to_spaces'):
                    tidied.replace("\t", self.space_tab)
                self.view.replace(edit, sel, tidied + "\n")
                return

    def set_shell(self, executable):
        if sublime.platform() == 'windows' and executable == 'php':
            return True
        return False

    def tidy_string(self, css, args, shell):
        print("CSSTidy: Sending command:" + " ".join(args))

        p = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=self.startupinfo,
            shell=shell
            )

        # Encode to send to pipe, decode what's recieved from pipe
        tidied, err = p.communicate(css.encode('utf-8', 'backslashreplace'))
        tidied = tidied.decode('utf-8')

        return tidied, err, p.returncode

    def find_tidier(self):
        ' Try php, then bundled tidy (if windows)'

        try:
            subprocess.call(['php', '-v'], startupinfo=self.startupinfo)
            # print("CSSTidy: Using PHP CSSTidy module.")
            return 'php'
        except OSError:
            print("CSSTidy: PHP not found. Is it installed and in your PATH?")
            pass

        if sublime.platform() == 'windows':
            try:
                scriptpath = join(self.packagepath, 'win', 'csstidy.exe')
                subprocess.call([scriptpath, "-v"], startupinfo=self.startupinfo, shell=True)
                print("CSSTidy: using csstidy.exe")
                return scriptpath
            except OSError:
                print("CSSTidy: Didn't find tidy.exe in " + self.packagepath)
                pass

        raise OSError

    def get_args(self, passed_args, executable):
        '''Build command line arguments.'''

        settings = sublime.load_settings('CSSTidy.sublime-settings')
        csstidy_args = [executable]

        # print('CSSTidy: preserve css get:', settings.get("preserve_css"))

        # Start off with a dash, the flag for using STDIN
        # Set out file for csstidy.exe. PHP uses STDOUT
        if executable == 'php':
            csstidy_args.extend(['-f', self.scriptpath, '--'])
        else:
            csstidy_args.extend(['-', '--silent=1'])

        for option in supported_options:
            # If custom value isn't set, ignore that setting.
            if settings.get(option) is None and passed_args.get(option) is None:
                continue

            # The passed arguments override options in the settings file.
            value = passed_args.get(option) if passed_args.get(option) is not None else settings.get(option)

            # For some reason, csstidy.exe acts up less when passed numerals rather than booleans.
            if value in [True, 'true', 'True', 1]:
                value = '1'
            if value in [False, 'false', 'False', 0]:
                value = '0'

            if 'template' == option and value not in ['default', 'low', 'high', 'highest']:
                value = join(sublime.packages_path(), 'User', value)

            csstidy_args.append("--{0}={1}".format(option, value))

        # Optionally replace tabs with spaces.
        if self.view.settings().get('translate_tabs_to_spaces'):
            self.space_tab = " " * int(self.view.settings().get('tab_size', 4))

        return csstidy_args
