#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Migrate Bare Bones Yojimbo Notes to Tomboy Note format.

Usage: yojimbo2tomboy.py

"""
import sys, getopt, os, time
import os.path
import logging
import logging, logging.handlers
from datetime import datetime
from bs4 import BeautifulSoup
import yaml
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger()


def get_settings():
    """Get settings from external YAML file
    """
    settings = {}
    try:
        with open("settings.yml", 'r') as ymlfile:
            settings = yaml.load(ymlfile)
    except IOError:
        logger.error("Could not open settings file")
    else:
        logger.debug("Opened settings file")

    return settings


def setup_logging(settings):
    """Log output

        Sends log output to console or file,
        depending on error level
    """
    try:
        log_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            settings['log_filename']
        )
        log_max_bytes = settings['log_max_bytes']
        log_backup_count = settings['log_backup_count']
    except KeyError as ex:
        print "WARNING: Missing logfile setting {}. Using defaults.".format(ex)
        log_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "log.txt"
        )
        log_max_bytes = 1048576 #1MB
        log_backup_count = 5

    logger.setLevel(logging.DEBUG)
    # Set up logging to file
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_filename,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
        '%m-%d %H:%M'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Handler to write INFO messages or higher to sys.stderr
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    logger.debug("------------------------------")
    logger.debug(
        "Starting log for session %s",
        datetime.now().strftime("%Y%m%d%H%M%S%f")
    )


def create_directory(path):
    """Create a directory.

    Args:
        path: Path to the project location.    
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            logging.error(
                "Sorry there was a problem creating the directory: %s",
                e.strerror)
            if not path:
                logging.error("The path string is empty")
    else:
        logging.info("The directory %s already exists", path)
  

def crawl_yojimbo_sidekick(source_dir, export_dir):
    """Crawl the Yojimbo Sidekick export directory.
    
    Crawl the Yojimbo Sidekick export directory looking for
    only .html files and ignore dot files. Write in Tomboy note format.
    """
    accepted = 0
    skipped = 0
    if os.path.exists(source_dir):
        for subdirectories, directories, files in os.walk(source_dir):
            for fname in files:
                if fname.endswith('.html') and not fname.startswith('.'):
                    logging.debug("Parsing %s", fname)
                    filepath = os.path.join(subdirectories, fname)
                    title, body = get_yojimbo_note(filepath)
                    notefname = os.path.splitext(fname)[0]+'.note'               
                    write_tomboy_note(title, body, export_dir, notefname)
                    accepted += 1
                else:
                    skipped += 1
                    logging.warning("File skipped: %s", fname )
    else:
        logging.error("Can't find source directory: %s", root_dir)
    logging.info("Files processed: %s", accepted)
    logging.info("Files skipped: %s", skipped)


def get_yojimbo_note(filename):
    """Get content from a Yojimbo Sidekick note.
    """
    title = None
    body = None
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except IOError:
        logger.error("Could not open %s", filename)
    else:
        logger.debug("Opened settings file")
        title, body = parse_yojimbo_note(content)

    return title, body


def parse_yojimbo_note(note_content):
    """Parse the content of a Yojimbo note file.
    
    There are two types of notes marked by the body class:
    * note
    * web_archive
    """
    content = BeautifulSoup(note_content, 'html.parser')
    title = None
    body = None
    # Find note title in the first h2 of the values div
    try:
        title = content.select('#values h2')[0].text
    except IndexError:
        logging.warning("No title for %s", filename)

    if 'note' in content.body['class']:
        logging.debug("Found a Note item")
        # Find note body in the first note_body ID
        try:
            body =  content.select('#note_body')[0].text
        except IndexError:
            logging.warning("No body for %s", filename)
    elif 'web_archive' in content.body['class']:            
        logging.debug("Found a Web archive")
        try:
            body =  content.select('.value a')[0].text
        except IndexError:
            logging.warning("No body for %s", filename)
    else:
        logging.info("Unknown note type")
                
    return title, body


def write_tomboy_note(title, body, export_dir, filename):
    """Write a Tomboy note in XML format to export directory.
    """
    iso_time = datetime.utcnow().isoformat()
    last_change_date = iso_time
    last_metadata_change_date = iso_time
    create_date = iso_time

    template_path = os.path.dirname(os.path.abspath(__file__))    

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(template_path, 'templates')),
        trim_blocks=False)

    output_path = os.path.join(export_dir, filename)
    context = {
        'title': title,
        'body': body,
        'last_change_date': last_change_date,
        'last_metadata_change_date': last_metadata_change_date,
        'create_date': create_date
    }
    logging.debug("Creating note at %s", output_path)

    with open(output_path, 'w') as f:
        html = env.get_template('tomboy-note.xml').render(context)
        f.write(html.encode('utf8'))


def write_tomboy_notebook_template(export_dir):
    """Write a Tomboy note in XML format to export directory.
    """
    iso_time = datetime.utcnow().isoformat()
    last_change_date = iso_time
    last_metadata_change_date = iso_time
    create_date = iso_time

    template_path = os.path.dirname(os.path.abspath(__file__))    

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(template_path, 'templates')),
        trim_blocks=False)

    output_path = os.path.join(export_dir, 'tomboy-notebook-template.note')
    context = {
        'last_change_date': last_change_date,
        'last_metadata_change_date': last_metadata_change_date,
        'create_date': create_date
    }
    logging.debug("Creating note at %s", output_path)

    with open(output_path, 'w') as f:
        html = env.get_template('tomboy-notebook.xml').render(context)
        f.write(html.encode('utf8'))


def main(argv):
    """Process the user's commands.

    Args:
        argv: The command line options.
    """
    settings = get_settings()
    setup_logging(settings['logger'])
    logging.info("Starting")
    
    export_dir = settings['writer']['export_dir']
    create_directory(export_dir)
    write_tomboy_notebook_template(export_dir)

    crawler_root_dir = settings['crawler']['root_dir']
    crawl_yojimbo_sidekick(crawler_root_dir, export_dir)
    """
    # Test one item
    title, body = get_yojimbo_note('sample-source.html')
    write_tomboy_note(title, body, export_dir, 'sample.xml')
    """
    logging.info("Export complete")
    exit(0)


# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
