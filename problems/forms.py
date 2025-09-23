# Django imports
from django import forms

# Third-party imports
from taggit.forms import TagWidget
from taggit.models import Tag

# Local application imports
from .models import (
    BookSource,
    DeckTagFilter,
    PersonSource,
    Problem,
    Solution,
    TaggedProblem,
    YouTubeVideoSource,
)
class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ["body"]
        widgets = {
            'body': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class ProblemAdminForm(forms.ModelForm):
    # Define choices for the source type dropdown
    SOURCE_TYPE_CHOICES = (
        ('', '---------'),
        ('book', 'Book'),
        ('person', 'Person'),
        ('youtube', 'YouTube Video'),
    )
    source_type = forms.ChoiceField(choices=SOURCE_TYPE_CHOICES, required=False, label="Source Type")

    # --- Fields for BookSource ---
    book_source = forms.ModelChoiceField(
        queryset=BookSource.objects.all(), required=False, label="Book"
    )

    # --- Fields for PersonSource ---
    person_source = forms.ModelChoiceField(
        queryset=PersonSource.objects.all(), required=False, label="Person"
    )

    # --- Fields for YouTubeVideoSource ---
    youtube_source = forms.ModelChoiceField(
        queryset=YouTubeVideoSource.objects.all(), required=False, label="YouTube Video"
    )


    class Meta:
        model = Problem
        fields = ('body', 'pub_date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.source:
            source = self.instance.source
            if isinstance(source, BookSource):
                self.initial['source_type'] = 'book'
                self.initial['book_source'] = source
            elif isinstance(source, PersonSource):
                self.initial['source_type'] = 'person'
                self.initial['person_source'] = source
            elif isinstance(source, YouTubeVideoSource):
                self.initial['source_type'] = 'youtube'
                self.initial['youtube_source'] = source

class DeckTagFilterForm(forms.ModelForm):
    class Meta:
        model = DeckTagFilter
        fields = '__all__'
        widgets = {'filter_type': forms.RadioSelect}

class BaseDeckTagFilterFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        tags = set()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            tag = form.cleaned_data.get('tag')
            if tag in tags:
                raise forms.ValidationError("This tag can only be added once per deck.")
            tags.add(tag)

class BaseTaggedProblemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        tags = set()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE', False):
                continue
            tag = form.cleaned_data.get('tag')
            if tag in tags:
                raise forms.ValidationError("This tag can only be added once per problem.")
            tags.add(tag)

class TaggedProblemForm(forms.ModelForm):
    class Meta:
        model = TaggedProblem
        fields = ('tag',)