ARGS ?=
.PHONY: run stop

run:
	@if [ -f serve.pid ] && kill -0 $$(cat serve.pid) 2>/dev/null; then echo "Already running (pid $$(cat serve.pid))"; exit 1; fi
	nohup python3 -u serve.py $(ARGS) > serve.log 2>&1 & echo $$! > serve.pid

stop:
	kill $$(cat serve.pid) && rm serve.pid