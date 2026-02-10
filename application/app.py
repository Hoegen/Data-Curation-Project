# Data Curation Final Project App
# Developed by: [Your Name]
# Course: Data Curation
# Academic Year: 2025-2026

import streamlit as st
import shapely
import pandas as pd
from PIL import Image
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path

# Pega o caminho do diretório onde o app.py está
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()



# --- HEADER ---
st.title("Data Curation Final Project")
st.markdown("""
**Developed by:** Marco Aurélio Hoegen Martins
**Course:** Data Curation  
**Academic Year:** 2025-2026
""")

# --- SIDEBAR NAVIGATION ---
section = st.sidebar.radio(
    "Go to section:",
    [
        "About / Domain",
        "Ontology & Schema",
        "Application"
    ]
)

# --- SECTION: ABOUT / DOMAIN ---
if section == "About / Domain":
    st.header("Domain of Interest")
    st.markdown("""
    This project integrates datasets related to landslides, avalanches, driveable roads, and municipalities in the province of Bozen/Bolzano. The goal is to enable querying of road segments in vulnerable areas and identify municipalities with the most kilometers of vulnerable zones, using a Virtual Knowledge Graph (VKG) approach with Ontop and SPARQL.
    
    This endpoint could also be used for a map that takes dangerous roads into consideration.
    
    Specific roads or zones can also be queried, as well as districts and other territorial units.
    """)
    
# --- SECTION: ONTOLOGY & SCHEMA ---
elif section == "Ontology & Schema":
    st.header("Ontology & Relational Schema")
    st.markdown("""
    - The ontology is expressed in turtle code and models hazards, municipalities, roads, and their relationships.
    - It is a virtual ontology - there's an underlying relational database.
    """)
    st.subheader("Ontology Diagram")
    st.image(current_dir / "Ontology diagram.png")
    st.info("You can use this as a reference for your custom queries.")
     # --- Downloadable Ontology File ---
    ontology_path = current_dir.parent / "semantic" / "hazards_ontology.ttl"
    if ontology_path.exists():
        with open(ontology_path, "rb") as f:
            st.download_button(
                label="Download Ontology (.ttl)",
                data=f.read(),
                file_name="hazards_ontology.ttl",
                mime="text/turtle"
            )
    else:
        st.warning("Ontology file not found.")
    
    
