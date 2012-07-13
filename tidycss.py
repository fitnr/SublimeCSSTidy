#!/usr/bin/env python
#coding: utf8
#################################### IMPORTS ###################################

# Std Libs
from __future__ import with_statement
from os.path import dirname, basename, join
import subprocess

# Sublime Libs
import sublime
import sublimeplugin

# AAA Libs
from indentation import insert_or_replace_indented

################################### CONTANTS ###################################

PACKAGE = join(sublime.packagesPath(), 'tidy')

#TIDY =   join(PACKAGE, 'csstidy.exe')
TIDY = 'C:\\tidy\\csstidy.exe';

#################################### OPTIONS ###################################

# csstidy input_filename [
#  --allow_html_in_templates=[false|true] |
#  --compress_colors=[true|false] |
#  --compress_font-weight=[true|false] |
#  --discard_invalid_properties=[false|true] |
#  --lowercase_s=[false|true] |
#  --preserve_css=[false|true] |
#  --remove_bslash=[true|false] |
#  --remove_last_;=[false|true] |
#  --silent=[false|true] |
#  --sort_properties=[false|true] |
#  --sort_selectors=[false|true] |
#  --timestamp=[false|true] |
#  --merge_selectors=[2|1|0] |
#  --case_properties=[0|1|2] |
#  --optimise_shorthands=[1|2|0] |
#  --template=[default|filename|low|high|highest] |
#  output_filename ]*

################################################################################

class CSSTidySelection(sublimeplugin.TextCommand):
    def run(self, view, args):
        if not view.hasNonEmptySelectionRegion():
            if view.matchSelector(0, 'text.html'):
                view.runCommand('selectInsideTag')
            else:
                view.sel().add(sublime.Region(0, view.size()))

        sel = view.sel()[0]
        sel_str = view.substr(sel)

        inf  = join(PACKAGE, 'csstidy.tmp')
        outf = inf + 'tidied'

        with open(inf, 'w') as fh: fh.write(sel_str)

        cmd = [TIDY,
            inf,
            '--template=high',
            '--preserve_css=true',
            '--sort_selectors=false',
            '--sort_properties=true',
            '--compress_colors=true',
            '--lowercase_s=false',
            '--merge_selectors=0',
            '--template=C:\\tidy\\custom.tpl',

            outf ]

        p = subprocess.Popen(cmd, shell=1)

        if not p.wait():
            with open(outf) as fh:
                tidied = fh.read().rstrip()
                insert_or_replace_indented(view, sel, tidied)
        else:
            sublime.messageBox (
            'There was a disaster. '
            'Try checking the css for missing property values' )

################################################################################