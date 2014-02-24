__author__ = 'andrei'


class Tab(object):
    def __init__(self, slug, name, url, icon, order, access_descriptor=None):
        self.slug = slug
        self.name = name
        self.url = url
        self.icon = icon
        self.order = order
        self.access_descriptor = access_descriptor


class TabSet(object):
    tabs = []

    @classmethod
    def has_tab(cls, search_tab, **kwargs):
        return any(t.slug == search_tab for t in cls.tabs)

    @classmethod
    def init_tabs(cls, *args, **kwargs):
        return

    @classmethod
    def enforce_permissions(cls, request, *args, **kwargs):
        cls.tabs = [t for t in cls.tabs if t.access_descriptor and t.access_descriptor(request, *args, **kwargs)]

    @classmethod
    def get_context_contribution(cls, request, *args, **kwargs):
        #   init_tabs
        cls.init_tabs(request, *args, **kwargs)
        cls.enforce_permissions(request, *args, **kwargs)
        cls.tabs.sort(key=lambda tab: tab.order)

        active_tab = cls.tabs[0].slug if len(cls.tabs) else None
        active_tab_get = request.GET.get("tab", active_tab)
        if cls.have_tab(active_tab_get):
            active_tab = active_tab_get

        return {"tabs": cls.tabs, "active_tab": active_tab}

