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

def _advance_practice_session(request, deck_id):
    """
    Helper function to advance the deck practice session to the next problem
    or end the session if all problems have been seen.
    """
    problem_ids = request.session.get('shuffled_problems', [])
    request.session['current_problem_index'] += 1

    if request.session.get('current_problem_index', 0) < len(problem_ids):
        return redirect('problems:deck-practice', deck_id=deck_id)
    else:
        # End of the deck, clean up session and redirect
        del request.session['shuffled_problems']
        del request.session['current_problem_index']
        del request.session['current_deck_id']
        return redirect('problems:deck-detail', pk=deck_id)

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
            return _advance_practice_session(request, deck_id)
        
        # New block for the skip button
        elif 'skip_problem' in request.POST:
            # If an attempt is in progress, end it without saving
            if active_attempt:
                active_attempt.delete() # Or set a flag to mark it as skipped
            return _advance_practice_session(request, deck_id)

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

from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import default_storage
from django.http import JsonResponse

@staff_member_required
def tiptap_image_upload(request):
    """
    Handles image uploads from the Tiptap editor.
    """
    print("\n--- Tiptap Image Upload View ---")
    print(f"Request method: {request.method}")
    if request.method == 'POST' and request.FILES.get('image'):
        print("Request is POST and contains an image file.")
        image = request.FILES['image']
        print(f"Image received: {image.name} ({image.size} bytes)")
        # Define a path to save the image, e.g., 'tiptap_uploads/...'
        file_name = default_storage.save(f"tiptap_uploads/{image.name}", image)
        print(f"Image saved as: {file_name}")
        # Get the URL for the saved file
        file_url = default_storage.url(file_name)
        print(f"Returning success JSON with URL: {file_url}")

        
        return JsonResponse({'url': file_url})
    print("Request failed validation (not POST or no image file).")
    return JsonResponse(
        {'error': 'Invalid request or no image file provided.'}, 
        status=400
    )
