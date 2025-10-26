# Gestor de tareas
Para la gestión de tareas se ha decidido utilizar make porque es fácil de usar y ampliamente conocido, además permite crear venv, instalar dependencias y ejecutar tests. También reproduce exactamente los pasos en local y en CI.

Para configurar el makefile se ha optado por 3 opciones, todas ellas trabajan con un entorno aislado virtualenv:

![makefile](imagenes/makefile.png)

* La primera de ellas es install, la cual se encarga de instalar todas las dependencias necesarias. Estas dependencias se han escrito en forma de columna en un .txt para que sea más fácil de ejecutar en el makefile.

* La opción de test se encarga de ejecutar el archivo de test_funciones.py con todos los tests de la aplicación.

* La opción de clean se ha añadido para que sea más cómodo para mí limpiar el repositorio tras ejecutar los tests y no tener que subir los 3.000 archivos que genera virtualenv.