## Table Of Contents
- [Getting started with Blueprints](#getting-started-with-blueprints)
- [Commands](#commands)
  * [Compile blueprint file](#compile-blueprint-file)
  * [Creating blueprint](#creating-blueprint)
  * [Describe blueprint](#describe-blueprint)
  * [List Blueprints](#list-blueprints)
  * [Launching the blueprint](#launching-the-blueprint)

## Getting started with Blueprints
You can create your first blueprint by running the command `calm init bp`. This will create a folder HelloBlueprint with all the necessary files. HelloBlueprint/blueprint.py is the main blueprint DSL file. Please read the comments in the beginning of the file for more details about the blueprint.


## Commands
Use the flag -h or --help with any for the commands to know more about it. For example: calm launch bp -h

### Compile blueprint file
Command converts the python blueprint file to json payload, which is used for server interactions
```
>> calm compile bp --file <blueprint_file_location>
```

### Creating blueprint
Command creates the blueprint on the server using the local blueprint file. Command accepts both a dsl blueprint python file or a json file.
```
>> calm create bp --file <blueprint_file_location> --name <blueprint_name>
```

Example:
```
(venv) ➜  calm-dsl git:(master) ✗ calm create bp -f HelloBlueprint/blueprint.py -n SampleBp                  
[2022-11-29 12:45:31] [INFO] [calm.dsl.cli.bp_commands:244] Blueprint SampleBp created successfully.
{
    "name": "SampleBp",
    "link": "https://<pc_ip>:9440/console/#page/explore/calm/blueprints/41c71bc3-7b90-4c82-846e-e9a60e9701e7",
    "state": "ACTIVE"
}
```

Options:
- Use `-fc/--force` to delete existin blueprint with same name and create new using current file.
- Use `-f/--file` to give the blueprint file path to upload.
- Use `-n/--name` to give the blueprint name.
- Use `-d/----description` to give blueprint description.
- Use `-q/--quiet` to show only blueprint names.

### Describe blueprint
Command used to describe blueprint.
```
>> calm describe bp <bp_name>
```

Example:
```
(venv) ➜  calm-dsl git:(master) ✗ calm describe bp SampleBp
[2022-11-29 13:16:37] [INFO] [calm.dsl.cli.bps:647] SampleBp found 

----Blueprint Summary----

Name: SampleBp (uuid: 41c71bc3-7b90-4c82-846e-e9a60e9701e7)
Description:  Sample blueprint for Hello app using AHV VM
Status: ACTIVE
Owner: admin Project: default
Created: Tue Nov 29 18:15:27 2022 (31 minutes ago)
Application Profiles [1]:
        HelloProfile
        Deployments[1]:
                HelloDeployment
                Substrate:
                        HelloSubstrate
                        Type: AHV_VM
                        Account: NTNX_LOCAL_AZ
        Actions[9]:
                custom_profile_action_1
                create
                start
                restart
                stop
                delete
                soft_delete
                snapshot_delete
                upgrade
Services [1]:
        HelloService
```

Options:
- Use `-o/--out` to get output format from `text/json`.

### List Blueprints
Command lists all blueprints on the server.
```
>> calm get bps
```
Example:
```
(venv) ➜  calm-dsl git:(master) ✗ calm get bps                                  
[2022-11-29 12:58:22] [WARNING] [calm.dsl.cli.bps:88] Displaying 20 out of 179 entities. Please use --limit and --offset option for more results.
+--------------------------------------------------+----------------+-------------------+------------------------------+--------+--------------------------+----------------+--------------------------------------+
|                       NAME                       | BLUEPRINT TYPE | APPLICATION COUNT |           PROJECT            | STATE  |        CREATED ON        |  LAST UPDATED  |                 UUID                 |
+--------------------------------------------------+----------------+-------------------+------------------------------+--------+--------------------------+----------------+--------------------------------------+
|                     SampleBp                     |  Multi VM/Pod  |         0         |           default            | ACTIVE | Tue Nov 29 18:15:27 2022 | 12 minutes ago | 41c71bc3-7b90-4c82-846e-e9a60e9701e7 |
|    test_vmware_soft_delete_actionb58d28c8e9ab    |   Single VM    |         1         |           default            | ACTIVE | Tue Nov 29 11:24:55 2022 |  7 hours ago   | b2e075db-faeb-479b-9418-5de791dd5268 |
|         test_aws_sspclone_win_78e1950a85         |   Single VM    |         0         |           default            | ACTIVE | Tue Nov 29 02:48:28 2022 |  15 hours ago  | fcaae46a-5994-d844-9d7d-8f7b592bd52e |
|             test_variable_b2542d3437             |  Multi VM/Pod  |         0         |           default            | ACTIVE | Sat Nov 26 18:04:30 2022 |   3 days ago   | f9260dfe-4cde-4c1c-93bb-59b9212d10d9 |
|             test_variable_3ff2453545             |  Multi VM/Pod  |         0         |           default            | ACTIVE | Sat Nov 26 17:25:33 2022 |   3 days ago   | bcdad578-770b-4e48-a9dc-d1c988dad014 |
+--------------------------------------------------+----------------+-------------------+------------------------------+--------+--------------------------+----------------+--------------------------------------+
```

Options:
- Use `-n/--name` to search blueprints by given name.
- Use `-o/--out` to get output format from `text/json`.
- Use `-a/--all-items` to get all items, including deleted ones.
- Use `-q/--quiet` to show only blueprint names.
- USe `-f/--filter` to filter blueprints by this string
- Use `-l/--limit` to set number of results to return.
- Use `-s/--offset` to offset results by the specified amount.

### Launching the blueprint
Launches blueprint to create an application on calm server.
```
>> calm launch bp <blueprint_name> --app_name <app_name>
```

Example:
```
(venv) ➜  calm-dsl git:(master) ✗ calm launch bp SampleBp -i
[2022-11-29 14:11:58] [INFO] [calm.dsl.cli.bps:1246] Searching for existing applications with name App-SampleBp-1669731118
[2022-11-29 14:12:00] [INFO] [calm.dsl.cli.bps:1261] No existing application found with name App-SampleBp-1669731118
[2022-11-29 14:12:01] [INFO] [calm.dsl.cli.bps:647] SampleBp found 
[2022-11-29 14:12:02] [INFO] [calm.dsl.cli.bps:1279] Fetching runtime editables in the blueprint
[2022-11-29 14:12:06] [INFO] [calm.dsl.cli.bps:1696] Blueprint SampleBp queued for launch
[2022-11-29 14:12:06] [INFO] [calm.dsl.cli.bps:1711] Polling status of Launch
{'api_version': '3.0',
 'metadata': {'kind': 'blueprint',
              'uuid': '2103f9c4-851a-4753-9981-214173202df0'},
 'status': {'app_name': 'App-SampleBp-1669731118',
            'application_uuid': None,
            'bp_name': 'SampleBp',
            'bp_uuid': '41c71bc3-7b90-4c82-846e-e9a60e9701e7',
            'message_list': [],
            'milestone': None,
            'state': 'running'}}
[2022-11-29 14:12:28] [INFO] [calm.dsl.cli.bps:1738] running
[2022-11-29 14:12:38] [INFO] [calm.dsl.cli.bps:1711] Polling status of Launch
{'api_version': '3.0',
 'metadata': {'kind': 'blueprint',
              'uuid': '2103f9c4-851a-4753-9981-214173202df0'},
 'status': {'app_name': 'App-SampleBp-1669731118',
            'application_uuid': '7e81ca47-2446-4a25-8994-a1e69f0c1441',
            'bp_name': 'SampleBp',
            'bp_uuid': '41c71bc3-7b90-4c82-846e-e9a60e9701e7',
            'message_list': [],
            'milestone': 'Succeeded',
            'state': 'success'}}
Successfully launched. App uuid is: 7e81ca47-2446-4a25-8994-a1e69f0c1441
[2022-11-29 14:12:41] [INFO] [calm.dsl.cli.bps:1726] App url: https://<pc_ip>:9440/console/#page/explore/calm/applications/7e81ca47-2446-4a25-8994-a1e69f0c1441
```

Options:
- Use `-ws/--with_secrets` to preserve secrets while launching the blueprint while patching environment data.
- Use `-e/--environment` to pass environment to be patched with blueprint.
- Use `-a/--app_name` to pass namefor the application.
- Use `-p/--profile_name` to pass name of app profile to be used for blueprint launch.
- Use `-i/--ignore_runtime_variables`to ignore runtime variables and use defaults for runtime data.
- Use `-pi/--poll-interval` to provide polling interval. Value type: INTEGER.
- Use `-w, --watch/--no-watch` to watch scrolling output.
- Use `-l/--launch_params` to pass path for python file containing data for runtime editables.
- Use `-b/--brownfield_deployments` to pass path of Brownfield Deployment file.
