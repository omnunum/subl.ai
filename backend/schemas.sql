CREATE EXTENSION "uuid-ossp";

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = NOW();
   RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TABLE scripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,

    name VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    
    audio_url TEXT

);

CREATE OR REPLACE TRIGGER update_scripts_updated_at
BEFORE UPDATE ON scripts
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    sort_order INT NOT NULL,

    name VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,

    audio_url TEXT,

    script_id UUID NOT NULL
        REFERENCES scripts(id) 
        ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER update_scripts_updated_at
BEFORE UPDATE ON sections
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE fragments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    sort_order INT NOT NULL,

    content TEXT NOT NULL,
    audio_url TEXT NOT NULL,

    section_id UUID NOT NULL
        REFERENCES sections(id) 
        ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER update_scripts_updated_at
BEFORE UPDATE ON fragments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();