# Description
This directory includes the API configuration necessary to power the dashboard.

Right now, it's setup using a super basic Flask server, which reads from the SQL database backend.

The service itself is configured to run on port 5000. These routes are exposed externally using a reverse-proxy setup with Apache (located `/etc/apache2/sites-available/000-default.conf`).

To start this API server, run from the *top-level* directory: `python -m api.app`.