# Django imports
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

# Third-party imports
from taggit.managers import TaggableManager
from taggit.models import Tag, TaggedItemBase

# Create your models here.
class TaggedProblem(TaggedItemBase):
    content_object = models.ForeignKey('Problem', on_delete=models.CASCADE)

class Problem(models.Model):
    body = models.TextField()
    pub_date = models.DateTimeField("date published", default=timezone.now)

    # Generic relation to a source
    source_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    source_object_id = models.PositiveIntegerField(null=True, blank=True)
    source = GenericForeignKey('source_content_type', 'source_object_id')
    tags = TaggableManager(through=TaggedProblem)

    class Meta:
        verbose_name = "problem"
        verbose_name_plural = "problems"
        ordering = ['-pub_date']

    def __str__(self):
        return (self.body[:75] + '...') if len(self.body) > 75 else self.body

class Source(models.Model):
    """Abstract base model for all sources."""
    class Meta:
        # This ensures that Source doesn't get its own table and avoids the 'id' clash.
        abstract = True

    def __str__(self):
        raise NotImplementedError("Subclasses must implement __str__")

class BookSource(Source):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)

    def __str__(self):
        return f"Book: {self.title} by {self.author}"
    
    class Meta:
        unique_together = ('title', 'author')

class PersonSource(Source):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class YouTubeVideoSource(Source):
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    def __str__(self):
        return self.title


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
