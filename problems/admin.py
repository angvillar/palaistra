# Django imports
from django.contrib import admin
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
    PersonSource,
    Problem,
    Solution,
    TaggedProblem,
    YouTubeVideoSource,
)

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
    form = ProblemAdminForm
    inlines = (
        TaggedProblemInline,
        HintInline,
        SolutionInline,
    )
    list_display = ('__str__', 'get_tags', 'pub_date')
    list_filter = ('tags',)
    search_fields = ('body',)

    class Media:
        js = (
            'admin/js/problem_admin.js', # Your existing JS
            'admin/js/problem_source_admin.js', # Corrected path
            'admin/js/related_popup.js'
        )

    # Define fieldsets to correctly group the fields for the JS to work
    fieldsets = (
        (None, {
            'fields': (
                'body',
                'get_problem_link_helper', # Our new helper field
                'pub_date'
            )
        }),
        ('SOURCE INFORMATION', {
            'classes': ('collapse',),
            'fields': (
                'source_type',
                'book_source', # Book field
                'person_source', # Person field
                # YouTubeVideoSource is not selectable, so it's removed
            ),
        }),
    )

    readonly_fields = ('get_problem_link_helper',)

    def get_form(self, request, obj=None, **kwargs):
        # Pass the admin_site to the form to enable the '+' button
        form = super().get_form(request, obj, **kwargs)
        form.admin_site = self.admin_site
        return form

    def save_model(self, request, obj, form, change):
        source_type = form.cleaned_data.get('source_type')
        new_source = None

        if source_type == 'book':
            new_source = form.cleaned_data.get('book_source')
        elif source_type == 'person':
            new_source = form.cleaned_data.get('person_source')
        # No 'youtube' case as it's not selectable

        # If the source is changing or being cleared, we just update the reference.
        # We no longer delete the old source from here, as it might be used by other problems.
        obj.source = new_source

        # Save the Problem instance first to get an ID
        super().save_model(request, obj, form, change)

    def get_tags(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    get_tags.short_description = 'Tags'

    def get_problem_link_helper(self, obj):
        from django.utils.html import format_html
        return format_html(
            # The `id` must be on the `<a>` tag itself for Django's JS to name the popup window correctly.
            # The `data-id` attribute tells our custom JS which textarea to target.
            '<a href="{}" id="lookup_id_body" class="related-widget-wrapper-link" data-popup="yes" data-id="id_body" title="Select a problem to link">Select a problem to link</a>',
            #'<a href="{}" id="lookup_id_body" class="related-widget-wrapper-link" data-popup="yes" data-id="id_body" title="Select a problem to link"  onclick="return showRelatedObjectLookupPopup(this);">Select a problem to link</a>',
            reverse('admin:problems_problem_changelist') + '?_to_field=id&_popup=1'
        )
    get_problem_link_helper.short_description = 'Link to Problem'
    get_problem_link_helper.allow_tags = True

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
admin.site.register(YouTubeVideoSource)
admin.site.register(PersonSource)