-- Check coordinate ranges for hazard zones
SELECT 
    ST_X(ST_Centroid(SHAPE)) as center_x,
    ST_Y(ST_Centroid(SHAPE)) as center_y,
    ST_SRID(SHAPE) as srid
FROM Hazard_zones 
LIMIT 5;

-- Check coordinate ranges for road segments  
SELECT 
    ST_X(ST_Centroid(geom)) as center_x,
    ST_Y(ST_Centroid(geom)) as center_y,
    ST_SRID(geom) as srid
FROM Road_segments 
LIMIT 5;