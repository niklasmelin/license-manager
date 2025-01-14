============
 Change Log
============

This file keeps track of all notable changes to license-manager-backend

Unreleased
----------

3.0.2 -- 2023-08-14
-------------------
* Added total and used as sortable fields in /features route

3.0.1 -- 2023-08-10
-------------------
* Fixed bug in /license_servers/types route and updated it to use authentication

3.0.0 -- 2023-08-08
-------------------
* Refactored API to use a normalized database.
* New endpoints available:

  - /configurations
  - /license_servers
  - /products
  - /features
  - /jobs
  - /bookings
* Added support for multi-tenancy

2.3.1 -- 2023-04-28
-------------------
* Added endpoint to query available license server types
* Added validators to check license server types in create/update for configs
* Updated Dockerfile to use Poetry 1.4.0

2.3.0 -- 2023-03-06
--------------------
* Bumped version to keep in sync with agent

2.2.22 -- 2023-02-23
--------------------
* Bumped version to keep in sync with agent

2.2.21 -- 2023-02-23
--------------------
* Bumped version to keep in sync with agent

2.2.20 -- 2023-02-07
--------------------
* Fixed issue with async lock by using an async loop to start uvicorn

2.2.19 -- 2023-02-01
--------------------
* Updated the booking create endpoint to fix overbooking issues

2.2.18 -- 2023-01-26
--------------------
* Updated the configuration format to make the limit optional

2.2.17.1 -- 2023-01-26
--------------------
* Bumped to sync with lm-agent version

2.2.17 -- 2023-01-24
--------------------
* Changed return code for configuration create endpoint to 201
* Improved message responses in configuration create and update endpoints
* Added new endpoint to get the version of the API

2.2.16 -- 2022-11-22
--------------------
* Updated license configuration to include a limit of how many features can be booked

2.2.15 -- 2022-10-26
--------------------
* Bump to sync with lm-agent version

2.2.14 -- 2022-10-03
--------------------
* Bump to sync with lm-cli version

2.2.13 -- 2022-09-06
--------------------
* Update configuration edit endpoint to allow the client id field to be updated

2.2.12 -- 2022-09-06
--------------------
* Add cluster_id column to config table to identify which cluster the configuration applies to
* Added new route to fetch all configurations from a specific cluster
* Added new route to fetch license usage with booked information
* Updated the sort logic for license endpoint to enable sorting using all columns

2.2.11 -- 2022-07-11
--------------------
* Added support for multiple domains in auth settings (for keycloak)

2.2.10 -- 2022-06-29
--------------------
* Changed DEPLOY_ENV to a string (to accept arbitrary values)

2.2.7 -- 2022-05-10
-------------------
* Update docker-compose to use postgresql instead of postgres
* Added search and sort to list endpoints.
* Skipped 2.2.6 to sync with agent


2.2.5 -- 2022-04-12
-------------------
* Bump to sync with lm-agent version

2.2.2 -- 2022-02-03
-------------------
* Fixed reconcile query

2.2.1 - 2022-02-03
------------------
* Removed version check endpoint

2.2.0 -- 2022-02-02
-------------------
* Simplified the permissions structure to a view/edit model for each data model

2.1.5 -- 2022-01-13
-------------------
* Refactored the Dockerfile

2.1.4 -- 2022-01-08
-------------------
* Added a detail endpoint for bookings by ID
* Upgraded databases and sqlalchemy versions

2.1.3 - 2021-12-15
------------------
* Removed the "LM2_" prefix from the Settings class

2.1.2 - 2021-12-10
------------------
* Changed the CORS policy to allow origins from everywhere

2.1.1 - 2021-12-07
------------------
* Restored mangum handler

2.1.0 -- 2021-12-06
-------------------
* Added Dockerfiles and docker-compose (for local development)
* Separated ``backend`` code from ``agent`` code into separate sub-projects
* Added ``config`` table and ``config`` endpoints in backend
* Parse job run-time through squeue and corrected time parsing logic
* Added docstrings throughout codebase
* Changed backend structure: the previously app is now mounted as a subapp
* Removed unnecessary unit tests from the backend and refactored some from both backend and agent
* Added security via Armasec
* Removed lambda build and configuration items

1.0.0 -- 2021-06-03
-------------------
* Enhanced logging with more debug information
* Added support for poetry to manage dependencies
* Added support for release to pypicloud
* Added authorization sub-project for security on AWS Lambda
* Vendorized flexlm
* Added support for deployment via terraform to AWS Lambda
* Backend:

  * Added alembic support
  * Added bookings endpoints
  * Added FastAPI app for backend

* Agent:

  * Skip epilog cleanup loop if there are no bookings
  * Moved support functions to cmd_utils
  * Epilog updates token count to account for bookings
  * Added PRODUCT_FEATURE_RX, ENCODING, and TOOL_TIMEOUT to settings
  * Update prolog to only track licenses that match the expected format
  * Added feature flags for "booked" and "product_feature"
  * Extra accounting to add used slurm licenses to the total
  * Added forced reconciliation to the prolog
  * Added slurmctld prolog and epilog entrypoints.
