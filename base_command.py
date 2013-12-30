import sublime, sublime_plugin, re
from .locales_path import LocalesPath

class BaseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not self.in_rails_view():
            self.display_message("This package only works on rails views!")
            return 

        self.settings = sublime.load_settings("I18nRails.sublime-settings")

        self.locales_path = LocalesPath(self.view.file_name())

        self.work()

    # Main method, override
    def work(self):
        pass

    def in_rails_view(self):
        return bool(re.search(r'\.(erb|haml)?$', self.view.file_name()))

    def get_selection_regions(self):
        selection_regions = self.view.sel()

        # If the user didn't select anything create a selection expanding to the nearest scope (hopefully quotes)
        if selection_regions[0].empty():
            self.view.run_command("expand_selection", { "to": "scope" }) 
            selection_regions = self.view.sel()

        return selection_regions

    def add_yml_file_paths_by(self, key):
        # If the text starts with a dot, parse the text and search in ../config/locales/views/folder_name/*.yml, else in ../config/locales/
        self.locales_path.reset()

        if key.startswith("."):
            self.locales_path.move_to_translation_folder()

        try:
            # Store every language (en, es, etc.) with the extension, except for the rejected files
            self.locales_path.add( self.settings.get("rejected_files", []) )
            return True
        except FileNotFoundError:
            self.display_message(self.locales_path.yaml() + " doesn't exist. Are you in a view?")

    # Panels and message
    def display_message(self, text):
        sublime.active_window().active_view().set_status("i18_rails", text)

    def show_quick_panel(self, items, on_done, on_highlighted, selected_index = -1):
        self.view.window().show_quick_panel(items, on_done, sublime.MONOSPACE_FONT, selected_index, on_highlighted)

    def show_input_panel(self, caption, initial_text = "", on_done = None, on_change = None, on_cancel = None):
        self.view.window().show_input_panel(caption, initial_text, on_done, on_change, on_cancel)

    # Files
    def preview_file(self, index):
        self.view.window().open_file(self.files[index], sublime.TRANSIENT)

    def open_file(self, index):
        self.view.window().open_file(self.files[index])

    # Regions
    def add_regions(self, region_name, start, end):
        self.view.add_regions(region_name, start, end, "", sublime.DRAW_NO_FILL)
