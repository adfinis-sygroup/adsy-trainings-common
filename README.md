TRAINING COMMON STUFF
=====================

This repository contains the common boilerplate to build presentations with
pandoc and revealjs.


BUILD NEW PRESENTATION
----------------------
To create a new presentation with this framework, you need to create a new
git repository and add this repository as a git submodule.

    git init
    git submodule add https://github.com/adfinis-sygroup/adsy-trainings-common commons

Create a ``Makefile`` with the following content (be aware of the correct path
to the pandoc template).

    SOURCES = $(wildcard *.md)
    SLIDES  = $(SOURCES:.md=.html)

    .PHONY: all clean

    all: $(SLIDES)

    %.html: %.md
    	@echo "building $@ from $<" && \
    	pandoc \
    	--to revealjs \
    	--template commons/revealjs-template.pandoc \
    	--standalone \
    	--section-divs \
    	--no-highlight \
    	$< \
    	-o $@

    clean:
    	-rm -f *.html *.pdf

And create some content (saved in a file with ending ``.md``) written in markdown
(pandoc flavor).

    # Skeleton

    # Attribution / License

    * Slides
      Creative Commons Attribution-Share Alike 3.0 Unported license ("CC-BY-SA")

    ---

    ## Feel Free to Contact Us

    [www.adfinis-sygroup.ch](https://www.adfinis-sygroup.ch)

    [Tech Blog](https://www.adfinis-sygroup.ch/blog)

    [GitHub](https://github.com/adfinis-sygroup)

    <info@adfinis-sygroup.ch>

    [Twitter](https://twitter.com/adfinissygroup)

To build your slides, use ``make``

    $ make
    building presentation.html from presentation.md
