import json
import os

from calm.dsl.api import get_api_client, get_resource_api
from calm.dsl.providers.base import get_provider


dsl_config_file_location = os.path.expanduser("~/.calm/.local/.tests/config.json")


def add_account_details(config):
    """add account details to config"""

    # Get api client
    client = get_api_client()

    # Add accounts details
    payload = {"length": 250, "filter": "state==VERIFIED;type!=nutanix"}
    res, err = client.account.list(payload)
    if err:
        raise Exception("[{}] - {}".format(err["code"], err["error"]))

    response = res.json()
    a_entities = response.get("entities", None)

    accounts = {}
    for a_entity in a_entities:
        account_type = a_entity["status"]["resources"]["type"].upper()
        account_name = a_entity["status"]["name"]
        account_state = a_entity["status"]["resources"]["state"]
        if account_type not in accounts:
            accounts[account_type] = []

        account_data = {
            "NAME": account_name,
            "UUID": a_entity["metadata"]["uuid"],
        }

        if account_type == "NUTANIX_PC":
            if not (
                account_name == "NTNX_LOCAL_AZ"
                or account_name.startswith("multipc_account")
                or account_state != "VERIFIED"
            ):
                continue
            account_data["SUBNETS"] = []
            account_data["OVERLAY_SUBNETS"] = []
            Obj = get_resource_api("nutanix/v1/subnets", client.connection)
            payload = {"filter": "account_uuid=={}".format(account_data["UUID"])}
            result, er = Obj.list(payload)
            if er:
                pass
            else:
                result = result.json()
                for entity in result["entities"]:
                    cluster_ref = entity["status"].get("cluster_reference", {})
                    if not cluster_ref:
                        if entity["status"]["resources"]["subnet_type"] != "OVERLAY":
                            continue
                        vpc_ref = (
                            entity["status"]
                            .get("resources", {})
                            .get("vpc_reference", {})
                        )
                        vpc_name, err = get_vpc_name(account_data["UUID"], vpc_ref)

                        if err:
                            raise Exception(
                                "[{}] - {}".format(err["code"], err["error"])
                            )

                        account_data["OVERLAY_SUBNETS"].append(
                            {
                                "NAME": entity["status"]["name"],
                                "VPC": vpc_name,
                                "UUID": entity["metadata"]["uuid"],
                            }
                        )
                        continue

                    cluster_name = cluster_ref.get("name", "")

                    account_data["SUBNETS"].append(
                        {
                            "NAME": entity["status"]["name"],
                            "CLUSTER": cluster_name,
                            "UUID": entity["metadata"]["uuid"],
                        }
                    )

            # If it is local nutanix account, assign it to local nutanix ACCOUNT
            if a_entity["status"]["resources"]["data"].get("host_pc", False):
                accounts["NTNX_LOCAL_AZ"] = account_data

        accounts[account_type].append(account_data)

    # fill accounts data
    config["ACCOUNTS"] = accounts


def get_vpc_name(account_uuid, vpc_reference):

    AhvVmProvider = get_provider("AHV_VM")
    AhvObj = AhvVmProvider.get_api_obj()
    vpc_uuid = vpc_reference.get("uuid", "")
    if not vpc_uuid:
        return "", {"code": 404, "error": "VPC UUID is missing"}
    vpc_filter = "(_entity_id_=={})".format(vpc_uuid)
    vpcs = AhvObj.vpcs(
        account_uuid=account_uuid, filter_query=vpc_filter, ignore_failures=True
    )
    if not vpcs:
        return "", {"code": 404, "error": "VPC UUID is missing"}
    vpcs = vpcs.get("entities", [])
    if len(vpcs) == 0:
        return "", {"code": 404, "error": "No VPC found"}
    return vpcs[0]["status"]["name"], ""


