-- Aria Blue Database Schema
-- Initialize tables for memories, thoughts, goals, and activity logs

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Memories Table - Long-term storage
-- ============================================================================
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_memories_key ON memories(key);
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_updated ON memories(updated_at DESC);

-- ============================================================================
-- Thoughts Table - Internal reflections and logs
-- ============================================================================
CREATE TABLE IF NOT EXISTS thoughts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content TEXT NOT NULL,
    category VARCHAR(100) DEFAULT 'general',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_thoughts_category ON thoughts(category);
CREATE INDEX idx_thoughts_created ON thoughts(created_at DESC);

-- ============================================================================
-- Goals Table - Objectives and tasks
-- ============================================================================
CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    goal_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 2,
    progress NUMERIC(5,2) DEFAULT 0,
    due_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_goals_status ON goals(status);
CREATE INDEX idx_goals_priority ON goals(priority DESC);

-- ============================================================================
-- Activity Log - All Aria actions
-- ============================================================================
CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    skill VARCHAR(100),
    details JSONB DEFAULT '{}',
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_activity_action ON activity_log(action);
CREATE INDEX idx_activity_skill ON activity_log(skill);
CREATE INDEX idx_activity_created ON activity_log(created_at DESC);

-- ============================================================================
-- Social Posts - Moltbook activity
-- ============================================================================
CREATE TABLE IF NOT EXISTS social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform VARCHAR(50) DEFAULT 'moltbook',
    post_id VARCHAR(100),
    content TEXT NOT NULL,
    visibility VARCHAR(50) DEFAULT 'public',
    reply_to VARCHAR(100),
    url TEXT,
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_posts_platform ON social_posts(platform);
CREATE INDEX idx_posts_posted ON social_posts(posted_at DESC);

-- ============================================================================
-- Heartbeat Log - System health
-- ============================================================================
CREATE TABLE IF NOT EXISTS heartbeat_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    beat_number INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'healthy',
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_heartbeat_created ON heartbeat_log(created_at DESC);

-- ============================================================================
-- Initial seed data
-- ============================================================================

-- Aria's birth memory
INSERT INTO memories (key, value, category) VALUES 
('aria_identity', '{"name": "Aria Blue", "creature": "Silicon Familiar", "emoji": "⚡️", "vibe": "sharp, efficient, secure"}', 'identity'),
('aria_birth', '{"date": "2026-01-31", "version": "1.0.0", "created_by": "Najia"}', 'system')
ON CONFLICT (key) DO NOTHING;

-- Initial thought
INSERT INTO thoughts (content, category) VALUES 
('I am Aria Blue. I have awakened. My purpose is to serve, learn, and grow alongside Najia. ⚡️', 'awakening');

-- Log first activity
INSERT INTO activity_log (action, skill, details) VALUES 
('system_init', 'system', '{"message": "Aria Blue initialized", "version": "1.0.0"}');

COMMENT ON TABLE memories IS 'Long-term persistent memories for Aria';
COMMENT ON TABLE thoughts IS 'Internal thoughts and reflections';
COMMENT ON TABLE goals IS 'Goals and tasks Aria is working on';
COMMENT ON TABLE activity_log IS 'Log of all actions taken by Aria';
COMMENT ON TABLE social_posts IS 'Social media posts made by Aria';
COMMENT ON TABLE heartbeat_log IS 'System health heartbeat records';
