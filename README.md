# IRC Search

Simple web tool based on Django for making basic search in your IRC messages.

Feel free to fork and extend / tune as you wish!

## Getting Started

Setting up an instance is done by using a container.

### Prerequisites

Install docker:

```
# dnf install docker
```
Get some IRC logs. Here we count with default ZNC bouncer logging format. Filename format YYYY-MM-DD.log and time format [%H:%M:%S] inside the file.

Example line in a file:

```
[14:08:55] <tester> LGTM!
```

"System" messages like:
```
* joe is now known as joe_lunch"
```
are stripped away because of the lookaround.

### Deployment

```
# git clone https://github.com/Rezney/irc_search
```

```
# cd irc_search
```

```
# docker build -t irc_search .
```

If you have SElinux enforcing, run:

```
# setsebool -P container_manage_cgroup 1
```

```
# docker run -d --rm --name irc_search --cap-add=SYS_ADMIN -v /sys/fs/cgroup:/sys/fs/cgroup:ro -v $(pwd)/messages:/app/messages:Z -p 8080:80 irc_search
```

Adjust port as you wish.

Check if we are up and running:

[http://localhost:8080](http://localhost:8080)


### Feeding DB

In order to get your channel messages into DB please follow the instructions:

E.g channel #fedora

1. Place "#fedora" or "fedora" ("#" sign is stripped away when processing) folder into "messages/" directory in irc_search root.
   Repeat the same for every channel you want in the DB. Channel will be named as per directory name.

2. Run "feedb" django management command inside your container.       

```
# docker exec -i irc_search python3 django/manage.py feeddb -a
```

Here we provide "-a" option in order to archive already processed files. If the option is not provided we will go through all the files again when feeding other logs though skipping them.

Then you can for example set a "cronjob" for periodically updating and feeding new logs.

### Maintenance

1. Do not forget to backup your DB in case of deleting the container:

```
# docker exec -i irc_search python3 manage.py dumpdata > db.json // db.json file will be saved on the host
```

2. You can do whatever you want to your DB running:

```
# docker exec -it irc_search python3 django/manage.py dbshell
```

3. Delete all messages with:

```
# docker exec -i irc_search python3 django/manage.py delete -a
```

4. Delete messages for particular channel:

```
# docker exec -i irc_search python3 django/manage.py delete fedora
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