# --- SECTION: APPLICATION ---
elif section == "Application":
    st.header("SPARQL Query Application")
    st.markdown("""
    Use the buttons below to run example SPARQL queries against the Ontop endpoint. Results will be shown in a table.
    """)
    # --- SPARQL ENDPOINT CONFIG ---
    sparql_endpoint = st.text_input("SPARQL Endpoint URL", "http://localhost:8080/sparql")
    sparql = SPARQLWrapper(sparql_endpoint)

    # --- PREDEFINED QUERIES ---
    queries = {
        "List all municipalities": """
PREFIX : <http://hazard-ontology.org/>
SELECT ?municipality ?name_it ?name_de ?name_ld WHERE {
  ?municipality a :Municipality .
  OPTIONAL { ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it") }
  OPTIONAL { ?municipality :name ?name_de . FILTER(LANG(?name_de) = "de") }
  OPTIONAL { ?municipality :name ?name_ld . FILTER(LANG(?name_ld) = "ld") }
}
        """,
        "Municipalities with most km of vulnerable roads": """
PREFIX : <http://hazard-ontology.org/>
SELECT ?municipality ?name_it
	((ROUND((SUM(DISTINCT ?length) / 1000) * 10) / 10) AS ?totaKm)
	((ROUND((SUM(DISTINCT ?danger_length) / 1000) * 10) / 10) AS ?totalVulnerableKm)
	((ROUND((SUM(DISTINCT ?danger_length) / SUM(DISTINCT ?length)) * 1000) / 10) AS ?vulnerableKmPct)
WHERE {
  ?municipality a :Municipality .
  OPTIONAL { ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it") }
  {
    SELECT DISTINCT ?municipality ?road ?length ?danger_length WHERE {
      ?road a :RoadSegment ;
            :isLocatedInMunicipality ?municipality ;
            :hasLength ?length ;
            :intersectsHazardZone ?zone .
      OPTIONAL {
        ?road :hasLength ?danger_length .
        ?zone :hasDangerLevel ?danger_level .
      	FILTER(?danger_level NOT IN (
          <http://hazard-ontology.org/DangerLevel/1040301>,
          <http://hazard-ontology.org/DangerLevel/1040101>
        ))
      }
    }
  }
}
GROUP BY ?municipality ?name_it
ORDER BY DESC(?vulnerableKmPct)
LIMIT 10
""",
        "Municipalities most endangered by Avalanches": """
PREFIX : <http://hazard-ontology.org/>
SELECT ?municipality ?name_it
       ((ROUND((SUM(DISTINCT ?totalRoadKm) / 1000) * 10) / 10) AS ?totalRoadKmAll)
       ((ROUND((SUM(DISTINCT ?avalancheKm) / 1000) * 10) / 10) AS ?avalanchehazardKm)
	   ((ROUND(((SUM(DISTINCT ?avalancheKm) /SUM(DISTINCT ?totalRoadKm)) * 100) * 10) / 10) AS ?avalanchehazardKmPct)
WHERE {
  ?municipality a :Municipality .
  OPTIONAL { ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it") }
  ?road a :RoadSegment ;
        :isLocatedInMunicipality ?municipality ;
        :hasLength ?totalRoadKm .
  OPTIONAL {
    ?road :intersectsHazardZone ?zone ;
          :hasLength ?avalancheKm .
    ?zone a :AvalancheZone ;
          :hasDangerLevel ?dangerLevel .
    FILTER(?dangerLevel NOT IN (
      <http://hazard-ontology.org/DangerLevel/1040301>
    ))
  }
}
GROUP BY ?municipality ?name_it
ORDER BY DESC(?avalanchehazardKmPct)
        """,
        "Municipalities most endangered by Landslides": """
PREFIX : <http://hazard-ontology.org/>
SELECT ?municipality ?name_it
       ((ROUND((SUM(DISTINCT ?totalRoadKm) / 1000) * 10) / 10) AS ?totalRoadKmAll)
       ((ROUND((SUM(DISTINCT ?landslideKm) / 1000) * 10) / 10) AS ?landslidehazardKm)
	   ((ROUND(((SUM(DISTINCT ?landslideKm) /SUM(DISTINCT ?totalRoadKm)) * 100) * 10) / 10) AS ?landslidehazardKmPct)
WHERE {
  ?municipality a :Municipality .
  OPTIONAL { ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it") }
  ?road a :RoadSegment ;
        :isLocatedInMunicipality ?municipality ;
        :hasLength ?totalRoadKm .
  OPTIONAL {
    ?road :intersectsHazardZone ?zone ;
          :hasLength ?landslideKm .
    ?zone a :LandslideZone ;
          :hasDangerLevel ?dangerLevel .
    FILTER(?dangerLevel NOT IN (
      <http://hazard-ontology.org/DangerLevel/1040101>
    ))
  }
}
GROUP BY ?municipality ?name_it
ORDER BY DESC(?landslidehazardKmPct)
        """
    }
    

    # --- MAP QUERIES ---
    map_queries = {
        "Avalanche": """
PREFIX : <http://hazard-ontology.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT ?municipality
		?hazardPct
		?name_it
		?shape
WHERE{
{
SELECT ?municipality
((ROUND(((SUM(DISTINCT ?avalancheKm) /SUM(DISTINCT ?totalRoadKm)) * 100) * 10) / 10) AS ?hazardPct)

WHERE {
  ?municipality a :Municipality .
  ?road a :RoadSegment ;
        :isLocatedInMunicipality ?municipality ;
        :hasLength ?totalRoadKm .
  OPTIONAL {
    ?road :intersectsHazardZone ?zone ;
          :hasLength ?avalancheKm .
    ?zone a :AvalancheZone ;
          :hasDangerLevel ?dangerLevel .
    FILTER(?dangerLevel NOT IN (
      <http://hazard-ontology.org/DangerLevel/1040301>
    ))
  }
}
GROUP BY ?municipality
ORDER BY DESC(?hazardPct)
}
  ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it")
  ?municipality :hasGeometry ?geom .
  ?geom geo:asWKT ?shape .
}
    """,
    "Landslide": """
PREFIX : <http://hazard-ontology.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT ?municipality
		?hazardPct
		?name_it
		?shape
WHERE{
{
SELECT ?municipality
((ROUND(((SUM(DISTINCT ?landslideKm) /SUM(DISTINCT ?totalRoadKm)) * 100) * 10) / 10) AS ?hazardPct)

WHERE {
  ?municipality a :Municipality .
  ?road a :RoadSegment ;
        :isLocatedInMunicipality ?municipality ;
        :hasLength ?totalRoadKm .
  OPTIONAL {
    ?road :intersectsHazardZone ?zone ;
          :hasLength ?landslideKm .
    ?zone a :LandslideZone ;
          :hasDangerLevel ?dangerLevel .
    FILTER(?dangerLevel NOT IN (
      <http://hazard-ontology.org/DangerLevel/1040101>
    ))
  }
}
GROUP BY ?municipality
ORDER BY DESC(?hazardPct)
}
  ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it")
  ?municipality :hasGeometry ?geom .
  ?geom geo:asWKT ?shape .
}
    """,
    "Either": """
PREFIX : <http://hazard-ontology.org/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
SELECT ?municipality
		?hazardPct
		?name_it
		?shape
WHERE{
{
SELECT ?municipality
((ROUND(((SUM(DISTINCT ?hazardKm) /SUM(DISTINCT ?totalRoadKm)) * 100) * 10) / 10) AS ?hazardPct)

WHERE {
  ?municipality a :Municipality .
  ?road a :RoadSegment ;
        :isLocatedInMunicipality ?municipality ;
        :hasLength ?totalRoadKm .
  OPTIONAL {
    ?road :intersectsHazardZone ?zone ;
          :hasLength ?hazardKm .
    ?zone a :HazardZone ;
          :hasDangerLevel ?dangerLevel .
    FILTER(?dangerLevel NOT IN (
      <http://hazard-ontology.org/DangerLevel/1040101>,
      <http://hazard-ontology.org/DangerLevel/1040301>
    ))
  }
}
GROUP BY ?municipality
ORDER BY DESC(?hazardPct)
}
  ?municipality :name ?name_it . FILTER(LANG(?name_it) = "it")
  ?municipality :hasGeometry ?geom .
  ?geom geo:asWKT ?shape .
}
    """
}

    # --- SECTION: MAP ---
    st.markdown("---")
    st.header("South Tyrol Hazard Map")
    hazard_type = st.selectbox("Select hazard type:", ["Avalanche", "Landslide", "Either"])
    if st.button("Show Hazard Map"):
        sparql.setQuery(map_queries[hazard_type])
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            cols = results["head"]["vars"]
            rows = [ [r.get(c, {}).get('value', '') if isinstance(r.get(c), dict) else r.get(c, '') for c in cols] for r in results["results"]["bindings"] ]
            df = pd.DataFrame(rows, columns=cols)
            df["hazardPct"] = pd.to_numeric(df["hazardPct"], errors="coerce")
            df["name_it"] = df["name_it"].fillna("Unknown")

            import geopandas as gpd
            import pydeck as pdk
            from shapely.ops import transform
            import pyproj
            # Define transformer from UTM 32N to WGS84
            project = pyproj.Transformer.from_crs("epsg:32632", "epsg:4326", always_xy=True).transform
            # Parse WKT shapes from SPARQL results
            def parse_geometry(wkt):
              try:
                  geom = shapely.wkt.loads(wkt)
                  geom_wgs84 = transform(project, geom)
                  if geom_wgs84.geom_type == "Polygon":
                      return [list(geom_wgs84.exterior.coords)]
                  elif geom_wgs84.geom_type == "MultiPolygon":
                      return [list(poly.exterior.coords) for poly in geom_wgs84.geoms]
                  else:
                      return []
              except Exception:
                  return []

            df["polygon"] = df["shape"].apply(parse_geometry)
            df["color"] = df["hazardPct"].apply(lambda pct: [255, int(255 - pct * 2.5), int(255 - pct * 2.5), 120] if pd.notna(pct) else [200,200,200,80])

            layer = pdk.Layer(
                "PolygonLayer",
                data=df,
                get_polygon="polygon",
                get_fill_color="color",
                pickable=True,
                auto_highlight=True,
                opacity=0.6
            )
            view_state = pdk.ViewState(
                latitude=46.6,
                longitude=11.3,
                zoom=8,
                pitch=0
            )
            st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{name_it}: {hazardPct}%" }))
        except Exception as e:
            st.error(f"Map rendering failed: {e}")
            
    # Query directly
    query_name = st.selectbox("Choose a query:", list(queries.keys()))
    if st.button("Run Query"):
        sparql.setQuery(queries[query_name])
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            cols = results["head"]["vars"]
            rows = [ [r.get(c, {}).get('value', '') if isinstance(r.get(c), dict) else r.get(c, '') for c in cols] for r in results["results"]["bindings"] ]
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Query failed: {e}")

    st.markdown("---")
    st.subheader("Custom SPARQL Query (optional)")
    custom_query = st.text_area("Enter your SPARQL query:")
    if st.button("Run Custom Query") and custom_query.strip():
        sparql.setQuery(custom_query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            cols = results["head"]["vars"]
            rows = [ [r.get(c, {}).get('value', '') if isinstance(r.get(c), dict) else r.get(c, '') for c in cols] for r in results["results"]["bindings"] ]
            df = pd.DataFrame(rows, columns=cols)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Query failed: {e}")