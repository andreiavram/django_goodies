from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

__author__ = 'andrei'


class ContextMenuItem(object):
    menu_type = "item"

    def __init__(self, title, url=None, icon=None, disabled=False, access_descriptor=None, order=None, active=False, modifier=None, badge=None):
        self.title = title
        self.url = url
        self.icon = icon
        self.disabled = disabled
        self.access_descriptor = access_descriptor
        self.order = order if order else 0
        self.active = active
        self.modifier = modifier
        self.badge = badge


class ContextMenuContainer(object):
    menu_type = "container"

    def __init__(self, title=None, menu_items=[], icon=None, order=None):
        self.title = title
        self.order = order if order else 0
        self.icon = icon

        self.menu_items = []
        for item in menu_items:
            self.add_menu_item(item)

    def add_menu_item(self, item):
        self.menu_items.append(item)
        self.menu_items.sort(key=lambda i: i.order)


class ContextMenu(object):
    menu_items = []
    type = "context"

    @classmethod
    def build_menu(cls, *args, **kwargs):
        return

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ContextMenu, self).__init__()

    def enforce_permissions(self, request, *args, **kwargs):
        return

    def render(self):
        html = render_to_string(self.get_template(), {"menu": self})
        return mark_safe(html)

    def as_html(self):
        return self.render()

    def get_menu_type(self):
        return self.type

    def get_template(self):
        return "goodies/%s_menu.html" % self.get_menu_type()

