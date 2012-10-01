.PHONY:	check clean cleandev dev superuser all tools

EMAIL = $(shell git config --get user.email)
BUILDOUT = ./bin/buildout
DJANGO = ./bin/django
FLAKE8 = ./bin/flake8
PYLINT = ./bin/pylint
TEST   = ./bin/test

all:	check cleandev

tools:	$(BUILDOUT) buildout.cfg
	find bin -type f ! -name buildout -exec rm {} + 
	$(BUILDOUT)


bin/buildout:
	python bootstrap.py


bin/%:	$(BUILDOUT) buildout.cfg
	$(MAKE) tools


clean:
	find . -type f -name \*.py[co] -exec rm {} +
	rm -f rdflib_django.db
	rm -rf dist/ build/
	

db:	$(DJANGO)
	$(DJANGO) syncdb --noinput


superuser:	$(DJANGO) db
	$(DJANGO) createsuperuser --username=$(USER) --email=$(EMAIL) 


prepare:	clean db superuser


cleandev:	$(DJANGO) clean db 
	$(DJANGO) syncdb --noinput
	$(MAKE) dev


dev:	$(DJANGO) 
	$(DJANGO) runserver


check:	$(TEST) $(FLAKE8) $(PYLINT)
	$(TEST)
	$(FLAKE8)
	$(PYLINT)

snapshot:	$(BUILDOUT) clean check
	$(BUILDOUT) setup . egg_info -b".dev-`date +'%Y%m%d%H%M'`" sdist bdist_egg

deploy: $(BUILDOUT) clean check
	$(BUILDOUT) setup . register sdist bdist_egg upload 

