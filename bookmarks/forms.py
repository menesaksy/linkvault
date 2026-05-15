from django import forms
from .models import Bookmark, Collection, Tag


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Koleksiyon adı'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                 'placeholder': 'Kısa açıklama (opsiyonel)'}),
        }


class BookmarkForm(forms.ModelForm):
    # Etiketleri virgülle ayrılmış metin olarak girmek kullanıcı için daha kolay
    tags_input = forms.CharField(
        required=False,
        label='Etiketler',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'python, güvenlik, makale (virgülle ayır)'})
    )

    class Meta:
        model = Bookmark
        fields = ['title', 'url', 'description', 'collection', 'is_favorite', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Başlık'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'collection': forms.Select(attrs={'class': 'form-select'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        # Koleksiyon listesini sadece o kullanıcıya ait olanlarla sınırla
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['collection'].queryset = Collection.objects.filter(owner=user)
        self.fields['collection'].required = False
        # Düzenleme modunda mevcut etiketleri input'a doldur
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(
                t.name for t in self.instance.tags.all()
            )

    def clean_tags_input(self):
        """Virgülle ayrılmış metni temiz etiket listesine çevir."""
        raw = self.cleaned_data.get('tags_input', '')
        names = [n.strip().lower() for n in raw.split(',') if n.strip()]
        return names

    def save(self, commit=True):
        bookmark = super().save(commit=commit)
        if commit:
            self._save_tags(bookmark)
        return bookmark

    def _save_tags(self, bookmark):
        tag_names = self.cleaned_data.get('tags_input', [])
        tag_objs = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tag_objs.append(tag)
        bookmark.tags.set(tag_objs)