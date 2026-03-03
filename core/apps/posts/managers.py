from __future__ import annotations
from typing import TYPE_CHECKING, Union
from dataclasses import dataclass
from django.db import models
from django.db.models import Manager as Manager_
from django.conf import settings


from core.apps.projects.models import Project

#if not settings.DEBUG:
if TYPE_CHECKING:
    from core.apps.users.models import Community  # noqa: TC004
    from core.apps.users.models import User  # noqa: TC004

    from core.apps.posts.models import IdeaThread
    from core.apps.posts.models import LongDraft
    from core.apps.posts.models import QuestionAndAnswer
    from core.apps.projects.models import Project



@dataclass
class BasePostType:
    user: str
    community: str
    project: str
    content: str

@dataclass
class PostExtrasType(BasePostType):
    title: str

@dataclass
class QuestionAndAnswerPostType(PostExtrasType):
    choices: list[str] | None

@dataclass
class IdeaThreadPostType(BasePostType):
    ...

@dataclass
class LongDraftPostType(PostExtrasType):
    ...


class PostsManager:

    class Base:
        def create_post(self: 
            Union[
            models.QuerySet[ "QuestionAndAnswer"] | 
            models.QuerySet[ "IdeaThread"] | 
            models.QuerySet[ "LongDraft"]
            ],
            data: Union[
                QuestionAndAnswerPostType | 
                IdeaThreadPostType | 
                LongDraftPostType
            ], 
            **kwargs
        ) -> Union["QuestionAndAnswer" | "IdeaThread" | "LongDraft"]:
            """ Creates a new post (QuestionAndAnswer, IdeaThread, or LongDraft) based on the post type."""

            post_type = self.__class__.__name__ # IdeaThread or QuestionAndAnswer or LongDraft
            base_data = BasePostType(**{k: v for k, v in data.items() if k in BasePostType.__annotations__}).__dict__
            post = self.model(**base_data)
            match post_type:
                case "QuestionAndAnswer":
                    post.choices = data["choices"]
                    post.title = data["title"]
                case "IdeaThread":
                    ...
                case "LongDraft":
                    post.title = data["title"]
                case _:
                    raise Exception("Invalid post type")

            return post.save()
        
        def update_post(self, post_id, user_id, title: str | None = None, content:str|None=None, choices:str|None=None) -> IdeaThread| LongDraft| QuestionAndAnswer:
            """
            Updates a post (QuestionAndAnswer, IdeaThread, or LongDraft) based on the post type and post id. Only the original creator can update a post."""
            post = self.get(id=post_id)

            if post.user_id != user_id:
                raise Exception("You cannot edit a post that you did not create")
            
            if hasattr(post, "title") and title is not None:
                post.title = title
            
            if hasattr(post, content):
                post.content = content
            
            if hasattr(post, choices):
                post.choices = choices

            post.save()
            return post

    
    class QuestionAndAnswerManager(Base, Manager_["PostsManager"]):
        def create_question_and_answer_post(self) -> models.QuerySet["QuestionAndAnswer"]:
            return PostsManager.QuestionAndAnswerManager(self.model, using=self._db)

        def update_question_and_answer_post(self) -> "QuestionAndAnswer":
            return PostsManager.QuestionAndAnswerManager(self.update_post(title=self.title, content=self.content, choices=self.choices), using=self._db)
            

    class IdeaThreadManager(Base, Manager_["PostsManager"]):
        def create_idea_thread_post(self) -> models.QuerySet["IdeaThread"]:
            return PostsManager.IdeaThreadManager(self.model, using=self._db)
        
        def update_idea_thread_post(self) -> "IdeaThread":
            return PostsManager.IdeaThreadManager(self.update_post(content=self.content), using=self._db)


    class LongDraftManager(Base, Manager_["PostsManager"]):
        def create_long_draft_post(self) -> models.QuerySet['LongDraft']:
            return PostsManager.LongDraftManager(self.model, using=self._db)
         
        def update_long_draft_post(self) -> "LongDraft":
            return PostsManager.LongDraftManager(self.update_post(title=self.title, content=self.content), using=self._db)