
all: install

install_deps:
	sudo -H pip3 install -r requirements.txt

help:
	@echo
	@echo "now call sudo systemctl daemon-reload"
	@echo ".. enable service via: sudo systemctl enable command-control-rest-daemon"
	@echo ".. start service via:  sudo systemctl start command-control-rest-daemon"
	@echo ".. status via:         sudo systemctl status command-control-rest-daemon"
	@echo ".. log info via:       sudo journalctl -u command-control-rest-daemon"

install:
	install -m 755 -T command-control-rest-daemon.py /usr/bin/command-control-rest-daemon
	mkdir -p /etc/command-control-rest-daemon
	install -m 644 -T conf.json /etc/command-control-rest-daemon/conf.json
	install -m 644 assets/command-control-rest-daemon.service /lib/systemd/system/
	make help

uninstall:
	rm -rf /usr/bin/command-control-rest-daemon
	rm -rf /etc/command-control-rest-daemon
	rm -rf /lib/systemd/system/command-control-rest-daemon.service


