"""Interactive gui based on ipywidgets and jupyter notebook."""
import os as _os

from ipywidgets import Dropdown, VBox, Text, Select, Button, HBox, SelectMultiple, Accordion
from IPython.display import display as _display

from knowviz import io as _io


def keyword_info_gui(index):
    # select a keyword

    style = {'description_width': 'initial'}
    select_keyword = Dropdown(options=list(index.unique_keys()),
                              value=None,
                              description="Select keyword:",
                              style=style)

    # edit keyword properties
    keyword_edit_box = VBox()
    keyword_name = Text(style=style, description="Name for display:")
    select_files = Select()
    file_open_button = Button(description="Open file", disabled=True)
    file_add_button = Button(description="Add file")
    file_box = HBox((select_files, VBox((file_open_button,
                                         file_add_button))))

    select_synonyms = SelectMultiple()
    keyword_acc = Accordion(children=(file_box, select_synonyms), selected_index=None)
    keyword_acc.set_title(0, "Files")
    keyword_acc.set_title(1, "Synonyms")

    edit_keyword_info = VBox([select_keyword, keyword_edit_box])

    def on_keyword_selected(change):
        keyword_edit_box.children = (keyword_name, keyword_acc)
        keyword_info = index.keyword_info(change.new)
        select_files.options = keyword_info["files"]
        select_files.index = None
        file_open_button.disabled = True
        select_synonyms.options = keyword_info["synonyms"]
        categories = keyword_info["categories"]
        keyword_acc.selected_index = None
        if "name" in keyword_info:
            keyword_name.value = keyword_info["name"]
        else:
            keyword_name.value = change.new

    def on_file_selected(change):
        file_open_button.disabled = False

    def on_file_open_button_clicked(b):
        _io.startfile(_os.path.join(index.basedir, select_files.value))

    file_open_button.on_click(on_file_open_button_clicked)
    select_keyword.observe(on_keyword_selected, "value")
    select_files.observe(on_file_selected, type="change")

    _display(edit_keyword_info)
