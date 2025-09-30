# Django imports
from django.contrib import admin
from django.forms import Textarea
from django.urls import reverse

# Local application imports
from .forms import (
    BaseDeckTagFilterFormSet,
    BaseTaggedProblemFormSet,
    DeckTagFilterForm,
    ProblemAdminForm,
    SolutionForm,
    TaggedProblemForm,
)
from .models import (
    Attempt,
    BookSource,
    Deck,
    DeckTagFilter,
    Hint,
    Problem,
    Solution,
    TaggedProblem,
)

from django.utils.html import format_html
from django.templatetags.static import static

class TiptapWidget(Textarea):
    """
    A custom widget to render a Tiptap editor.
    """
    template_name = 'admin/widgets/tiptap_editor.html'

    class Media:
        # Tiptap and its extensions from a CDN
        js = [
            format_html(
                '<script type="module" src="{}"></script>', 
                static('admin/js/tiptap_editor.js'),
            ),
            format_html(
                '<script type="module" src="{}"></script>',
                static('admin/js/related_popup.js')
            ), 
            'admin/js/problem_admin.js',
        ]
 
        css = {
            'all': ('admin/css/tiptap_editor.css',)
        }

class SolutionInline(admin.TabularInline):
    form = SolutionForm
    model = Solution
    extra = 0
    classes = ('collapse',)

class HintInline(admin.TabularInline):
    model = Hint
    extra = 0
    classes = ('collapse',)

class TaggedProblemInline(admin.TabularInline):
    model = TaggedProblem
    form = TaggedProblemForm
    formset = BaseTaggedProblemFormSet
    extra = 1
    verbose_name = 'Tag'
    verbose_name_plural = 'Tags'
    classes = ('collapse',)

class ProblemAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        # 1. Generate the URL on the server
        popup_url = reverse('admin:problems_problem_changelist') + '?_to_field=id&_popup=1'
        image_upload_url = reverse('problems:tiptap-image-upload') # For image uploads

        # 2. Pass it to the widget's attributes
        kwargs['widgets'] = {
            'body': TiptapWidget(attrs={
                'data_popup_url': popup_url,
                'data_image_upload_url': image_upload_url,
            })
        }
        return super().get_form(request, obj, **kwargs)

    form = ProblemAdminForm
    inlines = (
        TaggedProblemInline,
        HintInline,
        SolutionInline,
    )
    list_display = ('__str__', 'get_tags', 'pub_date')
    list_filter = ('tags',)
    search_fields = ('body',)
    fieldsets = (
        (None, {
            'fields': ('body', 'pub_date')
        }),
        ('Book Source Information', {
            'classes': ('collapse',),
            'fields': ('book_source', 'page_number', 'problem_number')
        })
    )

    def get_tags(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    get_tags.short_description = 'Tags'

class DeckTagFilterInline(admin.TabularInline):
    form = DeckTagFilterForm
    formset = BaseDeckTagFilterFormSet
    model = DeckTagFilter
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        # Pass the admin_site to the formset, which then passes it to the form
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.admin_site = self.admin_site
        return formset

class DeckAdmin(admin.ModelAdmin):
    inlines = (DeckTagFilterInline,)
    list_display = ('name', 'get_include_tags_list', 'get_exclude_tags_list')

    class Media:
        js = (
            'admin/js/deck_admin.js',
        )

    def get_include_tags_list(self, obj):
        return ", ".join(t.name for t in obj.get_include_tags())
    get_include_tags_list.short_description = 'Include Tags'

    def get_exclude_tags_list(self, obj):
        return ", ".join(t.name for t in obj.get_exclude_tags())
    get_exclude_tags_list.short_description = 'Exclude Tags'

admin.site.register(Deck, DeckAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(BookSource)