__author__ = 'andrei'

class Tab(object):
    def __init__(self, slug, name, url, icon, order, access_descriptor=None):
        self.slug = slug
        self.name = name
        self.url = url
        self.icon = icon
        self.order = order
        self.access_descriptor = access_descriptor