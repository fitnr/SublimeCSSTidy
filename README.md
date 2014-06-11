# SublimeCSSTidy
## CSS code formatter for Sublime Text

SublimeCSSTidy is a [Sublime Text](http://www.sublimetext.com/) package for cleaning and tidying up your CSS. It's mostly a wrapper for the [CSS Tidy PHP Library](http://github.com/Cerdic/CSSTidy), but it will fall back on a bundled [CSS Tidy](http://csstidy.sourceforge.net/) executable for Windows users without PHP.

SublimeCSSTidy adds three commands to the command palette:

* Tidy CSS (Highest Compression)
* Tidy CSS (Low Compression)
* Tidy CSS

The last command uses the default template, which balances readability and compression. If you can decipher the complicated pattern for creating [custom formatting rules](http://csstidy.sourceforge.net/templates.php), SublimeCSSTidy will happily use them. An example of a custom template file is included (`template-medium.txt`).

### Windows Support

If you do not have PHP installed, SublimeCSSTidy will use a bundled version of [CSS Tidy](http://csstidy.sourceforge.net/). This program is from 2007, and may not have complete support for all CSS3. Consider installing PHP.

### Configuration

Check out `csstidy.sublime-settings` for a documented list of options.

### Installation

#### With Package Control
If you have [Package Control](http://github.com/wbond/sublime_package_control) installed, you can install SublimeCSSTidy from within Sublime Text 2. Open the Command Palette and enter "Package Control: Install Package", then search for *CSSTidy*.

#### Without Package Control
Clone the repository into your Sublime Text 2 packages directory:

    git clone git://github.com/fitnr/SublimeCSSTidy.git

#### Without Package Control or Git
[Go to the download section](http://github.com/fitnr/SublimeCSSTidy/downloads) and download the package. Unzip it, rename the folder *CSSTidy* and move it into your Sublime Text 2 packages directory (*Preferences > Browse Packages* in the menu)

### Problems?
[Submit an issue](https://github.com/fitnr/SublimeCSSTidy/issues).