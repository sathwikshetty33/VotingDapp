from django.urls import path
from . import views

urlpatterns = [
    path('register-candidate/', views.register_candidate),
    path('register-voter/', views.register_voter),
    path('vote/', views.cast_vote),
    path('results/', views.get_result),
    path('get-can/', views.get_candidates),
    path('login/',views.logins),
    path('voting/',views.voting,name='voting')
]
