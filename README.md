__this tool is still in pre-alpha state and not ready for productive use__

# knowviz
Document-based knowledge management and visualization tool for _keywords_ (e.g. physical quantities) and _relations_ (e.g. physical models) that connect quantities.

## Knowledge management

_Knowledge_ is stored in documents, one or more for each keyword or relation. Keywords are treated as independent and unique entities. Keywords are names that can have synonyms and categories. Each synonym or name must be connected to only one keyword. Relations are meant to establish links between keywords. This is achieved by parsing the human-readable documents storing relation information and search for text-occurances of keywords. 

The underlying document-based database is based on `YAML (1.2)` files. It can thus be tracked (and synced) with version control (e.g. git). The database can be accessed either with the Python API or using the interactive gui based on `jupyter notebooks` and `ipywidgets`.

## Knowledge visualisation

__work in progress__

# Version history

See [wiki page](https://github.com/dafrose/knowviz/wiki/Version-history)
