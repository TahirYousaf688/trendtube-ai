"""Complete SQLAlchemy models for TrendTube AI."""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Date,
    DECIMAL,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


# ============================================
# ENUMS
# ============================================
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CREATOR = "creator"
    MEMBER = "member"
    VIEWER = "viewer"


class VideoStatus(str, enum.Enum):
    DRAFT = "draft"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    GENERATING_VOICE = "generating_voice"
    CREATING_VIDEO = "creating_video"
    GENERATING_THUMBNAIL = "generating_thumbnail"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class WorkflowStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    EXPIRED = "expired"
    TRIALING = "trialing"


class TrendSourceType(str, enum.Enum):
    GOOGLE_TRENDS = "google_trends"
    YOUTUBE_TRENDING = "youtube_trending"
    REDDIT = "reddit"
    TWITTER = "twitter"
    NEWS_API = "news_api"
    RSS_FEED = "rss_feed"
    HACKER_NEWS = "hacker_news"
    PRODUCT_HUNT = "product_hunt"
    GITHUB_TRENDING = "github_trending"
    COINMARKETCAP = "coinmarketcap"
    TRADINGVIEW = "tradingview"
    YAHOO_FINANCE = "yahoo_finance"
    GOOGLE_NEWS = "google_news"


class ContentStyle(str, enum.Enum):
    EDUCATIONAL = "educational"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    STORYTELLING = "storytelling"
    NEWS_REPORTER = "news_reporter"
    MOTIVATIONAL = "motivational"
    FUNNY = "funny"


class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    THUMBNAIL = "thumbnail"
    SUBTITLE = "subtitle"
    MUSIC = "music"
    FONT = "font"
    TEMPLATE = "template"


class NotificationType(str, enum.Enum):
    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


# ============================================
# MIXINS
# ============================================
class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


# ============================================
# USER MODELS
# ============================================
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_onboarded = Column(Boolean, default=False)
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    metadata = Column(JSON, default={})
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    channels = relationship("Channel", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),)

    user = relationship("User", back_populates="oauth_accounts")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="refresh_tokens")


class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False)
    key_prefix = Column(String(10), nullable=False)
    permissions = Column(JSON, default=[])
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="api_keys")


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    preferences = Column(JSON, default={})
    notification_settings = Column(JSON, default={})
    content_preferences = Column(JSON, default={})

    user = relationship("User", back_populates="settings")


# ============================================
# CHANNEL MODELS
# ============================================
class Channel(Base, TimestampMixin):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    platform = Column(String(50), default="youtube")
    youtube_channel_id = Column(String(100), nullable=True)
    youtube_handle = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    subscriber_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    metadata = Column(JSON, default={})

    owner = relationship("User", back_populates="channels")
    videos = relationship("Video", back_populates="channel", cascade="all, delete-orphan")
    playlists = relationship("ChannelPlaylist", back_populates="channel", cascade="all, delete-orphan")
    analytics = relationship("ChannelAnalytics", back_populates="channel", cascade="all, delete-orphan")


class ChannelPlaylist(Base, TimestampMixin):
    __tablename__ = "channel_playlists"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    youtube_playlist_id = Column(String(100), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=True)

    channel = relationship("Channel", back_populates="playlists")


# ============================================
# TREND MODELS
# ============================================
class TrendSource(Base, TimestampMixin):
    __tablename__ = "trend_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(Enum(TrendSourceType), nullable=False)
    api_endpoint = Column(String(500), nullable=True)
    api_key = Column(String(255), nullable=True)
    enabled = Column(Boolean, default=True)
    fetch_interval_minutes = Column(Integer, default=60)
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    config = Column(JSON, default={})

    topics = relationship("TrendingTopic", back_populates="source")


class TrendingTopic(Base, TimestampMixin):
    __tablename__ = "trending_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    topic_type = Column(String(100), default="general")
    source_id = Column(Integer, ForeignKey("trend_sources.id", ondelete="SET NULL"), nullable=True)
    source_name = Column(String(100), nullable=True)
    source_url = Column(String(500), nullable=True)
    score = Column(Integer, default=0)
    search_volume = Column(Integer, default=0)
    engagement_rate = Column(DECIMAL(5, 2), default=0)
    competition_level = Column(DECIMAL(5, 2), default=0)
    growth_rate = Column(DECIMAL(5, 2), default=0)
    virality_score = Column(DECIMAL(5, 2), default=0)
    metadata = Column(JSON, default={})
    is_processed = Column(Boolean, default=False)
    discovered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    source = relationship("TrendSource", back_populates="topics")
    research = relationship("Research", back_populates="topic", uselist=False, cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="topic", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="topic")

    __table_args__ = (
        Index("idx_trending_topics_score", "score"),
        Index("idx_trending_topics_discovered", "discovered_at"),
    )


