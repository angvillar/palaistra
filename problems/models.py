# Django imports
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# Third-party imports
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItemBase

# Create your models here.
class TaggedProblem(TaggedItemBase):
    content_object = models.ForeignKey('Problem', on_delete=models.CASCADE)

class Problem(models.Model):
    body = models.TextField()
    pub_date = models.DateTimeField("date published", default=timezone.now)
    tags = TaggableManager(through=TaggedProblem)

    # Book Source Information
    book_source = models.ForeignKey(
        'BookSource',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    page_number = models.PositiveIntegerField(null=True, blank=True)
    problem_number = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "problem"
        verbose_name_plural = "problems"
        ordering = ['-pub_date']

    def __str__(self):
        return (self.body[:75] + '...') if len(self.body) > 75 else self.body
    

class BookSource(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        unique_together = ('title', 'author')
        ordering = ['title']

class Solution(models.Model):
    body = models.TextField()
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='solutions')

    def __str__(self):
        return f"Solution for Problem #{self.problem.pk}"

class Hint(models.Model):
    body = models.TextField()
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='hints')

    def __str__(self):
        return f"Hint for Problem #{self.problem.pk}"

class Attempt(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Attempt for Problem #{self.problem.pk}"

class DeckTagFilter(models.Model):
    class FilterType(models.TextChoices):
        INCLUDE = 'INCLUDE', 'Include'
        EXCLUDE = 'EXCLUDE', 'Exclude'

    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    deck = models.ForeignKey('Deck', on_delete=models.CASCADE)
    filter_type = models.CharField(
        max_length=7,
        choices=FilterType.choices,
        default=FilterType.INCLUDE,
    )

    class Meta:
        unique_together = ('tag', 'deck') # A tag can only be used once per deck

class Deck(models.Model):
    name = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, through=DeckTagFilter, related_name='decks', blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name 

    def get_include_tags(self):
        return self.tags.filter(decktagfilter__filter_type=DeckTagFilter.FilterType.INCLUDE)

    def get_exclude_tags(self):
        return self.tags.filter(decktagfilter__filter_type=DeckTagFilter.FilterType.EXCLUDE)

    @property
    def problems(self):
        """
        Returns a queryset of problems that match the deck's tag filters.
        - Must have ANY of the include_tags.
        - Must NOT have ANY of the exclude_tags.
        """
        qs = Problem.objects.all()
        
        include_tags = self.tags.filter(decktagfilter__filter_type=DeckTagFilter.FilterType.INCLUDE)
        include_tag_names = [tag.name for tag in include_tags]
        if include_tag_names:
            qs = qs.filter(tags__name__in=include_tag_names).distinct()

        exclude_tags = self.tags.filter(decktagfilter__filter_type=DeckTagFilter.FilterType.EXCLUDE)
        exclude_tag_names = [tag.name for tag in exclude_tags]
        if exclude_tag_names:
            qs = qs.exclude(tags__name__in=exclude_tag_names)
            
        return qs
