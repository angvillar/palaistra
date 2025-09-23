# palaistra/problems/templatetags/problem_tags.py
import re
from django import template
from django.urls import reverse
from django.utils.html import format_html
from ..models import Problem

register = template.Library()

@register.filter(name='render_problem_links')
def render_problem_links(text):
    """
    Finds all occurrences of [[problem:ID]] and replaces them with
    a link to the corresponding problem.
    """
    def replace_link(match):
        problem_id = match.group(1)
        try:
            problem = Problem.objects.get(pk=problem_id)
            url = reverse('problems:problem-detail', args=[problem.id])
            # Using a snippet of the body for the link text
            link_text = (problem.body[:30] + '...') if len(problem.body) > 30 else problem.body
            return format_html('<a href="{}">{}</a>', url, link_text)
        except Problem.DoesNotExist:
            return f"[[Invalid Problem ID: {problem_id}]]"

    pattern = re.compile(r'\[\[problem:(\d+)\]\]')
    return pattern.sub(replace_link, text)
