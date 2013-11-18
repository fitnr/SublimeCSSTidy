#!/usr/bin/env python
#coding: utf8
# adapted from csstidy.py in the Sublime Text 1 webdevelopment package
from os.path import join, normpath
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
packagepath = normpath(join(sublime.packages_path(), 'CSSTidy'))
csstidypath = normpath(join(packagepath, 'win', 'csstidy.exe'))
scriptpath = normpath(join(packagepath, 'csstidy.php'))

startupinfo = None
if sublime.platform() == 'windows':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

### FUNCTIONS ###


def tidy_string(input_css, script, args, shell):
    command = [script] + args
    print("CSSTidy: Sending command:", " ".join(command))

    p = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        startupinfo=startupinfo,
        shell=shell
        )

    tidied, err = p.communicate(input_css)
    return tidied, err, p.returncode


def find_tidier():
    ' Try php, then bundled tidy (if windows)'

    try:
        subprocess.call(['php', '-v'], startupinfo=startupinfo)
        # print("CSSTidy: Using PHP CSSTidy module.")
        return 'php', True
    except OSError:
        print("CSSTidy: PHP not found. Is it installed and in your PATH?")
        pass

    if sublime.platform() == 'windows':
        try:
            subprocess.call([csstidypath, "-v"], startupinfo=startupinfo, shell=True)
            print("CSSTidy: using csstidy.exe")
            return csstidypath, False
        except OSError:
            print("CSSTidy: Didn't find tidy.exe in " + packagepath)
            pass

    raise OSError

### COMMAND ##


class CssTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        # Get current selection(s).
        print('CSSTidy: tidying {0} with args: {1}'.format(self.view.file_name(), args))

        try:
            csstidy, using_php = find_tidier()
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
        csstidy_args = self.get_args(args, using_php)

        if sublime.platform() == 'windows' and using_php is True:
            shell = True
        else:
            shell = False

        # Tidy each selection.
        for sel in self.view.sel():
            #print('CSSTIdy: Sending this to Tidy:\n', self.view.substr(sel))
            tidied, err, retval = tidy_string(self.view.substr(sel), csstidy, csstidy_args, shell)
            #print('CSSTIdy: Got these tidied styles back:\n', tidied)

            if err or retval != 0:
                print('CSSTidy returned {0}'.format(retval))
                print("CSSTidy experienced an error. Opening up a new window to show you more.")
                # Again, adapted from the Sublime Text 1 webdevelopment package
                nv = self.view.window().new_file()
                nv.set_scratch(1)
                # Append the given command to the error message.
                command = csstidy + " " + " ".join(x for x in csstidy_args)
                nv.insert(edit, 0, err + "\nCommand sent to Tidy:\n" + command)
                nv.set_name('CSSTidy Errors')

            else:
                if self.view.settings().get('translate_tabs_to_spaces'):
                    tidied.replace("\t", self.space_tab)
                self.view.replace(edit, sel, tidied + "\n")
                return

    def get_args(self, passed_args, using_php):
        '''Build command line arguments.'''

        self.settings = sublime.load_settings('CSSTidy.sublime-settings')

        print('get', self.settings.get("preserve_css"))
        csstidy_args = []
        settings = self.settings
        # Start off with a dash, the flag for using STDIN
        if using_php:
            csstidy_args.extend(['-f', normpath(scriptpath), '--'])
        else:
            csstidy_args.append('-')

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
                value = normpath(join(sublime.packages_path(), 'User', value))

            csstidy_args.append("--{0}={1}".format(option, value))

        # Optionally replace tabs with spaces.
        if self.view.settings().get('translate_tabs_to_spaces'):
            self.space_tab = " " * int(self.view.settings().get('tab_size', 4))

        # Set out file for csstidy.exe. PHP using stream.
        if not using_php:
            csstidy_args.append('--silent=1')

        return csstidy_args
