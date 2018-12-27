if __name__ == "__main__":

    from knowviz import index

    changed = index.update_model_index("data/")
    if changed:
        print("Models index has been updated.")
    else:
        print("Nothing has changed.")
