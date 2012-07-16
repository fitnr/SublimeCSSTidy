#!/usr/bin/env python
#coding: utf8
# adapted from csstidy.py in the Sublime Text 1 webdevelopment package
#################################### IMPORTS ###################################

# Std Libs
from __future__ import with_statement
from os.path import join, normpath
import subprocess

# Sublime Libs
import sublime
import sublime_plugin

#################################### OPTIONS ###################################

supported_options = [
    "allow_html_in_templates",
    "compress_colors",
    "compress_font"
    "discard_invalid_properties",
    "lowercase_s",
    "preserve_css",
    "remove_bslash",
    "remove_last_;",
    "silent",
    "sort_properties",
    "sort_selectors",
    "timestamp",
    "merge_selectors",
    "case_properties",
    "optimise_shorthands",
    "template"
]

#################################### FUNCTIONS #################################


def tidy_string(input_css, script, args, shell=False):
    command = [script] + args
    print "CSSTidy: Sending this to the command line: {0}".format(" ".join(command))
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=shell
        )
    tidied, err = p.communicate(input_css)
    return tidied, err, p.returncode


def get_csstidy_args(csstidy_args, passed_args):
    '''Build command line arguments.'''

    settings = sublime.load_settings('CSSTidy.sublime-settings')

    for option in supported_options:
        # The passed arguments override options in the settings file.
        value = settings.get(option) if passed_args.get(option) is None else passed_args.get(option)

        # If custom value isn't set, ignore that setting.
        if value is None:
            continue
        if value in [True, 'true', 'True', 1]:
            value = '1'
        if value in [False, 'false', 'False', 0]:
            value = '0'

        if 'template' == option and value not in ['default', 'low', 'high', 'highest', 'lowest']:
            value = '"' + normpath(join(sublime.packages_path(), 'User', value)) + '"'

        #print 'CSSTidy: setting --{0}={1}'.format(option, value)
        arg = "--{0}={1}".format(option, value)
        csstidy_args.append(arg)

    return csstidy_args


################################### CONSTANTS ##################################

packagepath = normpath(join(sublime.packages_path(), 'CSStidy'))
csstidy = normpath(join(packagepath, 'win', 'csstidy.exe'))

#################################### COMMAND ##################################


class CssTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit, **args):
        # Get current selection(s).
        print 'CSSTidy: invoked on {0} with args: {1}'.format(self.view.file_name(), args)

        if sublime.platform() == 'windows':
            shell = False
        else:
            shell = True

        if self.view.sel()[0].empty():
            # If no selection, get the entire view.
            self.view.sel().add(sublime.Region(0, self.view.size()))

            """
            # If selection, then make sure not to add body tags and the like.
            # Not sure how to bring this into st2, or if it ever worked.

            if self.view.match_selector(0, 'source.css.embedded.html'):
                self.view.run_command('select_inside_tag')
            """

        # Start off with a dash, the flag for using STDIN
        csstidy_args = get_csstidy_args(['-'], args)

        # Optionally replace tabs with spaces.
        if self.view.settings().get('translate_tabs_to_spaces'):
            space_tab = " " * int(self.view.settings().get('tab_size', 4))

        out_file = normpath(join(packagepath, 'csstidy.tmp'))
        print 'CSSTidy: setting out file to "{0}"'.format(out_file)

        csstidy_args.append(out_file)

        for sel in self.view.sel():
            tidied, err, retval = tidy_string(self.view.substr(sel), csstidy, csstidy_args, shell)
            print 'CSSTidy returned {0}'.format(retval)

        if err or retval != 0:
            print "CSSTidy experienced an error. Opening up a new window to show you."
            # Again, adapted from the Sublime Text 1 webdevelopment package
            nv = self.view.window().new_file()
            nv.set_scratch(1)
            # Append the given command to the error message.
            command = csstidy + " " + " ".join(x for x in csstidy_args)
            nv.insert(edit, 0, err + "\n" + command)
            nv.set_name('CSSTidy Errors')

        else:
            with open(out_file, "r") as fh:
                tidied = fh.read().rstrip()
                if self.view.settings().get('translate_tabs_to_spaces'):
                    tidied.replace("\t", space_tab)
                # Add newline at end of tidied result.
                self.view.replace(edit, sel, tidied + "\n")
