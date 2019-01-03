"""Interactive gui based on ipywidgets and jupyter notebook."""
import os as _os

from ipywidgets import Dropdown, VBox, Text, Select, Button, HBox, SelectMultiple, Accordion
from IPython.display import display as _display

from knowviz import io as _io
from knowviz import index as _index

long_description_style = {'description_width': 'initial'}


class KeywordDropdown(Dropdown):

    def __init__(self, keyword_index: _index.KeywordIndex, *args, **kwargs):
        """Dropdown menu to select a keyword."""

        super().__init__(*args, **kwargs,
                         options=list(keyword_index.unique_keys()),
                         value=None,
                         description="Select keyword:",
                         style=long_description_style
                         )

        self.keyword_index = keyword_index


class KeywordName(Text):

    def __init__(self, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs,
                         style=long_description_style,
                         description="Name for display:")


class KeywordAccordion(Accordion):

    def __init__(self, **kwargs):
        # access files related to keyword
        self.file_select = Select()
        self.file_open_button = Button(description="Open file", disabled=True)
        self.file_add_button = Button(description="Add file")
        self.filebox = HBox((self.file_select, VBox((self.file_open_button,
                                                     self.file_add_button))))

        # access synonyms
        # TODO: add stuff for synonyms
        self.synonyms_select = SelectMultiple()

        children = (self.filebox, self.synonyms_select)

        super().__init__(children=children,
                         selected_index=None,
                         **kwargs)

        self.set_title(0, "Files")
        self.set_title(1, "Synonyms")


class EditKeywordTab(VBox):

    def __init__(self, keyword_index: _index.KeywordIndex, **kwargs):

        self.keyword_index = keyword_index
        self.keyword_dropdown = KeywordDropdown(keyword_index)
        self.keyword_box = VBox()
        self.keyword_name = Text(style=long_description_style,
                                 description="Name for display:")
        self.keyword_acc = KeywordAccordion()
        self.keyword_info = dict()

        super().__init__(children=(self.keyword_dropdown, self.keyword_box))

        self.keyword_acc.file_open_button.on_click(self.open_selected_file)
        self.keyword_dropdown.observe(self.display_keyword_info, "value")
        self.keyword_acc.file_select.observe(self.enable_file_open_button, type="change")

    def display_keyword_info(self, change):
        self.keyword_box.children = (self.keyword_name, self.keyword_acc)
        self.keyword_info = self.keyword_index.keyword_info(change.new)

        self.keyword_acc.file_select.options = self.keyword_info["files"]
        self.keyword_acc.file_select.index = None
        self.keyword_acc.file_open_button.disabled = True

        self.keyword_acc.synonyms_select.options = self.keyword_info["synonyms"]

        # categories = self.keyword_info["categories"]
        self.keyword_acc.selected_index = None

        if "name" in self.keyword_info:
            self.keyword_name.value = self.keyword_info["name"]
        else:
            self.keyword_name.value = change.new

    def enable_file_open_button(self, change):
        self.keyword_acc.file_open_button.disabled = False

    def open_selected_file(self, b):
        _io.startfile(_os.path.join(self.keyword_index.basedir, self.keyword_acc.file_select.value))
