import os, sys, site
from os.path import abspath, dirname
from sys import path

try:
	SITE_ROOT = dirname(dirname(abspath(__file__)))
	path.append(SITE_ROOT)
	
	# Tell wsgi to add the Python site-packages to its path. 
	site.addsitedir('/home/{{usuario}}/.virtualenvs/{{maquina_virtual_nombre}}/lib/python2.7/site-packages')
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings.produccion")
	activate_this = os.path.expanduser("~/.virtualenvs/{{maquina_virtual_nombre}}/bin/activate_this.py")
	execfile(activate_this, dict(__file__=activate_this))
	
	# Calculate the path based on the location of the WSGI script
	project = '/home/{{usuario}}/webapps/{{nombre_de_la_aplicacion}}/project/project/'
	workspace = os.path.dirname(project)
	sys.path.append(workspace)
except: 

	pass

from django.core.handlers.wsgi import WSGIHandler
application = WSGIHandler()

