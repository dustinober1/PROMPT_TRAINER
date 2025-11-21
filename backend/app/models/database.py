"""
Database Models for Prompt Trainer

This module defines all database tables using SQLAlchemy ORM.
Each class represents a table, and each instance is a row in that table.

Tech Tip: SQLAlchemy relationships automatically handle foreign keys and joins.
You can access related data like: paper.evaluations or rubric.criteria
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone

# Base class for all models
Base = declarative_base()


def utc_now():
    """Return timezone-aware UTC timestamps for defaults."""
    return datetime.now(timezone.utc)


class Paper(Base):
    """
    Stores submitted papers to be graded.

    Tech Tip: __tablename__ determines the actual database table name.
    Column types (String, Text, Integer) map to database column types.
    """
    __tablename__ = "papers"

    # Primary key - unique identifier for each paper
    id = Column(Integer, primary_key=True, index=True)

    # Paper metadata
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # Text allows unlimited length
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="SET NULL"), nullable=True)
    submission_date = Column(DateTime, default=utc_now)
    created_at = Column(DateTime, default=utc_now)

    # Relationships - SQLAlchemy automatically handles the connections
    # 'back_populates' creates a two-way link between models
    evaluations = relationship("Evaluation", back_populates="paper", cascade="all, delete-orphan")
    rubric = relationship("Rubric", back_populates="papers")

    def __repr__(self):
        """String representation for debugging"""
        return f"<Paper(id={self.id}, title='{self.title}')>"

    @property
    def rubric_name(self):
        """Helper to expose rubric name without extra queries"""
        return self.rubric.name if self.rubric else None


class Rubric(Base):
    """
    Defines grading rubrics with multiple criteria.

    A rubric is like a checklist of things to evaluate in a paper.
    Example: "Grammar", "Thesis Clarity", "Evidence Quality"
    """
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)

    # Rubric information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Scoring type: how to score each criterion
    # Options: "yes_no", "meets", "numerical"
    scoring_type = Column(String(50), default="yes_no")

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    # cascade="all, delete-orphan" means: if rubric is deleted, delete its criteria too
    criteria = relationship("Criterion", back_populates="rubric", cascade="all, delete-orphan")
    papers = relationship("Paper", back_populates="rubric", passive_deletes=True)
    evaluations = relationship("Evaluation", back_populates="rubric")

    def __repr__(self):
        return f"<Rubric(id={self.id}, name='{self.name}', type='{self.scoring_type}')>"


class Criterion(Base):
    """
    Individual criteria within a rubric.

    Example criteria:
    - "Has a clear thesis statement"
    - "Uses proper grammar and spelling"
    - "Provides supporting evidence"
    """
    __tablename__ = "criteria"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key - links to parent rubric
    # ondelete="CASCADE" means: if rubric is deleted, delete these criteria automatically
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False)

    # Criterion details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)  # For display ordering (1st, 2nd, 3rd...)

    # Relationship back to parent rubric
    rubric = relationship("Rubric", back_populates="criteria")

    def __repr__(self):
        return f"<Criterion(id={self.id}, name='{self.name}')>"


class Prompt(Base):
    """
    Stores different versions of prompts used for AI evaluation.

    Each time you improve the prompt, you create a new version.
    This allows tracking which prompt performed better.

    Tech Tip: Only one prompt should have is_active=True at a time.
    """
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)

    # Version tracking
    version = Column(Integer, nullable=False)
    template_text = Column(Text, nullable=False)

    # Optional: track which prompt this was based on
    parent_version_id = Column(Integer, ForeignKey("prompts.id"), nullable=True)

    created_at = Column(DateTime, default=utc_now)
    is_active = Column(Boolean, default=True)

    # Performance metrics (calculated after evaluations)
    accuracy_rate = Column(Float, nullable=True)  # Percentage (0-100)
    total_evaluations = Column(Integer, default=0)

    # Relationships
    evaluations = relationship("Evaluation", back_populates="prompt")

    def __repr__(self):
        active_str = "ACTIVE" if self.is_active else "inactive"
        return f"<Prompt(v{self.version}, {active_str}, accuracy={self.accuracy_rate}%)>"


class Evaluation(Base):
    """
    Stores AI-generated evaluations of papers.

    This is the core of the system: when AI grades a paper using a rubric,
    we create an Evaluation record to store the results.

    Tech Tip: model_response is stored as JSON string for flexibility.
    This allows different rubric types without changing the schema.
    """
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys - what was evaluated, how, and with which prompt
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False)
    rubric_id = Column(Integer, ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)

    # AI model's response
    # Stored as JSON string: {"evaluations": [{"criterion_id": 1, "score": "yes", "reasoning": "..."}]}
    model_response = Column(Text, nullable=False)

    # User feedback
    # NULL = not reviewed yet
    # TRUE = user confirmed it's correct
    # FALSE = user corrected it
    is_correct = Column(Boolean, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    paper = relationship("Paper", back_populates="evaluations")
    rubric = relationship("Rubric", back_populates="evaluations")
    prompt = relationship("Prompt", back_populates="evaluations")
    feedback_entries = relationship("FeedbackEntry", back_populates="evaluation", cascade="all, delete-orphan")

    def __repr__(self):
        status = "✓" if self.is_correct else "✗" if self.is_correct is False else "?"
        return f"<Evaluation(id={self.id}, paper={self.paper_id}, status={status})>"


class FeedbackEntry(Base):
    """
    Stores user corrections when AI evaluations are wrong.

    This is how the system learns! When a user says "the AI got this wrong,
    the right answer is X", we store that here.

    Later, this feedback will be used to improve prompts.
    """
    __tablename__ = "feedback_entries"

    id = Column(Integer, primary_key=True, index=True)

    # Which evaluation and criterion this feedback is about
    evaluation_id = Column(Integer, ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False)
    criterion_id = Column(Integer, ForeignKey("criteria.id"), nullable=False)

    # What the model said vs what the user says is correct
    model_score = Column(String(50), nullable=False)  # e.g., "yes", "no", "8"
    user_corrected_score = Column(String(50), nullable=False)  # The right answer

    # Optional: user's explanation of why it was wrong
    user_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="feedback_entries")

    def __repr__(self):
        return f"<FeedbackEntry(id={self.id}, {self.model_score} → {self.user_corrected_score})>"


# Tech Tip: Why use relationships?
# Instead of writing SQL joins like:
#   SELECT * FROM criteria WHERE rubric_id = 5
#
# You can just do:
#   rubric.criteria  # Returns list of all criteria for this rubric
#
# SQLAlchemy handles the database query automatically!
