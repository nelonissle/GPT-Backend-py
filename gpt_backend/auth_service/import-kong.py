import yaml
import requests

# Filepath to your kong.yml
kong_yml_path = r"F:\repos\GPT-Backend-py\gpt_backend\kong\kong.yml"

# Admin API URL
admin_api_url = "http://kong-gateway:8001"

# Load the kong.yml file
with open(kong_yml_path, "r") as file:
    kong_config = yaml.safe_load(file)

# Add services and routes
for service in kong_config.get("services", []):
    # Add the service
    service_response = requests.post(
        f"{admin_api_url}/services",
        data={"name": service["name"], "url": service["url"]}
    )
    print(f"Added service {service['name']}: {service_response.status_code}")

    # Add routes for the service
    for route in service.get("routes", []):
        route_response = requests.post(
            f"{admin_api_url}/services/{service['name']}/routes",
            data={"name": route["name"], "paths[]": route["paths"]}
        )
        print(f"Added route {route['name']} for service {service['name']}: {route_response.status_code}")