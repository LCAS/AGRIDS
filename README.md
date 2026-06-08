# AGRIDS

Agricultural Robotics Integrated Data Storage.

AGRIDS is a vineyard data platform for agricultural robotics workflows. It provides a web application for creating, importing, visualising, editing, and exporting vineyard map data, backed by FIWARE Orion and optional robot-data storage through MinIO and Zenoh.

![AGRIDS component flowchart](https://github.com/LCAS/AGRIDS/assets/6209386/35a2fee6-12c0-4017-b69d-ba13e399ace6)

## Documentation

The project wiki is the main user and deployment guide:

| Need | Wiki page |
| --- | --- |
| Install and launch AGRIDS | [Setup Instructions](https://github.com/LCAS/AGRIDS/wiki/Setup-Instructions) |
| Understand the stack | [Architecture and Components](https://github.com/LCAS/AGRIDS/wiki/Architecture-and-Components) |
| Create or import vineyard maps | [Create and Import Map Data](https://github.com/LCAS/AGRIDS/wiki/Web-Application-%E2%80%90-Create-and-Import-Map-Data) |
| Visualise and export data | [Visualise Data](https://github.com/LCAS/AGRIDS/wiki/Web-Application%E2%80%90-Visualise-Data) |
| Query or integrate with Orion | [API](https://github.com/LCAS/AGRIDS/wiki/API) |
| Understand entity types | [Entities and Attributes](https://github.com/LCAS/AGRIDS/wiki/Entities-and-Attributes) |
| Operate or troubleshoot a deployment | [Operations and Troubleshooting](https://github.com/LCAS/AGRIDS/wiki/Operations-and-Troubleshooting) |
| Work with robot images/data | [Robot Data, MinIO, and Zenoh](https://github.com/LCAS/AGRIDS/wiki/Robot-Data-MinIO-Zenoh) |
| Use helper scripts | [Developer Scripts](https://github.com/LCAS/AGRIDS/wiki/Developer-Scripts) |

This README is intentionally concise. Keep detailed workflows, screenshots, import formats, and operational guidance in the wiki so deployment documentation stays in one place.

## What AGRIDS Provides

- Browser-based vineyard map creation and editing.
- CSV, GeoJSON, and MapVit import workflows.
- Storage of vineyard, block, vine-row, vine, infrastructure, and photo entities in FIWARE Orion.
- Map visualisation with selectable operational layers.
- Exports for GeoJSON, Antobot XML, PDF reports, KML, and topological map YAML.
- Optional MinIO and Zenoh integration for robot sensor data such as images.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `flask/` | Flask web application, templates, static files, import/export helpers, and geometry utilities |
| `orion/` | FIWARE service wrapper, Docker Compose configuration, Orion/MongoDB/STH helper scripts |
| `zenoh/minio/` | Optional Zenoh + MinIO configs and robot-data scripts |
| `documents/` | OpenAPI/NGSI-v2 API document |
| `VISTA_API.md` | Legacy API reference retained for compatibility |

## Quick Start

For normal deployment, use the wiki setup guide:

- [Setup Instructions](https://github.com/LCAS/AGRIDS/wiki/Setup-Instructions)

Release/application packages are expected to be launched with Docker Compose:

```bash
docker compose up -d
```

For source-checkout development, start the FIWARE services and Flask app separately:

```bash
cd orion/docker
./services cygnus
```

```bash
cd ../../flask
export FIWARE_ORION_BASE_URL=http://localhost:1026/v2/entities/
python flask_web_server.py
```

Then open:

```text
http://localhost:5000
```

## API and Data Model

AGRIDS stores current vineyard state in FIWARE Orion through the NGSI-v2 entity API. Local deployments usually expose Orion at:

```text
http://localhost:1026/v2/entities
```

See:

- [API](https://github.com/LCAS/AGRIDS/wiki/API)
- [Entities and Attributes](https://github.com/LCAS/AGRIDS/wiki/Entities-and-Attributes)
- [OpenAPI JSON](documents/agrids-fiwire-ngsiv2-openapi.json)

## Videos

- [AGRIDS Demo Video](https://www.youtube.com/watch?v=8N8bEK5EBhI)
- [AGRIDS Presentation](https://www.youtube.com/watch?v=CEKvy9WFA8E)

## Notes for Contributors

- Keep this README focused on repository orientation.
- Add detailed deployment, workflow, and troubleshooting guidance to the [wiki](https://github.com/LCAS/AGRIDS/wiki).
- Check scripts for hard-coded endpoints or credentials before using them in a deployment.
