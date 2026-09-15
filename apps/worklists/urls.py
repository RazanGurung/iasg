from django.urls import path

from . import views

urlpatterns = [
    path("tasks/", views.tasks, name="worklist_tasks"),
    path("additions-closures/", views.additions_closures, name="worklist_additions_closures"),
    path("client/<int:pk>/tasks/save/", views.task_save, name="task_save"),
    path("client/<int:pk>/tasks/<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path("client/<int:pk>/changes/save/", views.change_save, name="change_save"),
    path("client/<int:pk>/changes/<int:change_id>/delete/", views.change_delete, name="change_delete"),
]
