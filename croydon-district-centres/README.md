# Croydon district centre streets

Work in progress: maps of every road and street inside each designated district centre
in the London Borough of Croydon (Croydon Local Plan 2018 Policies Map boundaries,
OpenStreetMap road geometry). The finished HTML page and full build tools will be added here.

- `data/district_centres.geojson` – the nine District Centre boundaries (WGS84), traced from the
  Policies Map vector drawing and converted from British National Grid with OSTN15.
- `tools/fetch_osm.py` – downloads the OpenStreetMap roads for all centres from the Overpass API.
