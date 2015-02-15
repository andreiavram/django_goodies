from distutils.core import setup
from setuptools import find_packages

setup(
    name='django_goodies',
    version='0.0.2',
    packages=find_packages(exclude=["example", ]),
    url='https://github.com/andreiavram/django_goodies',
    license='MIT',
    author='Andrei Avram',
    author_email='andrei.avram@gmail.com',
    description='A collection of useful django views, forms, widgets that work with and around bootstrap to make building UIs easier',
    install_requires=['Django>=1.4', 'django-taggit', 'django-crispy-forms', 'django-recaptcha'],
    include_package_data=True,
    zip_safe=False
)
