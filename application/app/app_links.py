import os
import re
from contextlib import contextmanager


path_to_links = os.path.abspath("application")
s = re.search("application", path_to_links)
app_path = path_to_links.replace(path_to_links[s.end():], "")


@contextmanager
def raise_error(relative_url):
    is_dir = os.path.exists(os.path.join(app_path, relative_url))
    if not is_dir:
        raise ImportError("Wrong directory is provided")
    yield


def get_folder(rel_uri):
    with raise_error(rel_uri):
        return os.path.join(path_to_links, rel_uri)


if os.path.exists(app_path):
    template_folder = get_folder("templates")
    static_folder = get_folder("static")
    logging_folder = get_folder("logs")
else:
    raise ImportError("Put file with links into application's folders")
