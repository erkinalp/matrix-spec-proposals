#! /usr/bin/env python

from docutils.core import publish_file
import fileinput
import glob
import os
import shutil
import subprocess
import sys

stylesheets = {
    "stylesheet_path": ["basic.css", "nature.css"]
}

def glob_spec_to(out_file_name):
    with open(out_file_name, "wb") as outfile:
        for f in sorted(glob.glob("../specification/*.rst")):
            with open(f, "rb") as infile:
                outfile.write(infile.read())


def rst2html(i, o):
    with open(i, "r") as in_file:
        with open(o, "w") as out_file:
            publish_file(
                source=in_file,
                destination=out_file,
                reader_name="standalone",
                parser_name="restructuredtext",
                writer_name="html",
                settings_overrides=stylesheets
            )

def run_through_template(input):
    null = open(os.devnull, 'w')
    subprocess.check_output(
        [
            'python', 'build.py', 
            "-i", "matrix_templates", 
            "-o", "../scripts/tmp", 
            "../scripts/"+input
        ],
        stderr=null,
        cwd="../templating",
    )

def prepare_env():
    try:
        os.makedirs("./gen")
    except OSError:
        pass
    try:
        os.makedirs("./tmp")
    except OSError:
        pass
    
def cleanup_env():
    shutil.rmtree("./tmp")

def main():
    prepare_env()
    glob_spec_to("tmp/full_spec.rst")
    run_through_template("tmp/full_spec.rst")
    shutil.copy("../supporting-docs/howtos/client-server.rst", "tmp/howto.rst")
    run_through_template("tmp/howto.rst")
    rst2html("tmp/full_spec.rst", "gen/specification.html")
    rst2html("tmp/howto.rst", "gen/howtos.html")
    cleanup_env()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # we accept no args, so they don't know what they're doing!
        print "gendoc.py - Generate the Matrix specification as HTML."
        print "Usage:"
        print "  python gendoc.py"
        print ""
        print "The specification can then be found in the gen/ folder."
        print ""
        print "Requirements:"
        print " - This script requires Jinja2 and rst2html (docutils)."
        sys.exit(0)
    main()
