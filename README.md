The documentation in this tree is in plain text files and can be viewed using
any text file viewer.

To start with project

Linux (VSC):
* Скачать архив
  
* Установить Python 3.11.4

* Открыть в Visual Studio Code

* В extensions VSC установить Python

* Right-click на manage.py, Open in Integrated Terminal

* Ctrl+Shift+P

* ``python create eviroment``

* ``venv``

* ``Python 3.11.4``
  
* Поставить галочки на все поля.

* OK

* venv activate ``source .venv/bin/activate``

* Install Lib ``pip install -r requirements.txt``
  
* Make migrations ``python manage.py makemigrations``

* Apply migrations ``python manage.py migrate``

* Run server ``python manage.py runserver``
