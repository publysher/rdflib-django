.PHONY:	check clean cleandev dev superuser all tools

EMAIL = $(shell git config --get user.email)
DJANGO = ./bin/django
FLAKE8 = ./bin/flake8
PYLINT = ./bin/pylint
TEST   = ./bin/test

all:	check cleandev

tools:	bin/buildout buildout.cfg
	find bin -type f ! -name buildout -exec rm {} + 
	bin/buildout 


bin/buildout:
	python bootstrap.py


bin/%:	bin/buildout buildout.cfg
	$(MAKE) tools


clean:
	find . -type f -name \*.py[co] -exec rm {} +
	rm -f rdflib_django.db
	

cleandev:	$(DJANGO) clean
	$(DJANGO) syncdb --noinput
	$(MAKE) dev


dev:	$(DJANGO)
	$(DJANGO) runserver


superuser:	$(DJANGO)
	$(DJANGO) createsuperuser --username=$(USER) --email=$(EMAIL) 


check:	$(TEST) $(FLAKE8) $(PYLINT)
	$(TEST)
	$(FLAKE8)
	$(PYLINT)
