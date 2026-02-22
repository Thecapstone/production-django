from typing import TYPE_CHECKING, TypedDict
from dataclasses import dataclass
from django.db import models
from django.db.models import Manager as Manager_
from django.contrib.contenttypes.models import ContentType

from core.apps.projects.models import Project


if TYPE_CHECKING:
    from core.apps.users.models import Community  # noqa: TC004
    from core.apps.users.models import User  # noqa: TC004

    from core.apps.posts.models import IdeaThread
    from core.apps.posts.models import LongDraft
    from core.apps.posts.models import QuestionAndAnswer
    from core.apps.projects.models import Project


@dataclass
class BasePostType:
    user: User
    community: Community
    project: Project
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
        def create_post(self: models.QuerySet["IdeaThread" | "QuestionAndAnswer" | "LongDraft"], data: QuestionAndAnswerPostType | IdeaThreadPostType | LongDraftPostType, **kwargs) -> IdeaThread| LongDraft| QuestionAndAnswer:

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
        
        def update_post(self, post_id, user_id, title: str | None = None) -> IdeaThread| LongDraft| QuestionAndAnswer:
            post = self.get(id=post_id)

            if post.user_id != user_id:
                raise Exception("You cannot edit a post that you did not create")
            
            if hasattr(post, "title") and title is not None:
                post.title = title

            post.save()
            return post

    
    class QuestionAndAnswerManager(Base, Manager_):
        def create_question_and_answer_post(self: models.QuerySet["QuestionAndAnswer"], Base) -> "QuestionAndAnswer":
            question_and_answer =  Base.create_post(title=self.title, content=self.content, choices=self.choices)
            question_and_answer.save(using=self._db)

            return question_and_answer
        def update_question_and_answer_post(self: models.QuerySet['QuestionAndAnswer'], post_id, content, title, choices) -> "QuestionAndAnswer":
            question_and_answer = self.get(id=post_id)
            if content:
                question_and_answer.content = content
            if title:
                question_and_answer.title = title
            if choices:
                question_and_answer.choices = choices
            
            question_and_answer.save(using=self.db)
            return question_and_answer

    class IdeaThreadManager(Base, Manager_):
        def create_idea_thread_post(self: models.QuerySet["IdeaThread"], content) -> "IdeaThread":
            idea_thread = self.model(content=content)
            idea_thread.save(using=self._db)

            return idea_thread

        def update_idea_thread_post(self: models.QuerySet['QuestionAndAnswer'], post_id, content) -> "QuestionAndAnswer":
            question_and_answer = self.get(id=post_id)
            if content:
                question_and_answer.content = content
            
            question_and_answer.save(using=self.db)
            return question_and_answer
        

    class LongDraftManager(Base, Manager_):
        def create_long_draft_post(self: models.QuerySet["LongDraft"], content) -> "LongDraft":
            long_draft = self.model(content=content)
            long_draft.save(using=self._db)

            return long_draft