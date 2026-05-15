from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Tag(models.Model):
    """Etiket modeli. Bir bookmark'a birden fazla etiket eklenebilir (ManyToMany)."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Collection(models.Model):
    """Kullanıcının bookmark'larını gruplandırdığı koleksiyon (klasör)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # Aynı kullanıcı aynı isimde iki koleksiyon açamasın
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection_detail', kwargs={'pk': self.pk})


class Bookmark(models.Model):
    """Tek bir kaydedilmiş link."""
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookmarks'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='bookmarks')
    is_favorite = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bookmark_detail', kwargs={'pk': self.pk})