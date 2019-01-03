if __name__ == "__main__":

    from knowviz import index

    quantities = index.KeywordIndex("data/metadata/quantities.yml")
    models = index.RelationIndex(quantities, "data/metadata/models.yml")

    changed = quantities.rescan_documents(overwrite_file=True)
    if changed:
        print("Quantities index has been updated.")
    else:
        print("Nothing has changed.")

    changed = models.rescan_documents(overwrite_file=True)
    if changed:
        print("Models index has been updated.")
    else:
        print("Nothing has changed.")
