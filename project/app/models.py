# -*- encoding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractBaseUser, _user_has_perm, PermissionsMixin, _user_has_module_perms
from managers import UsuarioManager
from django.db.models.signals import *
from django.dispatch import receiver
from django.core.validators import RegexValidator
from datetime import datetime
from choices import *
try:
	from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
	from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import reversion
from django.db.models.signals import pre_delete, post_save
from django.contrib.admin.models import LogEntry, DELETION, ADDITION, CHANGE
from django.utils.encoding import force_text
import inspect
from django.core.handlers.wsgi import WSGIRequest
from reversion.admin import VersionAdmin
from reversion.models import Version, Revision
import json

class Usuario(AbstractBaseUser, PermissionsMixin):
	usuario = models.CharField(max_length=35, unique=True, db_index=True)
	perfil  = models.CharField(max_length=25, choices=Perfiles)
	email = models.EmailField(max_length=50, unique=True)
	activo = models.BooleanField(default=True, help_text='Activa un usuario para poder entrar en el sistema')
	administrador = models.BooleanField(default=False, help_text='Que usuarios se les permite entrar al administrador')
	objects = UsuarioManager()
	USERNAME_FIELD = 'usuario'
	def get_full_name(self):
		return self.usuario + ' ' + self.perfil
	def get_short_name(self):
		return self.usuario
	def __unicode__(self):
		return self.usuario
	def has_perm(self, perm, obj=None):
		if self.is_superuser:
			return True
		return _user_has_perm(self, perm, obj=obj)
	def has_module_perms(self, app_label):
		return True
	@property
	def is_staff(self):
		return self.administrador
	@property
	def is_active(self):
		return self.activo
	def __unicode__(self) :
	    return '%s' % (self.usuario)

