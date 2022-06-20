# General utilities for extracting information from MediaWiki and DBPedia
import time
import requests

from anytree import Node, RenderTree
from anytree.exporter import JsonExporter

count = 1


def mediawiki_request(params: dict):
    """
    Wrapper around the MediaWiki API including recovering from session failure
    :param params: params parameter for MediaWiki session request
    :return: raw output
    """
    session = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"
    try:
        data = session.get(url=url, params=params)
    except requests.exceptions.ConnectionError:
        time.sleep(2)
        return mediawiki_request(params)
    return data


def get_pages(category: str):
    """
    Get all pages in a Category
    :param category:
    :return: JSON list with properties 'pageid' and 'title'
    """
    params = {
        "action": "query",
        "cmtitle": category if category.startswith("Category:") else "Category:" + category,
        "cmlimit": 500,
        "list": "categorymembers",
        "format": "json"
    }
    data = mediawiki_request(params).json()
    for page in data["query"]["categorymembers"]:
        # yield page
        yield page["title"]


def get_subcategories(category: str):
    """
    Get all subcategories from a parent category
    :param category:
    :return: string list
    """
    params = {
        "action": "query",
        "cmtitle": category if category.startswith("Category:") else "Category:" + category,
        "cmtype": "subcat",
        "cmlimit": 500,
        "list": "categorymembers",
        "format": "json"
    }
    data = mediawiki_request(params).json()
    for cm in data["query"]["categorymembers"]:
        yield cm["title"].split(":")[1]


def recurse_sc_tree(category: str, depth: int, parent_node: Node):
    """
    Recurse subcategories up to a depth
    :param category: starting category
    :param depth:
    :param parent_node: current parent node
    :return:
    """
    global count

    # base case
    if depth < 0:
        return

    # call query
    subcategories = get_subcategories(category)
    print(count, category)
    count += 1
    for sc in subcategories:
        child_node = Node(sc, parent=parent_node)
        recurse_sc_tree(sc, depth - 1, child_node)


if __name__ == '__main__':
    import os

    depth = 2
    root = Node("Software")

    # Recursively get subcategories from defined root
    recurse_sc_tree("Software", depth, root)

    # Pretty print
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    # Anytree Exporter
    exporter = JsonExporter(indent=2, sort_keys=True)
    fname = os.path.join(os.getcwd(), "data/software.json")
    with open(fname, "w") as fh:
        exporter.write(root, fh)
