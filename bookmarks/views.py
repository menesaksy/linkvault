from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from .models import Bookmark, Collection, Tag
from .forms import BookmarkForm, CollectionForm


# ---------- Auth ----------

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Hesabın oluşturuldu, hoş geldin!')
            return redirect('bookmark_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# ---------- Bookmark CRUD ----------

class BookmarkListView(LoginRequiredMixin, ListView):
    model = Bookmark
    template_name = 'bookmarks/bookmark_list.html'
    context_object_name = 'bookmarks'
    paginate_by = 6  # pagination

    def get_queryset(self):
        # Sadece giriş yapan kullanıcının bookmark'ları + ilişkili veriyi tek sorguda çek
        qs = Bookmark.objects.filter(owner=self.request.user)\
            .select_related('collection').prefetch_related('tags')

        # Arama
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(url__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()

        # Koleksiyona göre filtre
        collection_id = self.request.GET.get('collection')
        if collection_id:
            qs = qs.filter(collection_id=collection_id)

        # Sadece favoriler filtresi
        if self.request.GET.get('favorites') == '1':
            qs = qs.filter(is_favorite=True)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['collections'] = Collection.objects.filter(owner=self.request.user)
        ctx['query'] = self.request.GET.get('q', '')
        ctx['active_collection'] = self.request.GET.get('collection', '')
        ctx['favorites_only'] = self.request.GET.get('favorites') == '1'
        return ctx


class BookmarkDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Bookmark
    template_name = 'bookmarks/bookmark_detail.html'
    context_object_name = 'bookmark'

    def test_func(self):
        # Authorization: sahibi değilse VE public değilse erişemesin
        bookmark = self.get_object()
        return bookmark.owner == self.request.user or bookmark.is_public


class BookmarkCreateView(LoginRequiredMixin, CreateView):
    model = Bookmark
    form_class = BookmarkForm
    template_name = 'bookmarks/bookmark_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Bookmark eklendi.')
        return super().form_valid(form)


class BookmarkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bookmark
    form_class = BookmarkForm
    template_name = 'bookmarks/bookmark_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Bookmark güncellendi.')
        return super().form_valid(form)


class BookmarkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bookmark
    template_name = 'bookmarks/bookmark_confirm_delete.html'
    success_url = reverse_lazy('bookmark_list')

    def test_func(self):
        return self.get_object().owner == self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Bookmark silindi.')
        return super().form_valid(form)

@login_required
@require_POST
def toggle_favorite(request, pk):
    """AJAX: bookmark'ı favori yap / favorilikten çıkar."""
    bookmark = get_object_or_404(Bookmark, pk=pk, owner=request.user)
    bookmark.is_favorite = not bookmark.is_favorite
    bookmark.save(update_fields=['is_favorite'])
    return JsonResponse({'is_favorite': bookmark.is_favorite})
    

# ---------- Collection CRUD ----------

class CollectionListView(LoginRequiredMixin, ListView):
    model = Collection
    template_name = 'bookmarks/collection_list.html'
    context_object_name = 'collections'

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class CollectionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Collection
    template_name = 'bookmarks/collection_detail.html'
    context_object_name = 'collection'

    def test_func(self):
        return self.get_object().owner == self.request.user


class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    form_class = CollectionForm
    template_name = 'bookmarks/collection_form.html'
    success_url = reverse_lazy('collection_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Koleksiyon oluşturuldu.')
        return super().form_valid(form)


class CollectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Collection
    form_class = CollectionForm
    template_name = 'bookmarks/collection_form.html'
    success_url = reverse_lazy('collection_list')

    def test_func(self):
        return self.get_object().owner == self.request.user


class CollectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Collection
    template_name = 'bookmarks/collection_confirm_delete.html'
    success_url = reverse_lazy('collection_list')

    def test_func(self):
        return self.get_object().owner == self.request.user
        
