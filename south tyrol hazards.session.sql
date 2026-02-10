SELECT r.ID_ROAD, r.ID_HAZARD
FROM road_hazard_Zone_intersection r
JOIN hazard_zones h ON r.ID_HAZARD = h.FID
WHERE h.CODE_DANGER IN ('1040304', '1040303', '1040302', '1040301');