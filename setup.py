from distutils.core import setup

setup(
    name='django_goodies',
    version='0.0.1',
    packages=['goodies', ],
    url='https://github.com/andreiavram/django_goodies',
    license='MIT',
    author='Andrei Avram',
    author_email='andrei.avram@gmail.com',
    description='A collection of useful django views, forms, widgets that work with and around bootstrap to make building UIs easier',
    install_requires=['Django>=1.4', 'django-taggit', 'django-crispy-forms', 'django-dajax', 'django-dajaxice',
                      'django-recaptcha']
)
