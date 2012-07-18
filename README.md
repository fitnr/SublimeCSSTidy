# CSS code formatter for Sublime Text 2

## What is does
CSSTidy is a [Sublime Text 2](http://www.sublimetext.com/2) package for cleaning and tidying up your CSS 2. It doesn't work as well with CSS 3, but it won't break anything. It uses [CSS Tidy](http://csstidy.sourceforge.net/), which is now a [PHP Library](http://github.com/Cerdic/CSSTidy)

CSSTidy adds three commands to the Sublime Text 2 command palette: "CSS Tidy (Highest)", and "CSS Tidy (Low), "CSS Tidy"". The last one uses the default template. If you can decipher the complicated patten for creating [custom formatting rules](http://csstidy.sourceforge.net/templates.php), CSSTidy will happily use them.

## Installation

### With Package Control
If you have [Package Control][package_control] installed, you can install CSSTIdy from within Sublime Text 2. Open the Command Palette and select "Package Control: Install Package", then search for CSSTidy.

### Without Package Control
Go to your Sublime Text 2 Packages directory (by selecting "Preferences > Browse Packages") and clone the repository there:
  
    git clone git://github.com/netpro2k/SublimeBlockCursor

## Configuration
Check out `csstidy.sublime-settings` for a documented list of options.