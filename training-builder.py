#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import yaml
import jinja2
import subprocess
import argparse
import fnmatch

from pprint import pprint



def jinja2_basename_filter(path):
    return os.path.basename(path)



def render_template(tpl_path, context):
    path, filename = os.path.split(
        tpl_path
    )
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    )
    env.filters['basename'] = jinja2_basename_filter
    return env.get_template(filename).render(context)



def build_html(source_file, dest_file, commons_dir):
    pandoc_cmd_arr = [
        "pandoc",
        "--to",
        "revealjs",
        "--template",
        "{0}/revealjs-template.pandoc".format(
            commons_dir
        ),
        "--standalone",
        "--section-divs",
        "--no-highlight",
        source_file,
        "-o",
        dest_file
    ]
    subprocess.check_call(pandoc_cmd_arr)



def build_pdf(source_file, dest_file, commons_dir, build_path):

    temp_html_file = "{0}/{1}.tmp.html".format(
        os.path.dirname( dest_file ),
        os.path.basename( dest_file )
    )

    # create a html that works with pdf css
    pandoc_cmd_arr = [
        "pandoc",
        "-c",
        "../../commons/pdf/style.css",
        source_file,
        "-o",
        temp_html_file
    ]
    subprocess.check_call(pandoc_cmd_arr)

    # then convert this to html
    wkhtmltopdf_cmd_arr = [
        "wkhtmltopdf",
        "--page-width",
        "200",
        "--page-height",
        "145",
        temp_html_file,
        dest_file
    ]
    subprocess.check_call(wkhtmltopdf_cmd_arr)

    # delete temp file
    #os.remove(temp_html_file)



def find_training_yaml(root_dir, commons_dir, build_dir):
    try:
        _index_files = glob.glob(
            "{0}/**/*yml".format(
                root_dir
            ),
            recursive = True
        )
    # python < 3.5
    except TypeError:
        _index_files = []
        for root, dirnames, filenames in os.walk(root_dir):
            for filename in fnmatch.filter(filenames, "*.yml"):
                _index_files.append(os.path.join(root, filename))

    # remove unwanted files from build/comons
    index_files = []
    for f in _index_files:
        if not f.startswith(commons_dir) and not f.startswith(build_dir):
            index_files.append(f)

    return index_files



def main():

    parser = argparse.ArgumentParser(
        description='Training builder'
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory of training sources"
    )
    parser.add_argument(
        "--commons",
        default="adsy-trainings-common.src",
        help="Common files location"
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        help="Output directory"
    )
    parser.add_argument(
        "--ignore",
        action="append",
        help="Ignore training"
    )
    parser.add_argument(
        "--index-only",
        action="store_true",
        default=False,
        help="Only build index, no content"
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        default=False,
        help="Skip PDF building"
    )


    args = parser.parse_args()

    root_dir = os.path.realpath(args.root)
    commons_dir_abs = os.path.realpath(args.commons)
    build_dir = os.path.realpath(args.build_dir)
    if not args.ignore:
        args.ignore = []


    index_files = find_training_yaml(
        root_dir,
        commons_dir_abs,
        build_dir
    )
    training_list = {}

    ## Copy commons files first for phantom
    subprocess.check_call([
        "cp",
        "-ra",
        commons_dir_abs,
        "{0}/commons".format(
            build_dir,
        )
    ])


    for yaml_file in sorted(index_files):

        training_dir = os.path.dirname( os.path.relpath(yaml_file, root_dir) )

        rdir = training_dir.split("/")[0]
        if rdir in args.ignore:
            continue

        source_dir = "{0}/{1}".format(
            root_dir,
            training_dir
        )
        build_path = "{0}/{1}".format(
            build_dir,
            training_dir
        )
        build_path_root_abs = build_dir

        yf = open(yaml_file, encoding="utf-8")
        training_yaml = yaml.load(yf)

        training_dict = {
            "category": training_yaml['Area'],
            "name": training_yaml['Name'],
            "description": training_yaml['Description'],
            "files_html": [],
            "files_pdf": []
        }
        if training_yaml['Area'] not in training_list:
            training_list[training_yaml['Area']] = []

        print("Building: {0}".format(training_dir))

        # Find all Markdown files in currend dir
        os.makedirs( build_path, exist_ok=True )
        markdown_files = glob.glob(
            "{0}/*md".format(source_dir)
        )

        # Build HTML files from Markdown
        for md in markdown_files:
            fname_no_ext = os.path.splitext(
                os.path.basename( md )
            )[0]
            html_build_file = "{0}/{1}.html".format(
                build_path,
                fname_no_ext
            )
            pdf_build_file = "{0}/{1}.pdf".format(
                build_path,
                fname_no_ext
            )

            training_dict['files_html'].append(
                "{0}/{1}.html".format(
                    training_dir,
                    fname_no_ext
                )
            )
            print("   > {0}.html".format(fname_no_ext))
            if args.index_only:
                continue
            build_html(md, html_build_file, commons_dir_abs)


        # copy image dirs
        static_dirs = [ name for name in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, name)) ]
        for sdir in static_dirs:
            src = "{0}/{1}/{2}".format(
                root_dir,
                training_dir,
                sdir
            )
            dst = "{0}/{1}/{2}".format(
                build_dir,
                training_dir,
                sdir
            )
            subprocess.check_call([
                "cp",
                "-ra",
                src,
                dst
            ])


        # then build pdf from generated html
        for htmlf in training_dict['files_html']:
            fname_no_ext = os.path.splitext(
                os.path.basename( htmlf )
            )[0]
            html_build_file = "{0}/{1}.html".format(
                build_path,
                fname_no_ext
            )
            pdf_output = "{0}/{1}.pdf".format(
                build_path,
                fname_no_ext
            )
            print("   > {0}.pdf".format(fname_no_ext))
            if not args.index_only and not args.no_pdf:
                build_pdf(
                    html_build_file,
                    pdf_output,
                    commons_dir_abs,
                    build_path_root_abs
                )

            training_dict['files_pdf'].append(
                "{0}/{1}.pdf".format(
                    training_dir,
                    fname_no_ext
                )
            )

        # append to dict for index file
        training_dict['files_html'] = sorted(training_dict['files_html'])
        training_dict['files_pdf']  = sorted(training_dict['files_pdf'])
        training_list[training_yaml['Area']].append(training_dict)


    ## Build the index template
    context = {
         "training_list": training_list
    }

    _tpl_path = "{0}/index/template.html".format(commons_dir_abs)


    output_index_html = render_template(_tpl_path, context)

    output_index = "{0}/index.html".format(
        build_dir
    )

    file_object  = open(output_index, "w", encoding="utf-8")
    file_object.write(
        output_index_html
    )







if __name__ == '__main__':
    main()
