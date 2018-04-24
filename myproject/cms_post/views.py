from django.shortcuts import render
from django.http import HttpResponse
from .models import Resource
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.template.loader import get_template
from django.template import Context

# Create your views here.

title = "SARO - 15.10 - CMS POST"
url_root = "/"


def get_plantilla(logged, url_logged, logged_str, rec_name, rec_cont):
	template = get_template("plantilla/index.html")
	c = Context({'title': title, 'url_root': url_root, 'logged': logged,
	'url_logged': url_logged, 'logged_str': logged_str, 'rec_name': rec_name,
	'rec_cont': rec_cont})
	my_template = template.render(c)
	return my_template


@csrf_exempt
def root_page(request):
	if request.user.is_authenticated():
		logged = "Logged in as " + request.user.username + ". "
		logged_str = "Logout"
		url_logged = "/logout"
	else:
		logged = "Not logged in. "
		url_logged = "/login"
		logged_str = "Login"

	recursos_DB = Resource.objects.all()
	lista = "Recursos: ["
	for my_rec in recursos_DB:
		lista += my_rec.name + '; '
	lista += "]"

	rec_name = "MIS RECURSOS: "
	rec_cont = lista
	my_template = get_plantilla(logged, url_logged, logged_str,
	rec_name, rec_cont)
	return HttpResponse(my_template)


@csrf_exempt
def annotated(request, resource):
	if request.user.is_authenticated():
		logged = "Logged in as " + request.user.username + ". "
		logged_str = "Logout"
		url_logged = "/logout"
		if request.method == "PUT":
			try:  # si el recurso YA existe, SE MUESTRA el contenido.
				resource_DB = Resource.objects.get(name=resource)
				rec_name = "Recurso ya existe: " + resource_DB.name
				rec_cont = resource_DB.cont
				my_template = get_plantilla(logged, url_logged, logged_str,
				rec_name, rec_cont)
				return HttpResponse(my_template)
			except Resource.DoesNotExist:  # Crea el recurso
				try:
					new_resource = Resource(name=resource, cont=request.body)
					new_resource.save()  # add recurso -- force_insert=True

					my_rec = Resource.objects.all().last()
					rec_name = "Nuevo recurso: " + my_rec.name + " añadido"
					rec_cont = my_rec.cont
					my_template = get_plantilla(logged, url_logged, logged_str,
					rec_name, rec_cont)
					return HttpResponse(my_template)

				except IntegrityError:
					rec_name = "MENSAJE! ERROR AL AÑADIR EL RECURSO"
					rec_cont = "Ha habido un problema en la base de datos.\
					Por favor, vuelva a intentarlo."
					my_template = get_plantilla(logged, url_logged, logged_str,
					rec_name, rec_cont)
					return HttpResponse(my_template)

	else:
		logged = "Not logged in. "
		url_logged = "/login"
		logged_str = "Login"

	if request.method == "GET":
		try:
			resource_DB = Resource.objects.get(name=resource)
			rec_name = resource_DB.name
			rec_cont = resource_DB.cont
		except Resource.DoesNotExist:
			rec_name = "MENSAJE!"
			rec_cont = "ERROR!! - EL RECURSO NO EXISTE. \
			Haga un PUT a 'localhost:8000/annotated/[nombre_recurso]'\
			si deseas añadirlo."

		my_template = get_plantilla(logged, url_logged, logged_str,
		rec_name, rec_cont)
		return HttpResponse(my_template)

	elif request.method == "PUT":  # No logeado - No puede añadir recursos
		rec_name = "MENSAJE! ERROR DE AUTENTICACIÓN"
		rec_cont = "Por favor. Identifiquese primero."
		my_template = get_plantilla(logged, url_logged, logged_str,
		rec_name, rec_cont)
		return HttpResponse(my_template)

	else:  # Metodo no valido
		rec_name = "MENSAJE! ACCIÓN NO VALIDA"
		rec_cont = "Para esta URL los métodos válidos son PUT y GET"
		my_template = get_plantilla(logged, url_logged, logged_str,
		rec_name, rec_cont)
		return HttpResponse(my_template)


@csrf_exempt
def show_form(request, resource):
	if request.user.is_authenticated():  # si esta autenticado
		logged = "Logged in as " + request.user.username + ". "
		logged_str = "Logout"
		url_logged = "/logout"
		try:  # si existe el recurso
			resource_DB = Resource.objects.get(name=resource)
			if request.method == "GET":
				title_form = "Editar " + resource_DB.name
				rec_cont = resource_DB.cont
				template = get_template("plantilla/form.html")
				c = Context({'title': title, 'url_root': url_root,
				'logged': logged, 'url_logged': url_logged,
				'logged_str': logged_str, 'rec_name': resource_DB.name,
				'rec_cont': rec_cont, 'title_form': title_form})
				my_template = template.render(c)
				return HttpResponse(my_template)
				
			elif request.method == "POST":
				rec_new_cont = request.POST['rec_cont']
				#  actualiza el contenido
				resource_DB.cont = rec_new_cont
				resource_DB.save()
				
				resource_DB = Resource.objects.get(name=resource)
				title_form = "Actualizado " + resource_DB.name
				rec_cont = resource_DB.cont
				template = get_template("plantilla/form.html")
				c = Context({'title': title, 'url_root': url_root,
				'logged': logged, 'url_logged': url_logged,
				'logged_str': logged_str, 'rec_name': resource_DB.name,
				'rec_cont': rec_cont, 'title_form': title_form})
				my_template = template.render(c)				
				return HttpResponse(my_template)
			else:
				rec_name = "MENSAJE! ACCIÓN NO VALIDA"
				rec_cont = "Para esta URL los métodos válidos son POST y GET"
				my_template = get_plantilla(logged, url_logged, logged_str,
				rec_name, rec_cont)
				return HttpResponse(my_template)
		except Resource.DoesNotExist:
			rec_name = "MENSAJE!"
			rec_cont = "ERROR!! - EL RECURSO NO EXISTE. \
			Haga un PUT a 'localhost:8000/annotated/[nombre_recurso]'\
			si desea añadirlo."	
			my_template = get_plantilla(logged, url_logged, logged_str,
			rec_name, rec_cont)
			return HttpResponse(my_template)
	else:  # NO AUTENTICADO
		logged = "Not logged in. "
		url_logged = "/login"
		logged_str = "Login"
		rec_name = "MENSAJE!"
		rec_cont = "Por favor. Identifiquese primero."
		my_template = get_plantilla(logged, url_logged, logged_str,
		rec_name, rec_cont)
		return HttpResponse(my_template)
