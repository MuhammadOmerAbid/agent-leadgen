.PHONY: install enrich send test lint

install:
	pip install -r requirements.txt

campaign:
	python agent_leadgen/main.py campaign create --type $(TYPE) --name "$(NAME)"

leads-pull:
	python agent_leadgen/main.py leads pull --campaign "$(CAMPAIGN)"

enrich:
	python agent_leadgen/main.py enrich --campaign "$(CAMPAIGN)"

send:
	python agent_leadgen/main.py send --campaign "$(CAMPAIGN)"

send-dry:
	python agent_leadgen/main.py send --campaign "$(CAMPAIGN)" --dry-run

test:
	pytest tests/ -v

lint:
	python -m py_compile agent_leadgen/main.py agent_leadgen/db.py agent_leadgen/drafter.py agent_leadgen/sender.py
