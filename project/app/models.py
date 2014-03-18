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

#Modificacion para guardar el historial de modificaciones
# Conectar con los del admin
def on_revision_commit(**kwargs):
    pass  # Your signal handler code here.
reversion.post_revision_commit.connect(on_revision_commit)

##Django admin
def get_content_type_for_model(obj):
    return ContentType.objects.get_for_model(obj)

#Encontrado en Google
def obtener_request_atributos():
	try:
		user = None
		outer_frames = inspect.getouterframes(inspect.currentframe())
		for tpl in outer_frames:
		        arginfo = inspect.getargvalues(tpl[0])
		        if(type(arginfo[3]) is dict):
		            arg_dict = arginfo[3].copy()
		            for k in arg_dict:
		                if(type(arg_dict.get(k)) is WSGIRequest):
		                    user = arg_dict.get(k).user
		                    path = arg_dict.get(k).path
		                    request = arg_dict.get(k)
		                    break
		            del arg_dict
		        del arginfo
		        if(user):                
		            break
		usuario = Usuario.objects.get(usuario=user)
		return usuario, path, request
	except Exception as e:
		print e 
        pass

def _compare(obj1, obj2, excluded_keys):
    d1, d2 = obj1.__dict__, obj2.__dict__
    old, new = {}, {}
    for k,v in d1.items():
        if k in excluded_keys:
            continue
        try:
            if v != d2[k]:
                old.update({k: v})
                new.update({k: d2[k]})
        except KeyError:
            old.update({k: v})
    return old, new  

def compare(obj1, obj2):
    excluded_keys = 'object', 'object_id_int', '_state'
    return _compare(obj1, obj2, excluded_keys)

@receiver(post_save)
def log(sender,instance,**kwargs):
	try:
		post_save.disconnect(log)
		flag = CHANGE
		usuario, path, request= obtener_request_atributos()
		if not "admin" in path:
			if instance._state.adding:
				flag = ADDITION
			try:
				if flag == CHANGE:
					VersionAdmin(LogEntry, "").log_change(request, instance, "Modifica")
					versiones = Version.objects.filter(content_type=get_content_type_for_model(instance)).order_by('-id')
					version_nueva = versiones[0]
					version_antigua = versiones[1]
					compares = compare(version_antigua, version_nueva)
					model_antiguo = compares[0]
					model_nuevo = compares[1]
					revision = Revision.objects.get(id=model_nuevo['id'])
					cambiados = []
					if(len(model_antiguo.keys()) == 2)  and (len(model_nuevo.keys()) == 2):
						if model_antiguo.keys()[0] == model_nuevo.keys()[0]:
							revision.comment = "No se Modifico nada"
					else:
						for ca, va in json.loads(model_antiguo['serialized_data'])[0]['fields'].iteritems():
							for cn,vn in json.loads(model_nuevo['serialized_data'])[0]['fields'].iteritems():
								if ca == cn:
									if va != vn:
										cambiados.append(str(cn))
						modificados = ', '.join(cambiados)
						revision.comment = "Modifica " + modificados + '.'
					revision.save()
				elif flag == ADDITION:
					VersionAdmin(LogEntry, "").log_addition(request, instance)
			except Exception as e:
				print e
				pass
		post_save.connect(log)
	except Exception as e:
		print e
		pass

@receiver(pre_delete)
def log_delete(sender,instance,**kwargs):
	try:
		pre_delete.disconnect(log_delete)
		flag = DELETION
		usuario, path, request= obtener_request_atributos()
		if not "admin" in path:
				try:
					LogEntry.objects.log_action(
				            user_id=usuario.pk,
				            content_type_id=get_content_type_for_model(instance).pk,
				            object_id=instance.pk,
				            object_repr=force_text(instance),
				            action_flag=flag
				        )
				except Exception as e:
					print e
		pre_delete.connect(log_delete)
	except: pass