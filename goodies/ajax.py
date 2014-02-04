#coding: utf-8
from django.db.models.fields import FieldDoesNotExist

__author__ = 'andrei'

from dajax.core import Dajax
import logging
from django.contrib.contenttypes.models import ContentType
from dajaxice.decorators import dajaxice_register
logger = logging.getLogger(__name__)

@dajaxice_register
def delete_action(request, obj_id, obj_ctype_id, prefix):
    dajax = Dajax()

    try:
        delete_object(request, obj_id = obj_id, obj_ctype_id = obj_ctype_id)
        dajax.add_data({"error_msg" : u"", "obj_id" : obj_id}, "after_generic_delete_%s" % prefix)
    except:
        dajax.add_data({"error_msg" : u"Nu am putut șterge obiectul. Contactați administratorul."}, "after_generic_delete_%s" % prefix)

    return dajax.json()


def delete_object(request, obj_model = None, obj_id = None, obj = None, obj_ctype = None, obj_ctype_id = None):
    if obj == None and ((obj_model == None and obj_ctype == None and obj_ctype_id == None) or obj_id == None):
        raise ValueError(u"delete_object are nevoie fie de obiect, fie de tipul obiectului si ID")

    try:
        if obj == None:
            if obj_model == None:
                if obj_ctype == None:
                    obj_ctype = ContentType.objects.get(id = obj_ctype_id)
                obj_model = obj_ctype.model_class()

            obj = obj_model.objects.get(id = int(obj_id))

        if hasattr(obj, 'status'):
            obj.status =  2
            obj.save()
        else:
            obj.delete()

        return True
    except Exception, e:
        logger.error(e)
        raise e

    raise Exception(u"Obiectul nu a putut fi șters - a intervenit o eroare generică.")

@dajaxice_register
def toggle_object_property(request, obj_ctype_id, obj_id, property, js_after = ""):
    """
    Metodă generală de modificare a unui atribut al unui obiect, pentru cazul de utilizare tipic
    cu un click pe un control care schimbă starea obiectului.

    Cazul tipic de utilizare este toggle-uirea valorilor obiectelor dintr-o listă prin simpla
    apăsare a unui buton în lista.

    @param obj_ctype_id:  id de ContentType, care poate fi obtinut intr-o functie wrapper sau
    poate fi pus la dispozitie textual de clasa in sine
    @param obj_id id-ul obiectului
    @param  property: atributul care trebuie toggleuit. Sunt acceptate BooleanField (care va fi toggle-uit True / False)
    si CharField cu un atribut choices setat, care va avansa optiunea la următoarea din listă, ciclând astfel opțiunile.

    @todo: test this in practice
    """
    dajax = Dajax()

    try:
        content_type = ContentType.objects.get(id = obj_ctype_id)
        obj = content_type.model_class().objects.get(id = obj_id)

        field = obj._meta.get_field_by_name(property)[0]
        if field.__name__ not in ("BooleanField", "CharField"):
            logger.debug(u"Proprietatea %s nu este de tipul BooleanField (cannot be toggled)" % (property, ))


        if field.__name__ == "BooleanField":
            #    toggles boolean value of obj.property
            setattr(obj, property, not getattr(obj, property))

        else:
            #    this is a char field. we can only toggle it's value if it has choices
            #    this will push the item to the next choice or cycle back to the first
            #    one if the current choice is the last in the list
            choices = list(field.choices)
            if not choices.length:
                logger.error(u"Câmpul nu este boolean și are câmpul choices gol")
                raise ValueError(u"Câmpul nu este boolean și are câmpul choices gol")
            current_choice = getattr(obj, property)
            current_position = choices.index(current_choice)

            if current_position < len(choices) - 1:
                new_choice = choices[current_position + 1][0]
            else:
                new_choice = choices[0][0]

            setattr(obj, property, new_choice)

        obj.save()

    except FieldDoesNotExist:
        logger.error(u"Obiectul %s : %d nu are proprietatea %s" % (obj.__class__.__name__, obj_id, property))
        dajax.add_data({"error" : u"Obiectul nu are proprietatea %s" % property}, "dajax_ui_messages")
        return dajax.json()
    except Exception, e:
        logger.error(u"Probleme la toggle-uirea proprietății %s, pentru obiectul %s : %s" (property, obj.__class__.__name__, obj_id))
        dajax.add_data({"error" : u"A apărut o problemă la efectuarea acțiunii (%s)" % e}, "dajax_ui_messages")
        return dajax.json()

    callback = js_after if js_after != "" else "after_generic_template"
    dajax.add_data({"obj_id" : obj_id, "obj_ctype_id" : obj_ctype_id, "property" : property}, callback)
    return dajax.json()