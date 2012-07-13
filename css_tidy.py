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

################################### CONSTANTS ##################################

packagepath = join(sublime.packages_path(), 'CSStidy')
csstidy = normpath(join(packagepath, 'win/csstidy.exe'))

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


def tidy_string(inputcss, script, args):
    command = [script] + args
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        shell=True
        )
    tidied, err = p.communicate(inputcss)
    return tidied, err, p.returncode


def get_args(args):
    'Build command line arguments.'

    # load CSSTidy settings
    settings = sublime.load_settings('CSSTidy.sublime-settings')

    for option in supported_options:
        value = settings.get(option)

        # If custom value isn't set, ignore that setting.
        if value is None:
            continue
        if value == True:
            value = '1'
        if value == False:
            value = '0'

        # print "CSSTidy: setting " + option + ": " + value
        args.extend(["--" + option, str(value)])

    return args


class CSSTidyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # Get current selection(s).
        if self.view.sel()[0].empty():
            # If no selection, get the entire view.
            self.view.sel().add(sublime.Region(0, self.view.size()))
            # If selection, then make sure not to add body tags and the like.
            # Not sure how to bring this into st2, or if it ever worked.
            #if self.view.match_selector(0, 'source.css.embedded.html'):
            #    self.view.run_command('select_inside_tag')

        # Start off with a dash, flag for using STDIN
        args = get_args(['-'])

        for sel in self.view.sel():
            tidied, err, retval = tidy_string(self.view.substr(sel), csstidy, args)

        if err:
            print "CSSTidy experienced an error. Opening up a new file to show you."
            # Again, adapted from the Sublime Text 1 webdevelopment package
            nv = self.view.window().new_file()
            nv.set_scratch(1)
            # Append the given command to the error message.
            command = csstidy + " " + " ".join(x for x in args)
            nv.insert(edit, 0, err + "\n" + command)
            nv.set_name('CSSTidy Errors')
