# -*- encoding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, date
from slugify import slugify
import json
from context_processors import *
from forms import *
from models import *

def inicio(request):
	globales = variables_globales(request)
	mensaje= False 
	formulario = LoginForm()
	if not request.user.is_anonymous():
		if globales['HOY'] > EXPIRA:
			mensaje="Periodo de sistema expirado"
			logout(request)
		else:			
			if request.user.perfil == 'Administrador':
				return HttpResponseRedirect(reverse('index'))
	if request.method == "POST":
		formulario = LoginForm(request.POST)
		if formulario.is_valid():
			usuario = formulario.cleaned_data["usuario"]
			password = formulario.cleaned_data["password"]
			acceso = authenticate(username=str(usuario), password=str(password))
			if acceso is not None:			
				if acceso.is_active:
					login(request, acceso)
					return HttpResponseRedirect(reverse('inicio'))
				else:
					mensaje="Tu usuario esta desactivado"		
			else:
				mensaje="Usuario o contraseña incorrecta"
		else:
			mensaje="Usuario o contraseña incorrecta"
	return render(request, 'login.html',locals())

def salir(request):
        logout(request)
        return HttpResponseRedirect(reverse('inicio'))

def index(request):	
	return render(request, 'blank.html', locals())


