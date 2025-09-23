import random

from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView
from .models import Attempt, Deck, Problem

class ProblemDetailView(DetailView):
    model = Problem

class ProblemListView(ListView):
    model = Problem
    paginate_by = 5
    context_object_name = 'problem_list'
    template_name = 'problems/problem_list.html'
        
class DeckListView(ListView):
    model = Deck

class DeckDetailView(DetailView):
    model = Deck

def deck_practice(request, deck_id):
    deck = get_object_or_404(Deck, pk=deck_id)

    if 'shuffled_problems' not in request.session or request.session.get('current_deck_id') != deck.id:
        problem_ids = list(deck.problems.values_list('id', flat=True))
        random.shuffle(problem_ids)
        request.session['shuffled_problems'] = problem_ids
        request.session['current_problem_index'] = 0
        request.session['current_deck_id'] = deck.id

    problem_ids = request.session.get('shuffled_problems')
    current_index = request.session.get('current_problem_index', 0)

    if not problem_ids:
        return render(request, 'problems/no_problems.html', {'deck': deck})

    current_problem_id = problem_ids[current_index]
    problem = get_object_or_404(Problem, pk=current_problem_id)
    
    active_attempt = Attempt.objects.filter(
        problem=problem,
        end_time__isnull=True
    ).first()

    if request.method == 'POST':
        if 'start_attempt' in request.POST:
            if not active_attempt:
                Attempt.objects.create(problem=problem)
            return redirect('problems:deck-practice', deck_id=deck_id)
        
        elif 'finish_attempt' in request.POST:
            if active_attempt:
                active_attempt.end_time = timezone.now()
                active_attempt.time_taken = active_attempt.end_time - active_attempt.start_time
                active_attempt.save()
            
            # This logic will be handled by the 'skip' block below.
            request.session['current_problem_index'] += 1

            if request.session['current_problem_index'] < len(problem_ids):
                return redirect('problems:deck-practice', deck_id=deck_id)
            else:
                del request.session['shuffled_problems']
                del request.session['current_problem_index']
                del request.session['current_deck_id']
                return redirect('problems:deck-detail', pk=deck_id)
        
        # New block for the skip button
        elif 'skip_problem' in request.POST:
            # If an attempt is in progress, end it without saving
            if active_attempt:
                active_attempt.delete() # Or set a flag to mark it as skipped
            
            # Increment the index to move to the next problem
            request.session['current_problem_index'] += 1

            if request.session['current_problem_index'] < len(problem_ids):
                return redirect('problems:deck-practice', deck_id=deck_id)
            else:
                del request.session['shuffled_problems']
                del request.session['current_problem_index']
                del request.session['current_deck_id']
                return redirect('problems:deck-detail', pk=deck_id)

    attempts_count = problem.attempts.count()

    context = {
        'deck': deck,
        'problem': problem,
        'active_attempt': active_attempt,
        'current_index': current_index + 1,
        'total_problems': len(problem_ids),
        'attempts_count': attempts_count,
    }
    return render(request, 'problems/deck_practice.html', context)