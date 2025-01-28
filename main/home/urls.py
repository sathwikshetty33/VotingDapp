from django.urls import path
from . import views

urlpatterns = [
    path('register-candidate/', views.register_candidate),
    path('register-voter/', views.register_voter),
    path('vote/', views.cast_vote,name='vote'),
    path('results/', views.get_result),
    path('get-can/', views.get_candidates),
    path('voting-status/',views.voting_status),
    path('',views.logins),
    path('voting/',views.voting,name='voting'),
    path('voter-reg/',views.voter,name='votereg'),
    path('canreg/',views.canreg,name='canreg'),
    path('set-vote-time/', views.set_vote_time,name='man'),

]
