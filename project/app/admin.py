# -*- coding: utf-8 -*-
from models import *
from forms import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group, Permission

admin.site.unregister(Site)
admin.site.unregister(Group)

class MyUserAdmin(UserAdmin):
    form = CambiarusuarioForm
    add_form = CrearusuarioForm

    list_display = ('usuario', 'email', 'perfil')
    list_filter = ('perfil', )
    
    fieldsets = (
                (None, {'fields': ('usuario', 'email', 'password')}),
                ('Perfil', {'fields': ('perfil',)}),
                ('Permisos', {'fields': ('administrador', 'activo', 'user_permissions')}),
    )
    add_fieldsets = (
                    (None, {'classes': ('wide',), 'fields': ('usuario', 'password1', 'password2',)}),
    )
    search_fields = ('usuario', 'email')
    ordering = ('usuario',)
    filter_horizontal = ('user_permissions',)
    exclude = ['is_superuser']

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'user_permissions':
            query = Permission.objects.filter(content_type__app_label="index")
            kwargs['queryset'] = query
        return super(MyUserAdmin, self).formfield_for_manytomany(db_field, request=request, **kwargs)

class UsuarioAdmin(reversion.VersionAdmin, MyUserAdmin):
    pass

admin.site.register(Usuario, UsuarioAdmin)






