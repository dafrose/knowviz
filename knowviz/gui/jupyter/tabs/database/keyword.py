"""Interactive gui based on ipywidgets and jupyter notebook."""
import os as _os

from ipywidgets import Dropdown as _Dropdown, VBox as _VBox, Text as _Text, Select as _Select
from ipywidgets import Button as _Button, HBox as _HBox, SelectMultiple as _SelectMultiple, Accordion as _Accordion

import traitlets as _traitlets
from tkinter import Tk as _Tk, filedialog as _filedialog

from knowviz import io as _io
from knowviz import index as _index

long_description_style = {'description_width': 'initial'}


class KeywordDropdown(_Dropdown):

    def __init__(self, keyword_index: _index.KeywordIndex, *args, **kwargs):
        """Dropdown menu to select a keyword."""

        super().__init__(*args, **kwargs,
                         options=list(keyword_index.unique_keys()),
                         value=None,
                         description="Select keyword:",
                         style=long_description_style
                         )

        self.keyword_index = keyword_index


class KeywordName(_Text):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         style=long_description_style,
                         description="Name for display:")

    def refresh(self, name: str = "", disable: bool = False):

        if disable:
            self.disabled = True
        else:
            self.disabled = False

        if name is "":
            self.value = ""
            self.placeholder = "Add custom display name here"
        else:
            self.value = name


class KeywordInfoBox(_VBox):

    def __init__(self, keyword_index: _index.KeywordIndex, **kwargs):

        self.keyword_index = keyword_index

        self.keyword_name = KeywordName()
        self.keyword_acc = KeywordAccordion(keyword_index)

        super().__init__(children=(self.keyword_name, self.keyword_acc), **kwargs)

        self.refresh(disable=True)

    def refresh(self, keyword_info: dict = None, disable: bool = False):

        if keyword_info is None:
            keyword_info = {}

        if disable:
            for child in self.children:
                child.refresh(disable=True)
        else:
            self.keyword_name.refresh(keyword_info.get("name", ""))
            self.keyword_acc.refresh(keyword_info)


class KeywordAccordion(_Accordion):

    def __init__(self, keyword_index: _index.KeywordIndex, **kwargs):
        # access files related to keyword
        self.keyword_index = keyword_index
        self.file_select = _Select()
        self.file_open_button = _Button(description="Open file", disabled=True)
        self.file_add_button = SelectFilesButton(description="Attach file(s)")
        self.file_remove_button = _Button(description="Detach file", disabled=True)
        self.filebox = _HBox((self.file_select, _VBox((self.file_open_button,
                                                       self.file_add_button,
                                                       self.file_remove_button))))

        # access synonyms
        # TODO: add stuff for synonyms
        self.synonyms_select = _SelectMultiple()

        children = (self.filebox, self.synonyms_select)

        super().__init__(children=children,
                         selected_index=None,
                         **kwargs)

        self.set_title(0, "Files")
        self.set_title(1, "Synonyms")

        self.file_select.observe(self.on_file_selection_change, "value")
        self.file_select.observe(self.on_file_list_change, "options")
        self.file_open_button.on_click(self.open_selected_file)
        self.file_add_button.observe(self.add_files, "files")
        self.file_remove_button.on_click(self.detach_selected_file)

        self.refresh()

    def on_file_selection_change(self, change):
        if change.new is not None:
            self.file_open_button.disabled = False
            self.file_remove_button.disabled = False

    def on_file_list_change(self, change):
        self.file_select.index = None
        self.file_open_button.disabled = True
        self.file_remove_button.disabled = True

    def open_selected_file(self, b):
        _io.startfile(_os.path.join(self.keyword_index.basedir, self.file_select.value))

    def detach_selected_file(self, b):
        self.file_select.options = [file for file in self.file_select.options if file != self.file_select.value]

    def add_files(self, change):
        self.file_select.options = [*self.file_select.options, *change.new]

    def refresh(self, keyword_info: dict = None, disable: bool = False):

        if keyword_info is None:
            keyword_info = {}
        else:
            keyword_info = keyword_info

        if disable:
            self.file_add_button.disabled = True
        else:
            self.file_add_button.disabled = False

        self.file_select.options = keyword_info.get("files", [])
        # this should trigger `on_file_list_changed` and refresh related states

        self.synonyms_select.options = keyword_info.get("synonyms", [])
        self.synonyms_select.index = ()


class KeywordTab(_VBox):

    def __init__(self, keyword_index: _index.KeywordIndex, **kwargs):
        self.keyword_index = keyword_index
        self.keyword_dropdown = KeywordDropdown(keyword_index)
        self.keyword_box = KeywordInfoBox(keyword_index)

        super().__init__(children=(self.keyword_dropdown, self.keyword_box), **kwargs)

        self.keyword_dropdown.observe(self.display_keyword_info, "value")

    def display_keyword_info(self, change):
        # collect keyword info and hand over to keyword info box
        keyword_info = self.keyword_index.keyword_info(change.new)
        self.keyword_box.refresh(keyword_info)


class SelectFilesButton(_Button):
    """Acknowledgement: This class is based on this code review:
    https://codereview.stackexchange.com/questions/162920/file-selection-button-for-jupyter-notebook

    A file widget that leverages tkinter.filedialog."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add the selected_files trait
        self.add_traits(files=_traitlets.traitlets.List())
        # Create the button and apply defaults
        if self.description is "":
            self.description = "Select Files"
        # self.icon = "square-o"
        # self.style.button_color = "orange"
        # Set on click behavior.
        self.on_click(self.select_files)

    @staticmethod
    def select_files(b):
        """Generate instance of tkinter.filedialog.

        Parameters
        ----------
        b : obj:
            An instance of ipywidgets.widgets.Button
        """
        # Create Tk root
        root = _Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call('wm', 'attributes', '.', '-topmost', True)
        # List of selected files will be set to b.value
        b.files = _filedialog.askopenfilename(multiple=True)

        # b.description = "Files attached"
        # b.icon = "check-square-o"
        # b.style.button_color = "lightgreen"

    @staticmethod
    def initial_state(b):
        b.files = []
