-- TrendTube AI - Complete PostgreSQL Schema
-- Production-ready schema with all tables, indexes, enums, and RLS policies

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================
-- ENUM TYPES
-- ============================================
CREATE TYPE user_role AS ENUM ('admin', 'creator', 'member', 'viewer');
CREATE TYPE video_status AS ENUM ('draft', 'researching', 'scripting', 'generating_voice', 'creating_video', 'generating_thumbnail', 'ready_for_review', 'approved', 'publishing', 'published', 'failed', 'archived');
CREATE TYPE workflow_status AS ENUM ('queued', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE task_status AS ENUM ('queued', 'running', 'completed', 'failed', 'retrying');
CREATE TYPE subscription_status AS ENUM ('active', 'past_due', 'canceled', 'expired', 'trialing');
CREATE TYPE billing_interval AS ENUM ('monthly', 'yearly');
CREATE TYPE trend_source_type AS ENUM ('google_trends', 'youtube_trending', 'reddit', 'twitter', 'news_api', 'rss_feed', 'hacker_news', 'product_hunt', 'github_trending', 'coinmarketcap', 'tradingview', 'yahoo_finance', 'google_news');
CREATE TYPE content_style AS ENUM ('educational', 'professional', 'friendly', 'storytelling', 'news_reporter', 'motivational', 'funny');
CREATE TYPE asset_type AS ENUM ('image', 'video', 'audio', 'thumbnail', 'subtitle', 'music', 'font', 'template');
CREATE TYPE notification_type AS ENUM ('email', 'push', 'in_app', 'webhook');
CREATE TYPE ai_provider AS ENUM ('openai', 'anthropic', 'google', 'azure', 'elevenlabs', 'replicate', 'stability', 'deepgram');

-- ============================================
-- USERS & AUTH
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'member',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_onboarded BOOLEAN DEFAULT FALSE,
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    metadata JSONB DEFAULT '{}'::jsonb,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS oauth_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    access_token TEXT,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider, provider_user_id)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    key_prefix VARCHAR(10) NOT NULL,
    permissions JSONB DEFAULT '[]'::jsonb,
    last_used_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CHANNELS
-- ============================================
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50) DEFAULT 'youtube',
    youtube_channel_id VARCHAR(100),
    youtube_handle VARCHAR(100),
    avatar_url VARCHAR(500),
    banner_url VARCHAR(500),
    subscriber_count INTEGER DEFAULT 0,
    video_count INTEGER DEFAULT 0,
    view_count BIGINT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    settings JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS channel_playlists (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    youtube_playlist_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TREND DISCOVERY
-- ============================================
CREATE TABLE IF NOT EXISTS trend_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_type trend_source_type NOT NULL,
    api_endpoint VARCHAR(500),
    api_key VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    fetch_interval_minutes INTEGER DEFAULT 60,
    last_fetched_at TIMESTAMP WITH TIME ZONE,
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    topic_type VARCHAR(100) DEFAULT 'general',
    source_id INTEGER REFERENCES trend_sources(id) ON DELETE SET NULL,
    source_name VARCHAR(100),
    source_url VARCHAR(500),
    score INTEGER DEFAULT 0,
    search_volume INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2) DEFAULT 0,
    competition_level DECIMAL(5,2) DEFAULT 0,
    growth_rate DECIMAL(5,2) DEFAULT 0,
    virality_score DECIMAL(5,2) DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_processed BOOLEAN DEFAULT FALSE,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_trending_topics_score ON trending_topics(score DESC);
CREATE INDEX idx_trending_topics_type ON trending_topics(topic_type);
CREATE INDEX idx_trending_topics_discovered ON trending_topics(discovered_at DESC);
CREATE INDEX idx_trending_topics_title_trgm ON trending_topics USING gin (title gin_trgm_ops);