# ============================================
# RESEARCH MODELS
# ============================================
class Research(Base, TimestampMixin):
    __tablename__ = "research"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("trending_topics.id", ondelete="CASCADE"), nullable=False)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, default=[])
    statistics = Column(JSON, default=[])
    citations = Column(JSON, default=[])
    sources = Column(JSON, default=[])
    confidence_score = Column(Integer, default=0)
    misinformation_flags = Column(JSON, default=[])
    is_fact_checked = Column(Boolean, default=False)
    fact_check_summary = Column(Text, nullable=True)

    topic = relationship("TrendingTopic", back_populates="research", uselist=False)
    scripts = relationship("Script", back_populates="research")


# ============================================
# SCRIPT MODELS
# ============================================
class Script(Base, TimestampMixin):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("trending_topics.id", ondelete="CASCADE"), nullable=False)
    research_id = Column(Integer, ForeignKey("research.id", ondelete="SET NULL"), nullable=True)
    style = Column(Enum(ContentStyle), default=ContentStyle.EDUCATIONAL, nullable=False)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    hook = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    call_to_action = Column(Text, nullable=True)
    estimated_duration_seconds = Column(Integer, default=600)
    word_count = Column(Integer, default=0)
    reading_ease_score = Column(DECIMAL(5, 2), nullable=True)
    seo_score = Column(DECIMAL(5, 2), nullable=True)
    is_optimized = Column(Boolean, default=False)
    version = Column(Integer, default=1)

    topic = relationship("TrendingTopic", back_populates="scripts")
    research = relationship("Research", back_populates="scripts")


# ============================================
# VOICE MODELS
# ============================================
class Voice(Base, TimestampMixin):
    __tablename__ = "voices"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(100), nullable=False)
    voice_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    language = Column(String(50), default="en")
    gender = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False)
    settings = Column(JSON, default={})
    preview_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("provider", "voice_id", name="uq_voice_provider_id"),)


# ============================================
# ASSET MODELS
# ============================================
class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    storage_key = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(DECIMAL(10, 2), nullable=True)
    provider = Column(String(100), default="s3")
    bucket = Column(String(255), nullable=True)
    region = Column(String(100), nullable=True)
    url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    is_public = Column(Boolean, default=False)

    user = relationship("User", back_populates="assets")


