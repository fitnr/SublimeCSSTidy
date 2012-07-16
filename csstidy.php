<?php 

// Includes

include 'csstidyphp/class.csstidy.php' ;

// Options

$long_options = array(
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
);

// Get arguments

$args = getopt("", $long_options);

var_dump($GLOBALS['argv']);
var_dump($args);

// Create tidier

$css = new csstidy();

// Set config options

for ($option in $long_options):

  if isset($args[$option]):
    $css->set_cfg($option, $args[$option]);
  endif;

endfor;

// read and write from pipe

$css->parse(STDIN);
fwrite(STDOUT, $css->print->formatted());

/*
// Is there an error handler in csstidy.php? who knows?

if ( SOME_KIND_OF_ERROR_OPTION ) {
    fwrite(STDERR, $css->errors);
}
*/

?>