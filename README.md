# README

## Introduction

Unsere API soll für die Challenge Tinder for Movies gebraucht werden. Sie stellt den Datenverkehr zwischen der geplanten Webapplikation und der Datenbank sicher. 

In der Webapplikation soll auf der Hauptseite eine Liste von allen Filmen angezeigt werden, zu Beginn sortiert nach Popularität. Durch ein Suchfeld können spezifische Filme gefunden werden. Mit einem Klick auf einen Film werden weitere Informationen angezeigt. Weiter soll man sich auf der Web-Applikation auch registrieren können. Mit dem eigenen Account kann man dann Filme bewerten. Die Hauptseite sortiert die Filme dann nicht mehr nur nach Popularität, sondern anhand unseres Recommenders. Ausserdem kann der Benutzer seine eigenen Ratings anschauen und auch wieder bearbeiten bzw. löschen. Sicherheitsrelevante Themen für Login und die Registrierung können dabei aber vernachlässigt werden.

## RESTful vs GraphQL

Unsere API ist nicht sehr komplex. Da wir unsere Datenbank nur in einer Webapplikation brauchen, bei welcher die Funktionen und verwendeten Daten von Beginn an klar und im weiteren Verlauf unseres Projekt konsistent sind, können alle Calls genau vordefiniert und auf unsere Problemstellungen zugeschnitten sein. So werden auch immer alle gelieferten Daten gebraucht, wodurch es zu keinem Overfetch kommt. Dadurch könnte GraphQL bei unserem Use Case seine grössten Stärken gar nicht zeigen. Ein  Da die Learning Curve und die Komplexität bei GraphQL grösser ist, haben wir uns für RESTful entschieden.

|  | GraphQL      | RESTful |
| ----------- | ----------- | ----------- |
| Organzied in terms of | Schema & Type System      | Endpoints       |
| Community | growing   | large        |
| Learning curve | difficult | moderate |
| Complexity | Higher | Medium |
| Use cases | multiple microservices, mobile apps | simple apps, resource driven apps |