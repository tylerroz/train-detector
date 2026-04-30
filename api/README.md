# Description
This directory includes the API configuration necessary to power the dashboard.

Right now, it's setup using a super basic Flask server, which reads from the SQL database backend.

The service itself is configured to run on port 5000. These routes are exposed externally using a reverse-proxy setup with Apache (located `/etc/apache2/sites-available/000-default.conf`).

The API is started automatically by the main detector entrypoint (`python main.py`), which spawns it in a daemon thread alongside the detection loop and the MJPEG video server.

For standalone development of the API only, you can still run it directly from the *top-level* directory: `python -m api.app`. Don't run both at once — port 5000 will collide.