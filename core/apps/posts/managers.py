from django.db import models
from django.db.models import Manager as Manager_
from django.contrib.contenttypes.models import ContentType

from core.apps.users.models import User, Community
from core.apps.projects.models import Project


from .models import IdeaThread, QuestionAndAnswer, LongDraft


class PostsManager():

    class Base:
        def create_post(self: models.QuerySet["IdeaThread" | "QuestionAndAnswer" | "LongDraft"], user, post_type: str, community: str | None, project: str | None, **kwargs) -> "IdeaThread| LongDraft| QuestionAndAnswer":
            content_type = ContentType.objects.get(model=post_type)

            post = self.create(user=user, content_type=content_type, **kwargs)
            if community is not None:
                comm = Community.objects.get(community)
                post.community = comm
            
            if project is not None:
                proj = Project.objects.get(title=project)
                post.project = proj
            
            post.save(using=self._db)
            return post
    
    class Q_And_A_Manager(Base, Manager_):
        def create_q_and_a_post(self: models.QuerySet["QuestionAndAnswer"], content, choices) -> "QuestionAndAnswer":
            question_and_answer =  self.model(content=content, choices=choices)
            question_and_answer.save(using=self._db)

            return question_and_answer
        
    class IdeaThreadManager(Base, Manager_):
        def create_idea_thread_post(self: models.QuerySet["IdeaThread"], content) -> "IdeaThread":
            idea_thread = self.model(content=content)
            idea_thread.save(using=self._db)

            return idea_thread
    
    class LongDraftManager(Base, Manager_):
        def create_long_draft_post(self: models.QuerySet["LongDraft"], content) -> "LongDraft":
            long_draft = self.model(content=content)
            long_draft.save(using=self._db)

            return long_draft

