"""Main entrypoint for jupyter-notebook-based GUI."""

from ipywidgets import Tab as _Tab


class RootWidget(_Tab):

    def __init__(self, **kwargs):
        children = ()
        super().__init__(children, **kwargs)
