# coding: utf-8
from captcha.fields import ReCaptchaField
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.widgets import PasswordInput

__author__ = 'andrei'

from django import forms
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


logger = logging.getLogger(__name__)


class CrispyBaseForm(forms.Form):
    form_id = None
    add_another_button = False
    submit_label = u"Salvează"
    submit_icon = ""
    has_submit_buttons = True
    form_class = "form-horizontal"
    css_additional_class = "btn-primary"

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()

        self.helper.form_id = "id_%s_form" % self.form_id if self.form_id is not None else "id_%s_form" % self.__class__.__name__.lower()
        self.helper.form_method = "post"
        self.helper.form_class = self.form_class
        if self.has_submit_buttons:
            submit_html = self.submit_label
            #if self.submit_icon and len(self.submit_icon):
            #    submit_html = "<i class = 'icon-%s'></i> " % self.submit_icon + submit_html
            self.helper.add_input(Submit('submit', submit_html, css_class="btn " + self.css_additional_class))
        if self.add_another_button:
            self.helper.add_input(
                Submit('submit', 'Salvează și adaugă mai departe', css_class="btn", css_id="id_save_other"))

        super(CrispyBaseForm, self).__init__(*args, **kwargs)


class CrispyBaseModelForm(forms.ModelForm):
    form_id = None
    add_another_button = False
    submit_label = u"Salvează"
    has_submit_buttons = True
    form_class = "form-horizontal"

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()

        self.helper.form_id = "id_%s_form" % self.form_id if self.form_id is not None else "id_%s_form" % self.__class__.__name__.lower()
        self.helper.form_method = "post"
        self.helper.form_class = self.form_class
        if self.has_submit_buttons:
            self.helper.add_input(Submit('submit', self.submit_label, css_class="btn btn-primary"))
        if self.add_another_button:
            self.helper.add_input(
                Submit('submit', 'Salvează și adaugă mai departe', css_class="btn", css_id="id_save_other"))

        super(CrispyBaseModelForm, self).__init__(*args, **kwargs)


class CrispyBaseDeleteForm(forms.ModelForm):
    form_id = None
    has_cancel = False

    def __init__(self, *args, **kwargs):
        super(CrispyBaseDeleteForm, self).__init(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_id = "id_%s_form" % self.form_id if self.form_id is not None else "id_%s_form" % self.__class__.__name__.lower()
        self.helper.form_method = "post"
        self.helper.form_class = "form-horizontal"
        self.helper.add_input(Submit('submit', 'Șterge', css_class="btn btn-danger"))
        if self.has_cancel:
            self.helper.add_input(Submit('cancel', 'Renunță', css_class="btn", css_id="id_has_cancel"))


class ChangePasswordForm(CrispyBaseForm):
    submit_label = u"Salvează noua parolă"
    password = forms.CharField(widget=PasswordInput(), label=u"Parola")
    password2 = forms.CharField(widget=PasswordInput(), label=u"Parola (verificare)")

    def clean_password(self):
        return self._clean_passwd(self.cleaned_data['password'])

    def clean_password2(self):
        return self._clean_passwd(self.cleaned_data['password2'])

    @staticmethod
    def _clean_passwd(self, passwd):
        if len(passwd) < 5:
            raise ValidationError(u"Parola trebuie să aibă cel puțin 5 caractere")
        return passwd

    def clean(self):
        if self.cleaned_data['password'] != self.cleaned_data['password2']:
            raise ValidationError(u"Cele două parole nu sunt identice")

        return self.cleaned_data


class PasswordResetForm(CrispyBaseForm):
    submit_label = u"Solicită schimbarea parolei"
    email = forms.EmailField(label=u"Adresa de email", help_text=u"Adresa de email cu care v-ați înregistrat",
                             required=True)
    captcha = ReCaptchaField(label=u"Cod verificare",
                             attrs={"theme": "clean", "lang": "ro", "options": {"refresh_btn": u"Imagine nouă"}})

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError(u"Nu există niciun utilizator cu această adresă de email")

        return email


class BetterPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = "change_password"
        self.helper.form_method = "post"

        self.helper.form_class = "form-horizontal"
        self.helper.add_input(Submit('submit', 'Salvează', css_class="btn btn-primary"))
        super(BetterPasswordChangeForm, self).__init__(*args, **kwargs)