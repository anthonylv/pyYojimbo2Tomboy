#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Walk a directory structure to find files

Skeleton code to walk through a directory structure to find files.
"""
import sys, getopt, os, time
import os.path
import logging
import logging, logging.handlers
from datetime import datetime
from bs4 import BeautifulSoup
import yaml

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
        logging.error("The directory %s already exists", path)
  

def crawl_yojimbo_sidekick(crawler_settings):
    """Crawl the Yojimbo Sidekick export directory.
    """
    root_dir = crawler_settings['root_dir']
    #Use generator to walk through all subdirectories
    for subdirectories, directories, files in os.walk(root_dir):         
        for fname in files:
            if fname.endswith('.html') and not fname.startswith('.'):
                logging.debug("Parsing %s", fname)
                filepath = os.path.join(subdirectories, fname)
                title, body = get_yojimbo_note(filepath)
                
                #print title
                #print body
            else:
                logging.warning("File skipped: %s", fname ) 


def get_yojimbo_note(filename):
    """Get content from a Yojimbo Sidekick note.
    
    There are two types of notes marked by the body class:
    * note
    * web_archive
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


def write_tomboy_note(title, body):
    iso_time = datetime.utcnow().isoformat()
    last_change_date = iso_time
    last_metadata_change_date = iso_time
    create_date = iso_time

    template_path = os.path.dirname(os.path.abspath(__file__))    

    env = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join(template_path, 'templates')),
        trim_blocks=False)

    fname = "output/index.html"
    context = {
        'content_dict': content_dict,
        'content_body': content_body
    }
    with open(fname, 'w') as f:
        html = env.get_template('index.html').render(context)
        f.write(html.encode('utf8'))


def main(argv):
    """Process the user's commands.

    Args:
        argv: The command line options.
    """
    settings = get_settings()
    setup_logging(settings['logger'])
    logging.info("Starting")
    
    crawler_settings = settings['crawler']
    crawl_yojimbo_sidekick(crawler_settings)
    #get_yojimbo_note('source.html')
                    
    #export_dir = settings['writer']['export_dir']
    #create_directory(export_dir)
    
    exit(0)


# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
