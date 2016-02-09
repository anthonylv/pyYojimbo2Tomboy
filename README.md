# Yojimbo to Tomboy migration tool

A Python tool for migrating [Yojimbo](http://www.barebones.com/products/yojimbo/) notes to the GNOME [Tomboy](https://wiki.gnome.org/Apps/Tomboy) desktop note-taking application.

[More information](http://anothercoffee.net/yojimbo-to-tomboy-notes-migration-tool) about why I created the tool.

## Limitations

This current version scrapes the content from Yojimbo's [Sidekick export](http://www.barebones.com/products/yojimbo/tour-sidekick.html) and converts the pages to Tomboy's XML format. Sidekick does not export all your Yojimbo note's metadata but you will be able to save the title and note body. Time permitting, I would like to find a way to save tag data in a future version.


## Requirements, setup and usage

* Python 2.7
* pip install -r requirements.txt

1. Grab the script files and install the required modules
1. [Follow the instructions](http://www.barebones.com/products/yojimbo/tour-sidekick.html) to export your Sidekick pages from Yojimbo. Make sure the export worked and you can browse the pages through your web browser.
1. Along with the Yojimbo2Tomboy script files, you'll fine a `settings-template.yml`. Rename it to `settings.yml`.
1. In the `settings.yml` file, set the `crawler:root_dir:` setting to your Yojimbo Sidekick `contents` directory. For example, if you created Sidekick in `/Users/username/Sites/Yojimbo`, you'll need to set it to `/Users/username/Sites/Yojimbo/contents`. You might want to copy the `contents` folder to a temporary location and run the crawler there.
1. In the `settings.yml` file, set the `writer:export_dir:` setting to the directory for the Tomboy notes files.

### Usage

Run:

`$ python yojimbo2tomboy.py`

### Copying to Tomboy

1. Quit Tomboy if it's running.
1. Copy the files in your export directory to Tomboy's notes directory. For example, in Linux mint you'll find it in `/home/username/.local/share/tomboy
1. Restart Tomboy and you should see the Yojimbo notes organised in the *YojimboSidekick* notebook.

Thi script uses the same basename and the Yojimbo Sidekick HTML files. Tomboy uses a different naming convention so it's unlikely you'll encounter problems with overwriting any existing Tomboy notes.


## Reminder
Remember to backup your Tomboy notes and Yojimbo Sidekick content before running this tool.

## License
Written by Anthony Lopez-Vito of [Another Cup of Coffee Limited](http://anothercoffee.net). All code is released under The MIT License.
Please see LICENSE.txt.