def add_directory_service_users(config):

    # Get api client
    client = get_api_client()

    # Add user details
    payload = {"length": 250}
    res, err = client.user.list(payload)
    if err:
        raise Exception("[{}] - {}".format(err["code"], err["error"]))

    # Add user details to config
    ds_users = []

    res = res.json()
    for entity in res["entities"]:
        if entity["status"]["state"] != "COMPLETE":
            continue
        e_resources = entity["status"]["resources"]
        if e_resources.get("user_type", "") == "DIRECTORY_SERVICE":
            ds_users.append(
                {
                    "DISPLAY_NAME": e_resources.get("display_name") or "",
                    "DIRECTORY": e_resources.get("directory_service_user", {})
                    .get("directory_service_reference", {})
                    .get("name", ""),
                    "NAME": e_resources["directory_service_user"].get(
                        "user_principal_name", ""
                    ),
                    "UUID": entity["metadata"]["uuid"],
                }
            )

    config["USERS"] = ds_users


def add_directory_service_user_groups(config):

    # Get api client
    client = get_api_client()

    # Add user details
    payload = {"length": 250}
    res, err = client.group.list(payload)
    if err:
        raise Exception("[{}] - {}".format(err["code"], err["error"]))

    # Add user_group details to config
    ds_groups = []

    res = res.json()
    for entity in res["entities"]:
        if entity["status"]["state"] != "COMPLETE":
            continue
        e_resources = entity["status"]["resources"]
        directory_service_user_group = (
            e_resources.get("directory_service_user_group") or dict()
        )
        distinguished_name = directory_service_user_group.get("distinguished_name")
        directory_service_ref = (
            directory_service_user_group.get("directory_service_reference") or dict()
        )
        directory_service_name = directory_service_ref.get("name", "")
        if directory_service_name and distinguished_name:
            ds_groups.append(
                {
                    "DISPLAY_NAME": e_resources.get("display_name") or "",
                    "DIRECTORY": directory_service_name,
                    "NAME": distinguished_name,
                    "UUID": entity["metadata"]["uuid"],
                }
            )

    config["USER_GROUPS"] = ds_groups


def add_project_details(
    config, config_header="PROJECTS", default_project_name="default"
):

    client = get_api_client()
    config_projects = config.get(config_header, {})

    if not config_projects:
        config[config_header] = {"PROJECT1": {"NAME": default_project_name}}

    for _, project_config in config[config_header].items():
        project_name = project_config["NAME"]

        payload = {
            "length": 200,
            "offset": 0,
            "filter": "name=={}".format(project_name),
        }
        project_name_uuid_map = client.project.get_name_uuid_map(payload)

        if not project_name_uuid_map:
            print("Project {} not found".format(project_name))
            continue

        project_uuid = project_name_uuid_map[project_name]
        project_config["UUID"] = project_uuid

        res, _ = client.project.read(project_uuid)
        project_data = res.json()

        # Attach project accounts here
        project_config["ACCOUNTS"] = {}

        payload = {"length": 250, "offset": 0}
        account_uuid_name_map = client.account.get_uuid_name_map(payload)
        account_uuid_type_map = client.account.get_uuid_type_map(payload)

        for _account in project_data["status"]["resources"].get(
            "account_reference_list", []
        ):
            _account_uuid = _account["uuid"]

            # Some deleted keys may also be present
            if _account_uuid not in account_uuid_type_map:
                continue
            _account_type = account_uuid_type_map[_account_uuid].upper()
            _account_name = account_uuid_name_map[_account_uuid]
            if _account_type not in project_config["ACCOUNTS"]:
                project_config["ACCOUNTS"][_account_type] = []

            project_config["ACCOUNTS"][_account_type].append(
                {"NAME": _account_name, "UUID": _account_uuid}
            )

        # From 3.2, it is envs are required for testing
        project_config["ENVIRONMENTS"] = []
        for _env in project_data["status"]["resources"].get(
            "environment_reference_list", []
        ):
            res, _ = client.environment.read(_env.get("uuid"))
            res = res.json()
            project_config["ENVIRONMENTS"].append(
                {"NAME": res["status"]["name"], "UUID": res["metadata"]["uuid"]}
            )


