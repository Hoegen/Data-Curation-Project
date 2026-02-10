# Data Curation Final Project App
# Developed by: [Your Name]
# Course: Data Curation
# Academic Year: 2025-2026

import streamlit as st
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
        "Municipalities most endangered by avalanches": """
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
    

    # --- SECTION: MAP ---
    st.markdown("---")
    st.subheader("South Tyrol Hazard Map")
    hazard_type = st.selectbox("Select hazard type:", ["Avalanche", "Landslide", "Either"])
    if st.button("Show Hazard Map"):
        sparql.setQuery(queries[hazard_type])
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            cols = results["head"]["vars"]
            rows = [ [r.get(c, {}).get('value', '') if isinstance(r.get(c), dict) else r.get(c, '') for c in cols] for r in results["results"]["bindings"] ]
            df = pd.DataFrame(rows, columns=cols)
            df["hazardPct"] = pd.to_numeric(df["hazardPct"], errors="coerce")
            df["name_it"] = df["name_it"].fillna("Unknown")

            import geopandas as gpd
            import os
            shape_path = current_dir.parent / "Data" / "Municipalities.csv"
            if os.path.exists(shape_path):
                muni_shapes = pd.read_csv(shape_path)
                if "SHAPE" in muni_shapes.columns:
                    muni_shapes["geometry"] = muni_shapes["SHAPE"].apply(lambda wkt: gpd.GeoSeries.from_wkt([wkt])[0] if pd.notna(wkt) else None)
                    gdf = gpd.GeoDataFrame(muni_shapes, geometry="geometry", crs="EPSG:32632")
                    gdf = gdf.merge(df, left_on="NAME_IT", right_on="name_it", how="left")
                    gdf = gdf.to_crs("EPSG:4326")
                    gdf = gdf[gdf["geometry"].notnull()]

                    import pydeck as pdk
                    gdf["polygon"] = gdf["geometry"].apply(lambda geom: [list(geom.exterior.coords)] if geom is not None and geom.geom_type == "Polygon" else [])
                    gdf["color"] = gdf["hazardPct"].apply(lambda pct: [255, int(255 - pct * 2.5), int(255 - pct * 2.5), 120] if pd.notna(pct) else [200,200,200,80])

                    layer = pdk.Layer(
                        "PolygonLayer",
                        data=gdf,
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
                    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{NAME_IT}: {hazardPct}%" }))
                else:
                    st.warning("Municipalities.csv does not contain SHAPE column.")
            else:
                st.warning("Municipalities.csv not found.")
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