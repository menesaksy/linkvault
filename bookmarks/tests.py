from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Bookmark, Collection, Tag


class ModelTests(TestCase):
    """Model seviyesinde temel davranış testleri."""

    def setUp(self):
        self.user = User.objects.create_user(username='enes', password='test1234')
        self.collection = Collection.objects.create(name='Güvenlik', owner=self.user)

    def test_bookmark_str(self):
        b = Bookmark.objects.create(title='Test Link', url='https://example.com', owner=self.user)
        self.assertEqual(str(b), 'Test Link')

    def test_collection_str(self):
        self.assertEqual(str(self.collection), 'Güvenlik')

    def test_bookmark_tags_relationship(self):
        """ManyToMany ilişkisi doğru çalışıyor mu?"""
        b = Bookmark.objects.create(title='Etiketli', url='https://example.com', owner=self.user)
        tag1 = Tag.objects.create(name='python')
        tag2 = Tag.objects.create(name='django')
        b.tags.add(tag1, tag2)
        self.assertEqual(b.tags.count(), 2)

    def test_collection_unique_per_user(self):
        """Aynı kullanıcı aynı isimde iki koleksiyon açamamalı."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Collection.objects.create(name='Güvenlik', owner=self.user)


class ViewAccessTests(TestCase):
    """View erişim ve authorization testleri."""

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass1234')
        self.user2 = User.objects.create_user(username='user2', password='pass1234')
        self.bookmark = Bookmark.objects.create(
            title='User1 Bookmark', url='https://example.com', owner=self.user1
        )

    def test_list_requires_login(self):
        """Giriş yapmadan ana sayfaya gidince login'e yönlendirilmeli."""
        response = self.client.get(reverse('bookmark_list'))
        self.assertEqual(response.status_code, 302)

    def test_list_works_when_logged_in(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('bookmark_list'))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_others_bookmark(self):
        """user2, user1'in bookmark'ını düzenleyememeli (authorization)."""
        self.client.login(username='user2', password='pass1234')
        response = self.client.get(reverse('bookmark_update', args=[self.bookmark.pk]))
        self.assertEqual(response.status_code, 403)

    def test_owner_can_view_detail(self):
        self.client.login(username='user1', password='pass1234')
        response = self.client.get(reverse('bookmark_detail', args=[self.bookmark.pk]))
        self.assertEqual(response.status_code, 200)


class CRUDTests(TestCase):
    """Create / Update / Delete işlemleri gerçekten veriyi değiştiriyor mu?"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='enes', password='test1234')
        self.client.login(username='enes', password='test1234')

    def test_create_bookmark(self):
        response = self.client.post(reverse('bookmark_create'), {
            'title': 'Yeni Link',
            'url': 'https://django.com',
            'description': '',
            'tags_input': 'web, framework',
        })
        self.assertEqual(Bookmark.objects.count(), 1)
        bookmark = Bookmark.objects.first()
        self.assertEqual(bookmark.title, 'Yeni Link')
        # tags_input metni gerçekten Tag nesnelerine çevrildi mi?
        self.assertEqual(bookmark.tags.count(), 2)

    def test_delete_bookmark(self):
        bookmark = Bookmark.objects.create(
            title='Silinecek', url='https://example.com', owner=self.user
        )
        self.client.post(reverse('bookmark_delete', args=[bookmark.pk]))
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_search_filter(self):
        """Arama sadece eşleşen sonuçları döndürüyor mu?"""
        Bookmark.objects.create(title='Python Tutorial', url='https://a.com', owner=self.user)
        Bookmark.objects.create(title='Cooking Recipes', url='https://b.com', owner=self.user)
        response = self.client.get(reverse('bookmark_list'), {'q': 'python'})
        self.assertContains(response, 'Python Tutorial')
        self.assertNotContains(response, 'Cooking Recipes')

    def test_toggle_favorite_ajax(self):
        """AJAX favori endpoint'i çalışıyor ve durumu değiştiriyor mu?"""
        bookmark = Bookmark.objects.create(
            title='Fav Test', url='https://example.com', owner=self.user, is_favorite=False
        )
        response = self.client.post(reverse('toggle_favorite', args=[bookmark.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'is_favorite': True})
        bookmark.refresh_from_db()
        self.assertTrue(bookmark.is_favorite)


class APITests(TestCase):
    """REST API testleri."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='enes', password='test1234')

    def test_api_requires_authentication(self):
        response = self.client.get('/api/bookmarks/')
        self.assertEqual(response.status_code, 403)

    def test_api_returns_only_own_bookmarks(self):
        other = User.objects.create_user(username='other', password='pass1234')
        Bookmark.objects.create(title='Benim', url='https://a.com', owner=self.user)
        Bookmark.objects.create(title='Başkasının', url='https://b.com', owner=other)

        self.client.login(username='enes', password='test1234')
        response = self.client.get('/api/bookmarks/')
        self.assertEqual(response.status_code, 200)
        # Pagination açık olduğu için 'results' içine bak
        data = response.json()
        results = data['results'] if 'results' in data else data
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Benim')