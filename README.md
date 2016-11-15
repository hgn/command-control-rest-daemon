# Installation #

```
sudo aptitude install python3-pip
sudo make install_deps
sudo make install
```

make install will print more information. I.e. how to start and integrate this server into the system permanently.

# Simple Tests #

```
http_proxy=""; curl -i -X POST -H "Content-Type:application/json" http://localhost:50023/v1/raw/ -d '[ "ls /" ]'
```
