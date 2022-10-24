# README

### Quickstart

Wir verwenden Docker, um die Umgebung für unsere API bereitzustellen. 
Voraussetzung dafür ist das Installieren von Docker, welches je nach Betriebssystem unterscheidlich gemacht werden muss.
Die Dokumentation findet sich hier: https://docs.docker.com/install/.

Ist Docker installiert und gestartet, können in einen Commandline Fenster im Projektverzeichnis folgende Befehle ausgeführt werden:

```
shell> docker build -t wdb_mc1_web -f ./dockerfile .
shell> docker-compose up -d
```

#### Webserver

Für das Aufsetzen des Webservers muss eine Datenbank installiert werden.
Wir verwenden MariaDB Server, welches von hier bezogen werden kann: https://mariadb.org/download/.
Nach abgeschlossener Installation kann die Datenbank folgendermassen aufgesetzt werden:

```
shell> mysql

MariaDB [(none)]> CREATE DATABASE wdb;
MariaDB [(none)]> CREATE USER 'api'@'%' IDENTIFIED BY 'some_password';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON wdb.* TO 'api'@'%';
MariaDB [(none)]> FLUSH PRIVILEGES;
MariaDB [(none)]> (CTRL + C)

shell> mysql wdb < ./sql/structure.sql

```

Die Datenbank "wdb" ist nun aufgesetzt und kann mit Daten befüllt werden.

Als Nächstes müssen die Zugangsdaten der Datenbank dem Webserver mitgeteilt werden.
Dazu die Datei 'credentials.json.sample' nach 'credentials.json' kopieren und die Felder "host, port, user, password, db" auf die Zugangsdaten des Datenbankservers anpassen.

Als Nächstes muss in den Docker Container gewechselt werden.
Im Container muss folgender Befehl ausgeführt werden, um die Python Abhängigkeiten zu installieren und die API zu starten:

```
shell> cd /home/motoko/work/ && pipenv install && pipenv run python main.py
```

Die API ist nun unter http://localhost:5000 verfügbar.


#### Test

Um die API zu testen muss man in den Docker Container wechseln und dort in der Shell folgenden Befehl ausführen:

```
shell> cd /home/motoko/work/ && pipenv install && pipenv run python test.py
```

Waren alle Tests erfolgreich, wird folgende Meldung ausgegeben:

```
----------------------------------------------------------------------
Ran (n) tests in (n)s

OK
```


## Übersicht Calls

### User

| Method | Route | Description |
| ---- | ---- | ---- |
| GET | /user | Get all users |
| GET | /user/<user_id> | Get a specific user |
| GET | /user/<user_id>/ratings | Get all ratings of a specific user |
| GET | /user/<user_id>/ratings/movies | Get all movies which a specific user has rated |
| POST | /user | Create a user |
| DELETE | /user/<user_id> | Delete a user |
| PUT | /user/<user_id> | Update a user |

### Movie

| Method | Route | Description |
| ---- | ---- | ---- |
| GET | /movie | Get all movies. Possible params: ?limit_n=<int> only returns top n movies by vote average. ?title=<string> only returns movies with titles containing the given string |
| GET | /movie/<movie_id> | Get a specific movie |
| POST | /movie | Create a movie |
| DELETE | /movie/<movie_id> | Delete a movie |
| PUT | /movie/<movie_id> | Update a movie |

### Ratings

| Method | Route | Description |
| ---- | ---- | ---- |
| POST | /rating | Create a rating |
| PUT | /rating/<rating_id> | Update a rating |
| DELETE | /rating/<rating_id> | Delete a rating |

## Report

### Use Case und Motivation

Unsere API soll für die Challenge Tinder for Movies gebraucht werden. Sie stellt den Datenverkehr zwischen der geplanten Webapplikation und der Datenbank sicher. 

In der Webapplikation soll auf der Hauptseite eine Liste von allen Filmen angezeigt werden, zu Beginn sortiert nach Popularität. Durch ein Suchfeld können spezifische Filme gefunden werden. Mit einem Klick auf einen Film werden weitere Informationen angezeigt. Weiter soll man sich auf der Web-Applikation auch registrieren können. Mit dem eigenen Account kann man dann Filme bewerten. Die Hauptseite sortiert die Filme dann nicht mehr nur nach Popularität, sondern anhand unseres Recommenders. Ausserdem kann der Benutzer seine eigenen Ratings anschauen und auch wieder bearbeiten bzw. löschen. Sicherheitsrelevante Themen für Login und die Registrierung können dabei aber vernachlässigt werden.

### Architektur

Um die im Use Case beschriebenen Funktionalitäten zu bedienen, haben wir einen Flask Webserver implementiert. Dieser stellt die Schnittstelle zwischen der Webapplikation und der Datenbank dar. 
Die Datenbank ist ein Mariadb Server, welchen wir auf einem Ubuntu Server gehostet haben. 

Für die Tests wird im Docker Container eine "mariadb-server" Instanz mit installiert.
Diese dient als Mock-Datenbank, welche die gleiche Struktur wie die echte Datenbank hat.
Sie wird vor jedem Test mit denselben Testdaten von ./sql/setup.sql befüllt.

Die API ist in zwei Teile aufgeteilt:

* User API
* Movie API

#### User API

Die User API dient zum Verwalten der User. Es können alle User abgefragt werden, ein User mit einer bestimmten ID abgefragt werden, ein User erstellt, gelöscht oder geupdatet werden. Es können auch die Ratings oder alle Filme eines Users abgefragt werden, welche er bewertet hat. Da die Webapplikation lediglich Ratings aus der bestehenden Datenbank verwenden soll und keine neuen Ratings dazu kommen, fallen Kreierung, Bearbeitung und Löschung von Ratings weg.

#### Movie API

Die Movie API dient zum Verwalten der Movies. Es können alle Movies abgefragt werden, ein Movie mit einer bestimmten ID abgefragt werden, ein Movie erstellt, gelöscht oder geupdatet werden.

### Datenbank

Die Datenbank besteht aus 3 Tabellen:

* TMDB_movie_infos
* user
* user_rating

#### TMDB_movie_infos

Die TMDB_movie_infos Tabelle enthält alle Informationen zu den Filmen. Diese werden von der TMDB API abgefragt und in die Datenbank geschrieben. 

#### user

Die user Tabelle enthält alle User.

#### user_rating

Die user_rating Tabelle enthält alle Ratings der User. Sie ist die Verbindungstabelle zwischen user und TMDB_movie_infos.


### RESTful vs GraphQL

Unsere API ist nicht sehr komplex. Da wir unsere Datenbank nur in einer Webapplikation brauchen, bei welcher die Funktionen und verwendeten Daten von Beginn an klar und im weiteren Verlauf unseres Projekt konsistent sind, können alle Calls genau vordefiniert und auf unsere Problemstellungen zugeschnitten sein. So werden auch immer alle gelieferten Daten gebraucht, wodurch es zu keinem Overfetch kommt. Dadurch könnte GraphQL bei unserem Use Case seine grössten Stärken gar nicht zeigen. Ein  Da die Learning Curve und die Komplexität bei GraphQL grösser ist, haben wir uns für RESTful entschieden.

#### Übersicht

|  | GraphQL      | RESTful |
| ----------- | ----------- | ----------- |
| Organzied in terms of | Schema & Type System      | Endpoints       |
| Community | growing   | large        |
| Learning curve | difficult | moderate |
| Complexity | Higher | Medium |
| Use cases | multiple microservices, mobile apps | simple apps, resource driven apps |
