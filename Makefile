.PHONY: setup backend frontend clean

setup:
	@echo "Setting up Backend..."
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "Setting up Frontend..."
	cd frontend && npm install

backend:
	@echo "Starting Backend..."
	cd backend && ./run.sh

frontend:
	@echo "Starting Frontend..."
	cd frontend && ./run.sh

clean:
	rm -rf backend/.venv
	rm -rf frontend/node_modules
