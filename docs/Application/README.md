## Getting started with Application
Application is an instance of blueprint through which you can perform actions and monitor your VMs. To know more about blueprints refer: [Getting started with blueprints](#)

Once you have a blueprint file ready, you can create an application out of a compiled blueprint file by running the command `calm create app -f <file>`. This command will create a blueprint and launch the application.

## Commands
Use the flag -h or --help with any for the commands to know more about it. For example: `calm create app -h`

| Commands | Description |
|----------|-------------|
|calm get apps | Lists the apps present. |
|calm create app | Used to create an application. |
|calm describe app |This command is used to describe an app. It will print a summary of the application and the current application state. |
|calm delete app |Deletes an app. |
|calm run action |Run an action on the application. |
|calm start app |Start an application. |
|calm stop app |Stop an application. |
|calm restart app |Restart an application. |
|calm watch app |Display app action runlogs. |
|calm watch action_runlog |Watch app action runlog |
|calm download action_runlog |Download app action runlogs |

## Examples
- [Example 1](#)