def add_tunnel_details(config):
    client = get_api_client()

    config_tunnels_dict = config.get("VPC_TUNNELS", {})

    params = {"length": 250, "offset": 0}
    params.update(
        {
            "nested_attributes": [
                "tunnel_name",
                "tunnel_vm_name",
                "app_uuid",
                "app_status",
            ]
        }
    )

    res, err = client.network_group.list(params=params)
    if err:
        raise Exception("[{}] - {}".format(err["code"], err["error"]))

    vpc_ngs = res.json()

    AhvVmProvider = get_provider("AHV_VM")
    AhvObj = AhvVmProvider.get_api_obj()

    for ng in vpc_ngs["entities"]:
        if ng["status"]["resources"]["state"] != "VERIFIED":
            continue  # skip UT created network groups

        tunnel_vpc_uuids = ng["status"]["resources"].get("platform_vpc_uuid_list", [])
        tunnel_vpc_uuid = None
        if len(tunnel_vpc_uuids) > 0:
            tunnel_vpc_uuid = tunnel_vpc_uuids[0]

        if not tunnel_vpc_uuid:
            # No VPC configured in network group
            continue

        account_uuid = (
            ng["status"]["resources"].get("account_reference", {}).get("uuid", None)
        )
        if not account_uuid:
            continue  # skip any test created network groups

        account_res, err = client.account.read(account_uuid)
        if err:
            raise Exception("[{}] - {}".format(err["code"], err["error"]))
        account = account_res.json()

        if account["status"]["name"] != "NTNX_LOCAL_AZ":
            # Skip Tunnels not of Local AZ account
            continue

        vpc_filter = "(_entity_id_=={})".format(tunnel_vpc_uuid)
        vpcs = AhvObj.vpcs(
            account_uuid=account_uuid, filter_query=vpc_filter, ignore_failures=True
        )
        if not vpcs:
            continue  # VPC not found
        vpcs = vpcs.get("entities", [])
        if not vpcs:
            continue
        vpc_name = vpcs[0].get("spec", {}).get("name")
        account_name = account["status"]["name"]

        if not config_tunnels_dict.get(account_name, False):
            config_tunnels_dict[account_name] = {}
        config_tunnels_dict[account_name][vpc_name] = {
            "name": ng["status"]["resources"]["tunnel_name"],
            "uuid": ng["status"]["resources"]["tunnel_reference"]["uuid"],
        }

    config["VPC_TUNNELS"] = config_tunnels_dict


def check_project_exists(project_name="default"):
    client = get_api_client()

    payload = {
        "length": 200,
        "offset": 0,
        "filter": "name=={}".format(project_name),
    }
    project_name_uuid_map = client.project.get_name_uuid_map(payload)

    if not project_name_uuid_map:
        print("Project {} not found".format(project_name))
        return False

    return True


def add_vpc_details(config):
    config["IS_VPC_ENABLED"] = False

    add_project_details(config, "VPC_PROJECTS", "test_vpc_project")

    # UUID gets populated if the project actually exists
    # config_projects = (
    #    config.get("VPC_PROJECTS", {}).get("PROJECT1", {}).get("UUID", None)
    # )
    # if config_projects:
    #    config["IS_VPC_ENABLED"] = True
    project_exists = check_project_exists("test_vpc_project")
    if project_exists:
        config["IS_VPC_ENABLED"] = True

    add_tunnel_details(config)


config = {}
if os.path.exists(dsl_config_file_location):
    f = open(dsl_config_file_location, "r")
    data = f.read()
    if data:
        config = json.loads(data)
    f.close()

add_account_details(config)
add_directory_service_users(config)
add_directory_service_user_groups(config)
add_project_details(config)
add_vpc_details(config)

f = open(dsl_config_file_location, "w")
f.write(json.dumps(config, indent=4))
f.close()
