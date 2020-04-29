from django.urls import path
from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name='index'),
    path('about/', views.About.as_view(), name='about'),
    path('register/', views.register, name='register'),
    path('organise/', views.create_term, name='create-term'),
    path('term/<int:pk>', views.TermDetail.as_view(), name='term-detail'),
    path('subj/edit/<int:pk>', views.ResultUpdateForm.as_view(), name='add-result'),
    path('term/analyse/<int:pk>', views.AnalyseTerm.as_view(), name='term-analysis'),
    path('daily/analyse/<int:pk>', views.DailyAnalysis.as_view(), name='daily-analysis'),
    path('term/delete/<int:pk>', views.TermDelete.as_view(), name='term-delete'),
    path('term/edit/daily_activity/<int:pk>/<int:year>/<int:month>/<int:day>', views.EditDailyActivity.as_view(), name='edit-daily-activity'),

]
