from django.urls import path

from . import views

app_name = "problems"
urlpatterns = [
    # problems
    # ex: /problems/
    path("problems/", views.ProblemListView.as_view(), name="problem-list"),
    # ex: /problems/5/
    path("problems/<int:pk>/", views.ProblemDetailView.as_view(), name="problem-detail"),

    # decks
    # ex: /decks/
    path("decks/", views.DeckListView.as_view(), name="deck-list"),
    # ex: /decks/5/
    path("decks/<int:pk>/", views.DeckDetailView.as_view(), name="deck-detail"),
    # ex /decks/5/practice/
    path('decks/<int:deck_id>/practice/', views.deck_practice, name='deck-practice'),

    # tiptap
    path('tiptap/image-upload/', views.tiptap_image_upload, name='tiptap-image-upload'),
    
]

from django.conf.urls.static import static
from django.conf import settings
# --- Add this section ---
# This is for serving media files during development.
# It is not needed in production, as your web server (e.g., Nginx)
# should be configured to serve media files directly.
#if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)