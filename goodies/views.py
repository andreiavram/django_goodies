# coding: utf-8
import types
from django.views.generic.base import TemplateView, View
from django.contrib.contenttypes.models import ContentType
from django.views.generic.list import ListView
import logging
from django.views.generic.edit import DeleteView
from django.contrib import messages
from taggit.models import Tag
from django.http import HttpResponse
import traceback
import json
import zipfile
import os
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from goodies.svg import output_svg_planner

from goodies.tabs import Tab
from goodies.forms import CrispyBaseDeleteForm


logger = logging.getLogger(__file__)


class GenericDeleteJavaScript(TemplateView):
    template_name = "goodies/generic_delete.js"

    def dispatch(self, request, *args, **kwargs):
        self.ctype_model = kwargs.pop("model")
        self.ctype_app = kwargs.pop("app_label")
        self.prefix = "delete"
        if "prefix" in request.GET and request.GET['prefix']:
            self.prefix = request.GET['prefix']

        return super(GenericDeleteJavaScript, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        current = super(GenericDeleteJavaScript, self).get_context_data(*args, **kwargs)

        try:
            ctype = ContentType.objects.get(app_label=self.ctype_app, model=self.ctype_model)
            current.update({"ctype": ctype})
        except Exception, e:
            logger.debug(e)

        current.update({"prefix": self.prefix})
        return current

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['current_app'] = self.request.resolver_match.namespace
        return super(GenericDeleteJavaScript, self).render_to_response(context, **response_kwargs)


class GenericTabDeleteJavaScript(GenericDeleteJavaScript):
    def get_context_data(self, *args, **kwargs):
        current = super(GenericTabDeleteJavaScript, self).get_context_data(*args, **kwargs)
        current.update({"using_tabs": True})
        return current


class TabbedViewMixin(object):
    tab_set = None

    def have_tab(self, search_tab):
        if hasattr(self, "tab_set") and self.tab_set:
            return self.tab_set.has_tab(search_tab)

        for tab in self._tabs:
            if tab.slug == search_tab.strip():
                return True
        return False

    def prepare_tabs(self):
        """ deprecated in favour of using the TabSet object """
        self._tabs = []
        for tab in self.tabs:
            self.add_tab(tab)

    def add_tab(self, tab):
        """ deprecated in favour of the TabSet object """
        if isinstance(tab, type([])) or isinstance(tab, type(())):
            logger.debug("Adding tab from list {0}".format(tab))
            if len(tab) == 6:
                if isinstance(tab[6], types.BooleanType):
                    if not tab[6]:
                        return
                else:
                    if not tab[6](request=self.request):
                        return
            self._tabs.append(Tab(*tab))
        elif isinstance(tab, type({})):
            logger.debug("Adding tab from dict {0}".format(tab))
            if "access_descriptor" in tab and not tab['access_descriptor'](request=self.request):
                return
            if not tab.get("access_flag", True):
                return
            self._tabs.append(Tab(**tab))

        logger.debug("Tabs: {0}".format(self._tabs))

    def get_context_contribution(self, *args, **kwargs):
        return self.tab_set.get_context_contribution(self.request, *args, **kwargs)

    def get_tabs(self, *args, **kwargs):
        """ deprecated in favor of using get_context_contribution """
        if hasattr(self, "tab_set") and self.tab_set:
            return self.tab_set.get_context_contribution(self.request, *args, **kwargs)

        #   backward compatibility
        self.prepare_tabs()
        self._tabs.sort(key=lambda tab: tab.order)

        active_tab = self._tabs[0].slug if len(self._tabs) else None
        active_tab_get = self.request.GET.get("tab", active_tab)
        if self.have_tab(active_tab_get):
            active_tab = active_tab_get

        return {"tabs": self._tabs, "active_tab": active_tab}


class GenericDeleteView(DeleteView):
    template_name = "goodies/delete_form.html"

    def delete(self, *args, **kwargs):
        messages.success(self.request, u"Obiectul a fost șters")
        return super(GenericDeleteView, self).delete(*args, **kwargs)

    def get_context_data(self, **kwargs):
        current = super(GenericDeleteView, self).get_context_data(**kwargs)
        current.update({"form": CrispyBaseDeleteForm(instance=self.object)})
        return current


class AjaxException(Exception):
    def __init__(self, *args, **kwargs):
        self.original_exception = kwargs.get('exception', None)
        self.extra_message = kwargs.get("extra_message", None)

    def to_response(self):
        json_dict = {"original_exception": "%s" % self.original_exception, "extra_message": "%s" % self.extra_message}
        return HttpResponse(json.dumps(json_dict), status=500, content_type="text/json")

    @classmethod
    def validation_compose(self, missing={}, errors={}, call=""):
        return AjaxException(
            extra_message="%s: Validation error, missing required params: %s, params that errored out %s" % (
                call, missing, errors))

    @classmethod
    def generic_response(cls, e, stack_trace):
        json_dict = {"status": "error", "exception": "%s" % e, "trace": "%s" % stack_trace}
        return HttpResponse(json.dumps(json_dict), status=500, content_type="text/json")

    def __unicode__(self):
        return "Error: $s, %s" % (self.original_exception, self.extra_message)


class JSONView(View):
    """ Generic abstract view for API calls
    """
    _params = {}

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(JSONView, self).dispatch(request, *args, **kwargs)
        except AjaxException, e:
            return e.to_response()
        except Exception, e:
            return AjaxException.generic_response(e, traceback.format_exc())

    @property
    def params(self):
        return self._params

    def parse_json_data(self):
        try:
            json_dict = json.loads(self.request.body)
        except ValueError, e:
            json_dict = self.request.POST.dict()
        except Exception, e:
            json_dict = {}

        return json_dict

    def validate(self, use_global_kwargs=True, **kwargs):
        error_dict = {}
        error_dict['missing'] = []
        error_dict['error'] = []

        if use_global_kwargs:
            kwargs.update(self.kwargs)

        self.cleaned_data = {}
        #   checking and cleaning required params
        for param in self.params:
            if not kwargs.has_key(param):
                if self.params.get(param).get("type", "optional") == "required":
                    error_dict['missing'].append(param)
                continue

            validator = getattr(self, "clean_%s" % param, self.default_cleaner)
            try:
                # ISSUE on len(INT)
                #if self.params.get(param).get("type", "optional") == "optional" and len(kwargs.get(param, "")) == 0:
                if self.params.get(param).get("type", "optional") == "optional" and (kwargs.get(param) in ['', None]):
                    continue
                self.cleaned_data[param] = validator(kwargs.get(param))
            except AjaxException, e:
                error_dict['error'].append((param, e))

        if len(error_dict['missing']) + len(error_dict['error']):
            raise AjaxException.validation_compose(missing=error_dict['missing'],
                                                            errors=error_dict['error'], call=self.__class__.__name__)

    def default_cleaner(self, value):
        """ This is the default cleaner, by default it simply returns the value as
        it got it """
        return value

    def construct_json_response(self, **kwargs):
        json_dict = {}
        return json.dumps(json_dict)


class TagsJson(ListView):
    model = Tag
    content_type = "application/json"

    def get_queryset(self):
        q = self.request.GET.get("q", None)
        qs = self.model.objects.all()
        if q:
            qs = qs.filter(name__icontains=q)

        return qs

    def render_to_response(self, context, **response_kwargs):
        json_data = [{"name": t.name, "id": t.id} for t in self.get_queryset()]
        return HttpResponse(json.dumps(json_data), content_type=self.content_type)


class ZipPackageMixin(object):
    def zip_source_folder(self):
        raise NotImplementedError()

    def zip_absolute_url(self):
        raise NotImplementedError()

    def zip_file_name(self):
        raise NotImplementedError()

    def zip_enforce_fresh(self):
        """ Recreates the zip if any of its would-be components are newer than the existing zipfile
        """
        newest_time = 0
        for dirname, dirnames, filenames in os.walk(self.zip_source_folder()):
            for filename in filenames:
                filetime = os.path.getmtime(os.path.join(dirname, filename))
                if filetime > newest_time:
                    newest_time = filetime

        zipfile_time = 0
        if os.path.exists(self.zip_file_name()):
            zipfile_time = os.path.getmtime(self.zip_file_name())

        if newest_time > zipfile_time:
            self.create_zip_file()

    def zip_url(self):
        self.zip_enforce_fresh()
        return self.zip_absolute_url()

    def create_zip_file(self):
        """
        Create zip file based on zip source folder
        """

        zf_filename = self.zip_file_name()
        zf = zipfile.ZipFile(zf_filename, mode='w')

        try:
            for dirname, dirnames, filenames in os.walk(self.zip_source_folder()):
                for filename in filenames:
                    zf.write(os.path.join(dirname, filename),
                             os.path.join(dirname, filename).replace(self.zip_source_folder(), self.slug() + os.sep))
        except Exception, e:
            logger.error(
                u"Nu am putut genera arhiva: %s pentru %s (%s)" % (e, self.__class__.__name__, traceback.format_exc()))
        finally:
            zf.close()


class ContextContributionMixin(object):
    def get_context_data(self, **kwargs):
        context_contribution = self.get_context_contribution(**kwargs)
        return super(ContextContributionMixin, self).get_context_data(**context_contribution)

    def get_context_contribution(self, **kwargs):
        return kwargs


class ContextMenuMixin(ContextContributionMixin):
    menu_classes = {}

    def get_context_contribution(self, **kwargs):
        data = kwargs
        data["menus"] = self._menus
        return data

    def enforce_permissions(self, user=None, **kwargs):
        for name, menu in self._menus.items():
            menu.enforce_permissions(user, **kwargs)

    def get_menu_kwargs(self, **kwargs):
        data = kwargs
        if "object" in self and self.object:
            data['object'] = self.object
        return data

    def get_menus(self, user=None, **kwargs):
        generic_kwargs = self.get_menu_kwargs(**kwargs)
        self._menus = {}
        for name, cls in self.menu_classes.items():
            menu_kwargs = generic_kwargs.copy()
            if "get_%s_menu_kwargs" % name in self and callable(getattr(self, "get_%s_menu_kwargs" % name)):
                menu_kwargs.update(getattr(self, "get_%s_menu_kwargs" % name)(**kwargs))
                self._menus[name] = cls.build_menu(**menu_kwargs)

        self.enforce_permissions(user, **kwargs)


class CalendarViewMixin(ContextContributionMixin):
    def events_context(self):
        return {"events_url": self.get_events_url()}

    def get_events_url(self):
        raise NotImplementedError()

    def get_context_contribution(self, **kwargs):
        kwargs['events_url'] = self.get_events_url()
        return kwargs


class GenericDeleteAPI(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, format=None):
        obj_id = request.data.get("obj_id")
        obj_ctype_id = request.data.get("obj_ctype_id")

        try:
            self.delete_object(obj_id=obj_id, obj_ctype_id=obj_ctype_id)
            data = {"error_msg": u"", "obj_id": obj_id}
        except Exception, e:
            data = {"error_msg": u"Nu am putut șterge obiectul. Contactați administratorul."}

        return Response(data)

    @staticmethod
    def delete_object(obj_model=None, obj_id=None, obj=None, obj_ctype=None, obj_ctype_id=None):
        if obj is None and ((obj_model is None and obj_ctype is None and obj_ctype_id is None) or obj_id is None):
            raise ValueError(u"delete_object are nevoie fie de obiect, fie de tipul obiectului si ID")

        try:
            if obj is None:
                if obj_model is None:
                    if obj_ctype is None:
                        obj_ctype = ContentType.objects.get(id=obj_ctype_id)
                    obj_model = obj_ctype.model_class()

                obj = obj_model.objects.get(id=int(obj_id))

            if hasattr(obj, 'status'):
                obj.status = 2
                obj.save()
            else:
                obj.delete()

            return True
        except Exception, e:
            logger.error(e)
            raise Exception(u"Obiectul nu a putut fi șters - a intervenit o eroare generică.")
