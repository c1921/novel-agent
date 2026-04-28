from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    title: str
    genre: str = ""
    target_audience: str = ""
    style_guide: str = ""


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = None
    genre: str | None = None
    target_audience: str | None = None
    style_guide: str | None = None


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CharacterBase(BaseModel):
    name: str
    role: str = ""
    personality: str = ""
    goal: str = ""
    speech_style: str = ""
    constraints: str = ""
    background: str = ""


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    personality: str | None = None
    goal: str | None = None
    speech_style: str | None = None
    constraints: str | None = None
    background: str | None = None


class CharacterRead(CharacterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class WorldSettingBase(BaseModel):
    title: str
    content: str = ""
    category: str = ""


class WorldSettingCreate(WorldSettingBase):
    pass


class WorldSettingUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None


class WorldSettingRead(WorldSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class OutlineBase(BaseModel):
    title: str
    content: str = ""


class OutlineCreate(OutlineBase):
    pass


class OutlineUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class OutlineRead(OutlineBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class ChapterBase(BaseModel):
    chapter_number: int
    title: str = ""
    goal: str = ""
    outline: str = ""
    draft: str = ""
    polished_draft: str = ""
    status: str = "planned"


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    chapter_number: int | None = None
    title: str | None = None
    goal: str | None = None
    outline: str | None = None
    draft: str | None = None
    polished_draft: str | None = None
    status: str | None = None


class ChapterRead(ChapterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class ForeshadowingBase(BaseModel):
    name: str
    setup: str = ""
    payoff_plan: str = ""
    status: str = "planned"


class ForeshadowingCreate(ForeshadowingBase):
    pass


class ForeshadowingUpdate(BaseModel):
    name: str | None = None
    setup: str | None = None
    payoff_plan: str | None = None
    status: str | None = None


class ForeshadowingRead(ForeshadowingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class ProjectDetail(ProjectRead):
    characters: list[CharacterRead] = []
    world_settings: list[WorldSettingRead] = []
    outlines: list[OutlineRead] = []
    chapters: list[ChapterRead] = []
    foreshadowings: list[ForeshadowingRead] = []


class PlotQuestion(BaseModel):
    id: str
    type: Literal["must_ask", "optional", "auto_decidable"]
    question: str
    reason: str = ""
    options: list[str] = Field(default_factory=list)


class QuestionAnswer(BaseModel):
    question_id: str
    answer: str


class ConsistencyIssue(BaseModel):
    severity: Literal["high", "medium", "low"]
    type: Literal["character", "timeline", "worldbuilding", "plot", "foreshadowing", "style"]
    description: str
    suggestion: str


class ConsistencyReport(BaseModel):
    summary: str
    issues: list[ConsistencyIssue] = Field(default_factory=list)


class StartChapterRequest(BaseModel):
    project_id: int
    chapter_id: int | None = None
    user_goal: str


class StartChapterResponse(BaseModel):
    session_id: str
    next_action: str
    plot_questions: list[PlotQuestion]
    auto_decidable: list[str] = []


class AnswerQuestionsRequest(BaseModel):
    session_id: str
    answers: list[QuestionAnswer]


class AnswerQuestionsResponse(BaseModel):
    next_action: str
    chapter_outline: str


class ApproveOutlineRequest(BaseModel):
    session_id: str
    approved: bool
    revision_instruction: str = ""


class ApproveOutlineResponse(BaseModel):
    next_action: str
    chapter_outline: str = ""
    draft: str = ""
    polished_draft: str = ""
    consistency_report: ConsistencyReport | None = None


class SaveChapterRequest(BaseModel):
    session_id: str
    use_polished: bool = True


class IndexResponse(BaseModel):
    project_id: int
    document_count: int
    backend: str
    message: str


NovelAgentState = dict[str, Any]
