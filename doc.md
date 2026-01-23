## Inicia el proyecto
django-admin startproject myproject .

# Inicia la aplicación
django-admin startapp app 

# Corre el aplicativo
python manage.py runserver 0.0.0.0:8000

# crear migracion 
python manage.py makemigrations

# correr una migración 
python manage.py migrate

# revisar base de datos
python manage.py dbshell

# para entrar a la shell
python manage.py shell

# Para buscar mediante el modelo podemos hacer esto

## Buscar por propiedad

La clase. objects.get(aqui se pasa las propiedades)
ejemplo

```python
from app_1.models import Car

# Obtener un coche por id
try:
    car1 = Car.objects.get(id=1)
except Car.DoesNotExist:
    car1 = None

# Actualizar
    car1.title = "nuevo title"
    car1.save()

# Eliminar
    car1.delete()
```

### Tools:
Para que en terminal nos autocomplete

pip install ipython

Para crear una relación one to Many

se usa en el modelon que va a tener la relacion, se usa la instrucción 
ForeignKey.

```python
class Publisher(models.Model):
    name = models.TextField(max_length=200)
    address = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.address}"

  
class Book(models.Model):
    title = models.TextField(max_length=200)
    publisher_id = models.ForeignKey(Publisher, on_delete=models.PROTECT)
```

Relación many to many

En el modelo que va a tener la relación usar ManyToManyField.

```python
class Authors(models.Model):
    name = models.TextField(max_length=100)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class Book(models.Model):
    title = models.TextField(max_length=200)
    publisher_id = models.ForeignKey(Publisher, on_delete=models.PROTECT)
    publication_at = models.DateField()
    author = models.ManyToManyField(Authors, related_name="authors")
    
    def __str__(self):
        return f"{self.title} - {self.publisher_id.name} - {self.publication_at}"
```


Para agregar las relaciones desde el modelo.

```python
author1 = Authors(name="Mario benedetti",email= "mario@gmail.com")
author2 = Authors(name="Elena",email= "elenita@gmail.com")
book1.author.set([author1, author2])
```

Ahora para ver los autores de libro 

```python
Book.objects.first().author.all()
```

# Iniciar proyecto

docker compose exec web bash 

python manage.py runserver

# Crear usuarios

python manage.py createsuperuser