# ============================================
# VIDEO MODELS
# ============================================
class Video(Base, TimestampMixin):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(Integer, ForeignKey("trending_topics.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.DRAFT, nullable=False)
    youtube_video_id = Column(String(100), nullable=True)
    youtube_url = Column(String(500), nullable=True)
    duration_seconds = Column(Integer, default=0)
    resolution = Column(String(20), default="1080p")
    file_size_bytes = Column(Integer, nullable=True)
    storage_key = Column(String(500), nullable=True)
    privacy_status = Column(String(20), default="unlisted")
    made_for_kids = Column(Boolean, default=False)
    category_id = Column(Integer, nullable=True)
    language = Column(String(10), default="en")
    is_short = Column(Boolean, default=False)
    metadata = Column(JSON, default={})
    published_at = Column(DateTime(timezone=True), nullable=True)

    channel = relationship("Channel", back_populates="videos")
    topic = relationship("TrendingTopic", back_populates="videos")
    thumbnails = relationship("Thumbnail", back_populates="video", cascade="all, delete-orphan")
    seo = relationship("SEOMetadata", back_populates="video", uselist=False, cascade="all, delete-orphan")
    subtitles = relationship("Subtitle", back_populates="video", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="video", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")


class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    storage_key = Column(String(500), nullable=False)
    url = Column(String(500), nullable=True)
    width = Column(Integer, default=1280)
    height = Column(Integer, default=720)
    ctr_score = Column(DECIMAL(5, 2), default=0)
    is_selected = Column(Boolean, default=False)
    is_a_b_test = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    video = relationship("Video", back_populates="thumbnails")


class SEOMetadata(Base, TimestampMixin):
    __tablename__ = "seo_metadata"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    hashtags = Column(JSON, default=[])
    chapters = Column(JSON, default=[])
    pinned_comment = Column(Text, nullable=True)
    community_post = Column(Text, nullable=True)
    seo_score = Column(DECIMAL(5, 2), default=0)
    keyword_density = Column(JSON, default={})
    suggestions = Column(JSON, default=[])
    is_optimized = Column(Boolean, default=False)

    video = relationship("Video", back_populates="seo", uselist=False)


class Subtitle(Base):
    __tablename__ = "subtitles"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    language = Column(String(10), default="en")
    content = Column(Text, nullable=False)
    format = Column(String(20), default="srt")
    storage_key = Column(String(500), nullable=True)
    is_auto_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    video = relationship("Video", back_populates="subtitles")


# ============================================
# ANALYTICS MODELS
# ============================================
class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    views = Column(Integer, default=0)
    watch_time_minutes = Column(DECIMAL(10, 2), default=0)
    average_view_duration_seconds = Column(DECIMAL(10, 2), default=0)
    ctr = Column(DECIMAL(5, 2), default=0)
    impressions = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    subscribers_gained = Column(Integer, default=0)
    subscribers_lost = Column(Integer, default=0)
    estimated_revenue_usd = Column(DECIMAL(10, 2), default=0)
    rpm = Column(DECIMAL(5, 2), default=0)
    audience_retention = Column(JSON, default={})
    traffic_sources = Column(JSON, default={})
    top_countries = Column(JSON, default=[])
    top_keywords = Column(JSON, default=[])
    demographics = Column(JSON, default={})
    recorded_at = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("video_id", "recorded_at", name="uq_video_analytics_date"),)

    video = relationship("Video", back_populates="analytics")


class ChannelAnalytics(Base):
    __tablename__ = "channel_analytics"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False)
    total_views = Column(Integer, default=0)
    total_watch_time_minutes = Column(DECIMAL(12, 2), default=0)
    total_subscribers = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)
    estimated_revenue_usd = Column(DECIMAL(12, 2), default=0)
    recorded_at = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("channel_id", "recorded_at", name="uq_channel_analytics_date"),)

    channel = relationship("Channel", back_populates="analytics")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    youtube_comment_id = Column(String(100), nullable=True)
    author_name = Column(String(255), nullable=True)
    author_channel_id = Column(String(100), nullable=True)
    text_content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_replied = Column(Boolean, default=False)
    ai_reply = Column(Text, nullable=True)
    sentiment = Column(String(20), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    video = relationship("Video", back_populates="comments")


# ============================================
# WORKFLOW MODELS
# ============================================
class WorkflowRun(Base, TimestampMixin):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(100), nullable=False)
    topic_id = Column(Integer, ForeignKey("trending_topics.id", ondelete="SET NULL"), nullable=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.QUEUED, nullable=False)
    current_step = Column(String(100), nullable=True)
    progress = Column(DECIMAL(5, 2), default=0)
    result = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    tasks = relationship("Task", back_populates="workflow_run", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="workflow_run", cascade="all, delete-orphan")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.QUEUED, nullable=False)
    priority = Column(Integer, default=0)
    payload = Column(JSON, default={})
    result = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    workflow_run = relationship("WorkflowRun", back_populates="tasks")

    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_priority", "priority"),
    )


# ============================================
# NOTIFICATION MODELS
# ============================================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.IN_APP, nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default={})
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")

    __table_args__ = (Index("idx_notifications_user", "user_id", "is_read"),)


# ============================================
# BILLING MODELS
# ============================================
class BillingPlan(Base, TimestampMixin):
    __tablename__ = "billing_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price_usd = Column(DECIMAL(10, 2), nullable=False, default=0)
    interval = Column(String(20), default="monthly")
    currency = Column(String(3), default="USD")
    features = Column(JSON, default={})
    limits = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    stripe_price_id = Column(String(255), nullable=True)

    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("billing_plans.id", ondelete="RESTRICT"), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    paypal_subscription_id = Column(String(255), nullable=True)
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("BillingPlan", back_populates="subscriptions")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(50), default="pending")
    stripe_invoice_id = Column(String(255), nullable=True)
    paypal_invoice_id = Column(String(255), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percent = Column(DECIMAL(5, 2), default=0)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    max_uses = Column(Integer, default=0)
    current_uses = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ============================================
# AI AGENT MODELS
# ============================================
class PromptTemplate(Base, TimestampMixin):
    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    variables = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(100), nullable=False)
    prompt_template_id = Column(Integer, ForeignKey("prompt_templates.id", ondelete="SET NULL"), nullable=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="SET NULL"), nullable=True)
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(DECIMAL(10, 6), default=0)
    duration_ms = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    status = Column(String(50), default="completed")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workflow_run = relationship("WorkflowRun", back_populates="agent_runs")


# ============================================
# AUDIT & EMBEDDING MODELS
# ============================================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default={})
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=False)
    vector_id = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

