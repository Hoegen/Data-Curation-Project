
-- Create the database
CREATE DATABASE IF NOT EXISTS south_tyrol_hazards;
USE south_tyrol_hazards;

-- 1. Create lookup tables first (for foreign key constraints)
CREATE TABLE IF NOT EXISTS Districts (
    CODE TINYINT UNSIGNED PRIMARY KEY,
    LABEL_IT VARCHAR(100),
    LABEL_DE VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Health_districts (
    HEALTH_DISTRICT TINYINT UNSIGNED PRIMARY KEY,
    HEALTH_REGION TINYINT UNSIGNED
);

CREATE TABLE IF NOT EXISTS Process_types (
    CODE VARCHAR(2) PRIMARY KEY,
    LABEL_IT VARCHAR(20),
    LABEL_DE VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Study_levels (
    CODE VARCHAR(1) PRIMARY KEY,
    LABEL_IT VARCHAR(10),
    LABEL_DE VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS Danger_levels (
    CODE INT UNSIGNED PRIMARY KEY,
    LABEL_IT VARCHAR(50),
    LABEL_DE VARCHAR(50)
);

-- 2. Main entities
CREATE TABLE IF NOT EXISTS Municipalities (
    ISTAT_CODE SMALLINT UNSIGNED PRIMARY KEY,
    BELFIORE_CODE VARCHAR(4) UNIQUE,
    ZIP_CODE SMALLINT UNSIGNED,
    NAME_IT VARCHAR(100),
    NAME_DE VARCHAR(100),
    NAME_LD VARCHAR(100),
    DISTR_CODE TINYINT UNSIGNED,
    AREA DECIMAL(13,3),
    HEALTH_DISTRICT TINYINT UNSIGNED,
    MAP_LABEL VARCHAR(100),
    SHAPE GEOMETRY NOT NULL,
    SPATIAL INDEX(SHAPE),
    FOREIGN KEY (DISTR_CODE) REFERENCES Districts(CODE),
    FOREIGN KEY (HEALTH_DISTRICT) REFERENCES Health_districts(HEALTH_DISTRICT)
);

CREATE TABLE IF NOT EXISTS Hazard_zones (
    FID VARCHAR(50) PRIMARY KEY,
    OBJECTID INT UNSIGNED UNIQUE,
    ISTAT_CODE SMALLINT UNSIGNED,
    CODE_PROCESS VARCHAR(2),
    CODE_STUDY VARCHAR(1),
    CODE_DANGER INT UNSIGNED,
    X_LABEL DECIMAL(9,2),
    Y_LABEL DECIMAL(9,2),
    SHAPE GEOMETRY NOT NULL,
    SPATIAL INDEX(SHAPE),
    FOREIGN KEY (ISTAT_CODE) REFERENCES Municipalities(ISTAT_CODE),
    FOREIGN KEY (CODE_PROCESS) REFERENCES Process_types(CODE),
    FOREIGN KEY (CODE_STUDY) REFERENCES Study_levels(CODE),
    FOREIGN KEY (CODE_DANGER) REFERENCES Danger_levels(CODE)
);

CREATE TABLE IF NOT EXISTS Road_segments (
    FID VARCHAR(50) PRIMARY KEY,
    from_node BIGINT UNSIGNED,
    to_node BIGINT UNSIGNED,
    ref VARCHAR(20),
    bridge BOOLEAN DEFAULT FALSE,
    tunnel BOOLEAN DEFAULT FALSE,
    geom MULTILINESTRING NOT NULL,
    SPATIAL INDEX(geom)
);

-- 3. Junction table for many-to-many relationship
CREATE TABLE IF NOT EXISTS Road_Hazard_Zone_intersection (
    ID_HAZARD VARCHAR(50),
    ID_ROAD VARCHAR(50),
    PRIMARY KEY (ID_HAZARD, ID_ROAD),
    FOREIGN KEY (ID_HAZARD) REFERENCES Hazard_zones(FID),
    FOREIGN KEY (ID_ROAD) REFERENCES Road_segments(FID)
);

-- 4. Separate table for individual osmids
CREATE TABLE IF NOT EXISTS Osmids (
    FID VARCHAR(50),
    osmid INT UNSIGNED,
    PRIMARY KEY (FID, osmid),
    FOREIGN KEY (FID) REFERENCES Road_segments(FID)
);

-- 5. Create triggers
DELIMITER $$

CREATE TRIGGER after_hazard_zone_insert
AFTER INSERT ON Hazard_zones
FOR EACH ROW
BEGIN
    INSERT INTO Road_Hazard_Zone_intersection (ID_HAZARD, ID_ROAD)
    SELECT NEW.FID, r.FID
    FROM Road_segments r
    WHERE ST_Intersects(NEW.SHAPE, r.geom)
    AND NOT EXISTS (
        SELECT 1 FROM Road_Hazard_Zone_intersection 
        WHERE ID_HAZARD = NEW.FID AND ID_ROAD = r.FID
    );
END$$

CREATE TRIGGER after_hazard_zone_update
AFTER UPDATE ON Hazard_zones
FOR EACH ROW
BEGIN
    IF NOT ST_Equals(OLD.SHAPE, NEW.SHAPE) THEN
        DELETE FROM Road_Hazard_Zone_intersection 
        WHERE ID_HAZARD = NEW.FID;
        
        INSERT INTO Road_Hazard_Zone_intersection (ID_HAZARD, ID_ROAD)
        SELECT NEW.FID, r.FID
        FROM Road_segments r
        WHERE ST_Intersects(NEW.SHAPE, r.geom);
    END IF;
END$$

CREATE TRIGGER after_road_segment_insert
AFTER INSERT ON Road_segments
FOR EACH ROW
BEGIN
    INSERT INTO Road_Hazard_Zone_intersection (ID_HAZARD, ID_ROAD)
    SELECT h.FID, NEW.FID
    FROM Hazard_zones h
    WHERE ST_Intersects(h.SHAPE, NEW.geom)
    AND NOT EXISTS (
        SELECT 1 FROM Road_Hazard_Zone_intersection 
        WHERE ID_HAZARD = h.FID AND ID_ROAD = NEW.FID
    );
END$$

CREATE TRIGGER after_road_segment_update
AFTER UPDATE ON Road_segments
FOR EACH ROW
BEGIN
    IF NOT ST_Equals(OLD.geom, NEW.geom) THEN
        DELETE FROM Road_Hazard_Zone_intersection 
        WHERE ID_ROAD = NEW.FID;
        
        INSERT INTO Road_Hazard_Zone_intersection (ID_HAZARD, ID_ROAD)
        SELECT h.FID, NEW.FID
        FROM Hazard_zones h
        WHERE ST_Intersects(h.SHAPE, NEW.geom);
    END IF;
END$$

DELIMITER ;