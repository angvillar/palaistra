# Django imports
from django import forms

# Third-party imports
from taggit.forms import TagWidget
from taggit.models import Tag

# Local application imports
from .models import (
    DeckTagFilter,
    Problem,
    Solution,
    TaggedProblem,
)
class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ["body"]
        widgets = {
            'body': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class ProblemAdminForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = (
            'body', 
            'pub_date',
            'book_source',
            'page_number',
            'problem_number',
        )

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