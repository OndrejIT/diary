.PHONY: build clean docker shell outdated reload
.DEFAULT_GOAL := clean

build:
	docker build --tag docker.io/ondrejit/diary:latest .

clean:
	find . -name \*.py[oc] -delete

docker:
	docker exec -ti diary_uwsgi_1 sh

shell:
	docker exec -ti diary_uwsgi_1 python manage shell_plus

outdated:
	docker exec diary_uwsgi_1 pip list --outdated --format columns

reload:
	touch ./.reload