-- ============================================
-- RESEARCH
-- ============================================
CREATE TABLE IF NOT EXISTS research (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES trending_topics(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    key_points JSONB DEFAULT '[]'::jsonb,
    statistics JSONB DEFAULT '[]'::jsonb,
    citations JSONB DEFAULT '[]'::jsonb,
    sources JSONB DEFAULT '[]'::jsonb,
    confidence_score INTEGER DEFAULT 0 CHECK (confidence_score >= 0 AND confidence_score <= 100),
    misinformation_flags JSONB DEFAULT '[]'::jsonb,
    is_fact_checked BOOLEAN DEFAULT FALSE,
    fact_check_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SCRIPTS
-- ============================================
CREATE TABLE IF NOT EXISTS scripts (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES trending_topics(id) ON DELETE CASCADE,
    research_id INTEGER REFERENCES research(id) ON DELETE SET NULL,
    style content_style DEFAULT 'educational',
    title VARCHAR(500),
    content TEXT NOT NULL,
    hook TEXT,
    body TEXT,
    call_to_action TEXT,
    estimated_duration_seconds INTEGER DEFAULT 600,
    word_count INTEGER DEFAULT 0,
    reading_ease_score DECIMAL(5,2),
    seo_score DECIMAL(5,2),
    is_optimized BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- VOICES
-- ============================================
CREATE TABLE IF NOT EXISTS voices (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(100) NOT NULL,
    voice_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    language VARCHAR(50) DEFAULT 'en',
    gender VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    settings JSONB DEFAULT '{}'::jsonb,
    preview_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider, voice_id)
);

-- ============================================
-- ASSETS (Media)
-- ============================================
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    asset_type asset_type NOT NULL,
    storage_key VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500),
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    width INTEGER,
    height INTEGER,
    duration_seconds DECIMAL(10,2),
    provider VARCHAR(100) DEFAULT 's3',
    bucket VARCHAR(255),
    region VARCHAR(100),
    url TEXT,
    thumbnail_url TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- VIDEOS
-- ============================================
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    script_id INTEGER REFERENCES scripts(id) ON DELETE SET NULL,
    topic_id INTEGER REFERENCES trending_topics(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status video_status DEFAULT 'draft',
    youtube_video_id VARCHAR(100),
    youtube_url VARCHAR(500),
    duration_seconds INTEGER DEFAULT 0,
    resolution VARCHAR(20) DEFAULT '1080p',
    file_size_bytes BIGINT,
    storage_key VARCHAR(500),
    privacy_status VARCHAR(20) DEFAULT 'unlisted',
    made_for_kids BOOLEAN DEFAULT FALSE,
    category_id INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    is_short BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- THUMBNAILS
-- ============================================
CREATE TABLE IF NOT EXISTS thumbnails (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    storage_key VARCHAR(500) NOT NULL,
    url VARCHAR(500),
    width INTEGER DEFAULT 1280,
    height INTEGER DEFAULT 720,
    ctr_score DECIMAL(5,2) DEFAULT 0,
    is_selected BOOLEAN DEFAULT FALSE,
    is_a_b_test BOOLEAN DEFAULT FALSE,
    generation_prompt TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SEO
-- ============================================
CREATE TABLE IF NOT EXISTS seo_metadata (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    tags TEXT[] DEFAULT '{}',
    hashtags TEXT[] DEFAULT '{}',
    chapters JSONB DEFAULT '[]'::jsonb,
    pinned_comment TEXT,
    community_post TEXT,
    seo_score DECIMAL(5,2) DEFAULT 0,
    keyword_density JSONB DEFAULT '{}'::jsonb,
    suggestions JSONB DEFAULT '[]'::jsonb,
    is_optimized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SUBTITLES / CAPTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS subtitles (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'en',
    content TEXT NOT NULL,
    format VARCHAR(20) DEFAULT 'srt',
    storage_key VARCHAR(500),
    is_auto_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- ANALYTICS
-- ============================================
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    watch_time_minutes DECIMAL(10,2) DEFAULT 0,
    average_view_duration_seconds DECIMAL(10,2) DEFAULT 0,
    ctr DECIMAL(5,2) DEFAULT 0,
    impressions INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    subscribers_gained INTEGER DEFAULT 0,
    subscribers_lost INTEGER DEFAULT 0,
    estimated_revenue_usd DECIMAL(10,2) DEFAULT 0,
    rpm DECIMAL(5,2) DEFAULT 0,
    audience_retention JSONB DEFAULT '{}'::jsonb,
    traffic_sources JSONB DEFAULT '{}'::jsonb,
    top_countries JSONB DEFAULT '[]'::jsonb,
    top_keywords JSONB DEFAULT '[]'::jsonb,
    demographics JSONB DEFAULT '{}'::jsonb,
    recorded_at DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_id, recorded_at)
);

CREATE TABLE IF NOT EXISTS channel_analytics (
    id SERIAL PRIMARY KEY,
    channel_id INTEGER NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    total_views BIGINT DEFAULT 0,
    total_watch_time_minutes DECIMAL(12,2) DEFAULT 0,
    total_subscribers INTEGER DEFAULT 0,
    total_videos INTEGER DEFAULT 0,
    estimated_revenue_usd DECIMAL(12,2) DEFAULT 0,
    recorded_at DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(channel_id, recorded_at)
);

-- ============================================
-- COMMENTS (AI-Managed)
-- ============================================
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    youtube_comment_id VARCHAR(100),
    author_name VARCHAR(255),
    author_channel_id VARCHAR(100),
    text_content TEXT NOT NULL,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_replied BOOLEAN DEFAULT FALSE,
    ai_reply TEXT,
    sentiment VARCHAR(20),
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- WORKFLOWS
-- ============================================
CREATE TABLE IF NOT EXISTS workflow_runs (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    topic_id INTEGER REFERENCES trending_topics(id) ON DELETE SET NULL,
    video_id INTEGER REFERENCES videos(id) ON DELETE SET NULL,
    status workflow_status DEFAULT 'queued',
    current_step VARCHAR(100),
    progress DECIMAL(5,2) DEFAULT 0,
    result JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TASKS (Celery/Background)
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task_type VARCHAR(100) NOT NULL,
    workflow_run_id INTEGER REFERENCES workflow_runs(id) ON DELETE SET NULL,
    status task_status DEFAULT 'queued',
    priority INTEGER DEFAULT 0,
    payload JSONB DEFAULT '{}'::jsonb,
    result JSONB DEFAULT '{}'::jsonb,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_type ON tasks(task_type);
CREATE INDEX idx_tasks_priority ON tasks(priority DESC, created_at ASC);

-- ============================================
-- NOTIFICATIONS
-- ============================================
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type DEFAULT 'in_app',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}'::jsonb,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- ============================================
-- BILLING & SUBSCRIPTIONS
-- ============================================
CREATE TABLE IF NOT EXISTS billing_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price_usd DECIMAL(10,2) NOT NULL DEFAULT 0,
    interval billing_interval DEFAULT 'monthly',
    currency VARCHAR(3) DEFAULT 'USD',
    features JSONB DEFAULT '{}'::jsonb,
    limits JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    stripe_price_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES billing_plans(id) ON DELETE RESTRICT,
    status subscription_status DEFAULT 'active',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    paypal_subscription_id VARCHAR(255),
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) DEFAULT 'pending',
    stripe_invoice_id VARCHAR(255),
    paypal_invoice_id VARCHAR(255),
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    max_uses INTEGER DEFAULT 0,
    current_uses INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- AI AGENTS & PROMPTS
-- ============================================
CREATE TABLE IF NOT EXISTS prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    variables JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(100) NOT NULL,
    prompt_template_id INTEGER REFERENCES prompt_templates(id) ON DELETE SET NULL,
    workflow_run_id INTEGER REFERENCES workflow_runs(id) ON DELETE SET NULL,
    input_data JSONB DEFAULT '{}'::jsonb,
    output_data JSONB DEFAULT '{}'::jsonb,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    model_used VARCHAR(100),
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- AUDIT LOG
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- ============================================
-- SETTINGS
-- ============================================
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB DEFAULT '{}'::jsonb,
    notification_settings JSONB DEFAULT '{}'::jsonb,
    content_preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- VECTOR EMBEDDINGS (ChromaDB mirror)
-- ============================================
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER NOT NULL,
    vector_id VARCHAR(255),
    content TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TRIGGERS & FUNCTIONS
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION current_user_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_user_id', TRUE), '')::INTEGER;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_channels_updated_at
    BEFORE UPDATE ON channels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_trending_topics_updated_at
    BEFORE UPDATE ON trending_topics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_owned_data ON users
    USING (id = current_user_id());

CREATE POLICY channel_owner ON channels
    USING (owner_id = current_user_id());

CREATE POLICY video_channel_owner ON videos
    USING (channel_id IN (SELECT id FROM channels WHERE owner_id = current_user_id()));

-- ============================================
-- SEED DATA
-- ============================================
INSERT INTO trend_sources (name, source_type, enabled, fetch_interval_minutes) VALUES
    ('Google Trends', 'google_trends', TRUE, 30),
    ('YouTube Trending', 'youtube_trending', TRUE, 15),
    ('Reddit', 'reddit', TRUE, 30),
    ('Hacker News', 'hacker_news', TRUE, 60),
    ('Product Hunt', 'product_hunt', TRUE, 60),
    ('GitHub Trending', 'github_trending', TRUE, 60),
    ('Yahoo Finance', 'yahoo_finance', TRUE, 30),
    ('Google News', 'google_news', TRUE, 15)
ON CONFLICT DO NOTHING;

INSERT INTO billing_plans (name, description, price_usd, interval, features, limits, sort_order) VALUES
    ('Free', 'Basic access to explore TrendTube AI', 0, 'monthly',
     '{"videos_per_month": 3, "trend_discovery": true, "basic_analytics": true}',
     '{"max_videos": 3, "max_channels": 1}', 0),
    ('Creator', 'For individual creators and YouTubers', 29, 'monthly',
     '{"videos_per_month": 30, "trend_discovery": true, "research": true, "ai_script": true, "voice_generation": true, "thumbnail_generation": true, "seo_optimization": true, "analytics": true, "priority_support": false}',
     '{"max_videos": 30, "max_channels": 3, "max_voice_minutes": 120}', 1),
    ('Pro', 'For professional content creators and agencies', 99, 'monthly',
     '{"videos_per_month": 100, "trend_discovery": true, "research": true, "ai_script": true, "voice_generation": true, "thumbnail_generation": true, "video_editing": true, "seo_optimization": true, "analytics": true, "a_b_testing": true, "priority_support": true, "team_members": 5}',
     '{"max_videos": 100, "max_channels": 10, "max_voice_minutes": 500}', 2),
    ('Enterprise', 'For media companies and large teams', 299, 'monthly',
     '{"videos_per_month": -1, "trend_discovery": true, "research": true, "ai_script": true, "voice_generation": true, "video_editing": true, "thumbnail_generation": true, "seo_optimization": true, "analytics": true, "a_b_testing": true, "priority_support": true, "team_members": -1, "api_access": true, "custom_workflows": true, "dedicated_account_manager": true}',
     '{"max_videos": -1, "max_channels": -1, "max_voice_minutes": -1}', 3)
ON CONFLICT DO NOTHING;

INSERT INTO prompt_templates (name, agent_type, content, variables) VALUES
    ('Trend Discovery Default', 'trend_agent',
     'You are the Trend Agent for TrendTube AI. Detect emerging topics with strong virality potential across news, social, and creator ecosystems. Return a concise, factual summary with confidence and recommended hooks.',
     '["source", "timeframe", "category"]'),
    ('Research Default', 'research_agent',
     'You are the Research Agent. Gather reliable information, deduplicate sources, and produce a trusted summary with citations and confidence scores.',
     '["topic", "depth", "sources"]'),
    ('Script Writer Default', 'script_writer_agent',
     'You are the Script Writer Agent. Create a polished YouTube script with a strong hook, compelling narrative, examples, statistics, and a CTA, tailored to the selected style.',
     '["topic", "style", "duration", "tone"]')
ON CONFLICT DO NOTHING;
