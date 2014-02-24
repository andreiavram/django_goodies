from django.template.loader import render_to_string

__author__ = 'andrei'


class ContextMenuItem(object):
    menu_type = "item"

    def __init__(self, title, url=None, icon=None, disabled=False, access_descriptor=None, order=None):
        self.title = title
        self.url = url
        self.icon = icon
        self.disabled = disabled
        self.access_descriptor = access_descriptor
        self.order = order if order else 0
        self.rendered_html = ""

    def render(self):
        if self.rendered_html:
            return self.rendered_html

        self.rendered_html = render_to_string("goodies/context_menu_item.html", context={"menu_item": self})
        return self.rendered_html


class ContextMenuContainer(object):
    menu_type = "container"

    def __init__(self, title, menu_items=[], icon=None, order=None):
        self.menu_items = menu_items[:]
        self.title = title
        self.order = order if order else 0
        self.rendered_html = ""

    def add_menu_item(self, item):
        self.menu_items.append(item)
        self.menu_items.sort(key=lambda i: i.order)

    def render(self):
        if self.rendered_html:
            return self.rendered_html

        self.rendered_html = render_to_string("goodies/context_menu_container.html", context={"menu_container": self})
        return self.rendered_html


class ContextMenu(object):
    menu_items = []
    rendered_html = ""

    @classmethod
    def build_menu(cls, *args, **kwargs):
        return

    @classmethod
    def enforce_permissions(cls, request, *args, **kwargs):
        return

    @classmethod
    def render(cls):
        if cls.rendered_html:
            return cls.rendered_html
        cls.rendered_html = render_to_string("goodies/context_menu_main.html", context={"menu": cls})

    @classmethod
    def get_context_contribution(cls, request, *args, **kwargs):
        cls.build_menu(*args, **kwargs)
        cls.enforce_permissions(request, *args, **kwargs)

        return {"context_menu": cls}