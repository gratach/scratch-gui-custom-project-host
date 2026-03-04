#!/usr/bin/env python3
import json
import os
import sys
import re
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def load_json_file(path):
    """Load a JSON file and return it as dict."""
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def merge_dicts(base, override):
    """
    Recursively merge override into base.
    Values in override take priority.
    """
    for key, value in override.items():
        if (
            key in base
            and isinstance(base[key], dict)
            and isinstance(value, dict)
        ):
            merge_dicts(base[key], value)
        else:
            base[key] = value


def validate_host(host, port, name):
    """
    Validate that host matches:
    http://localhost:<port>/<path>
    Returns extracted path.
    """

    pattern = rf"^http://localhost:{port}/(.+)$"

    match = re.match(pattern, host)

    if not match:
        print(
            f"Error: {name} has invalid format.\n"
            f"Expected: http://localhost:{port}/<path>\n"
            f"Got: {host}"
        )
        sys.exit(1)

    return match.group(1).strip("/")


# ---------------------------------------------------------
# Custom HTTP Handler
# ---------------------------------------------------------

class BuildRequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.project_prefix = kwargs.pop("project_prefix")
        self.asset_prefix = kwargs.pop("asset_prefix")
        self.script_dir = kwargs.pop("script_dir")

        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """
        Translate URL path to filesystem path.
        Handles rewrites for project and asset routes.
        """

        parsed = urlparse(path)
        clean_path = parsed.path.lstrip("/")

        # Project redirect
        if clean_path.startswith(self.project_prefix + "/"):
            rest = clean_path[len(self.project_prefix) + 1 :]
            return os.path.join(
                self.script_dir,
                "data",
                "projects",
                rest
            )

        # Asset redirect
        if clean_path.startswith(self.asset_prefix + "/"):
            rest = clean_path[len(self.asset_prefix) + 1 :]
            return os.path.join(
                self.script_dir,
                "data",
                "assets",
                rest
            )

        # Default: serve from build directory
        return os.path.join(
            self.script_dir,
            "build",
            clean_path
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # File paths
    default_settings_path = os.path.join(
        script_dir, "default_settings.json"
    )

    settings_path = os.path.join(
        script_dir, "settings.json"
    )

    # Load configs
    default_settings = load_json_file(default_settings_path)
    settings = {}

    if os.path.exists(settings_path):
        settings = load_json_file(settings_path)

    # Merge settings
    merge_dicts(default_settings, settings)

    config = default_settings

    # Required variables
    try:
        serve_build_port = int(config["serve_build_port"])
        project_host = config["project_host"]
        asset_host = config["asset_host"]
    except KeyError as e:
        print(f"Error: Missing config value: {e}")
        sys.exit(1)
    except ValueError:
        print("Error: serve_build_port must be an integer")
        sys.exit(1)

    # Validate hosts
    project_prefix = validate_host(
        project_host,
        serve_build_port,
        "project_host"
    )

    asset_prefix = validate_host(
        asset_host,
        serve_build_port,
        "asset_host"
    )

    # Check build directory
    build_dir = os.path.join(script_dir, "build")

    if not os.path.isdir(build_dir):
        print(f"Error: build directory not found: {build_dir}")
        sys.exit(1)

    # Change working directory to script dir
    os.chdir(script_dir)

    # Create handler
    def handler_factory(*args, **kwargs):
        return BuildRequestHandler(
            *args,
            project_prefix=project_prefix,
            asset_prefix=asset_prefix,
            script_dir=script_dir,
            **kwargs
        )

    # Start server
    server_address = ("localhost", serve_build_port)

    httpd = HTTPServer(server_address, handler_factory)

    print("=======================================")
    print("Serve Build Server started")
    print(f"Port: {serve_build_port}")
    print(f"Build dir: {build_dir}")
    print(f"Project prefix: /{project_prefix}/")
    print(f"Asset prefix: /{asset_prefix}/")
    print("=======================================")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()