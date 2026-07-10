published_links = set()


def is_published(link):
    return link in published_links


def mark_as_published(link):
    published_links.add(link)
