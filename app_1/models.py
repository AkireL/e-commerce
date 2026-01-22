from django.db import models

# Create your models here.
class Card(models.Model):
    title = models.TextField(max_length=20)
    year = models.TextField(max_length=4, null=True)
    color = models.TextField(max_length=20, default="black")

    def __str__(self):
        return f"{self.title} - {self.year} - {self.color}"
    

class Publisher(models.Model):
    name = models.TextField(max_length=200)
    address = models.TextField(max_length=500)

    def __str__(self):
        return f"{self.name} - {self.address}"

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

class Profile(models.Model):
    website = models.URLField(max_length=200)
    bio = models.TextField(max_length=500)
    author_id = models.OneToOneField(Authors, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.website} - {self.bio} - {self.author_id}"