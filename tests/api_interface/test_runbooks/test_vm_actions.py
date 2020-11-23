import pytest
import uuid

from calm.dsl.cli.main import get_api_client
from calm.dsl.cli.constants import RUNLOG
from tests.api_interface.test_runbooks.test_files.vm_actions import (
    AHVPowerOnAction,
    AHVPowerOffAction,
    VMwarePowerOnAction,
    VMwarePowerOffAction,
)
from utils import upload_runbook, poll_runlog_status


class TestVMActions:
    @pytest.mark.runbook
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "Runbook, warning_msg",
        [
            pytest.param(AHVPowerOffAction, "VM is not in powered ON State"),
            # pytest.param(VMwarePowerOffAction, "VM is not in powered ON State"),
        ],
    )
    def test_power_off_action(self, Runbook, warning_msg):
        """
        Test power off action on vm endpoints
        """

        client = get_api_client()
        rb_name = "test_vm_action_" + str(uuid.uuid4())[-10:]

        rb = upload_runbook(client, rb_name, Runbook)
        rb_state = rb["status"]["state"]
        rb_uuid = rb["metadata"]["uuid"]
        print(">> Runbook state: {}".format(rb_state))
        assert rb_state == "ACTIVE"
        assert rb_name == rb["spec"]["name"]
        assert rb_name == rb["metadata"]["name"]

        # endpoints generated by this runbook
        endpoint_list = rb["spec"]["resources"].get("endpoint_definition_list", [])

        # running the runbook
        print("\n>>Running the runbook")

        res, err = client.runbook.run(rb_uuid, {})
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        response = res.json()
        runlog_uuid = response["status"]["runlog_uuid"]

        # polling till runbook run gets to terminal state
        state, reasons = poll_runlog_status(
            client, runlog_uuid, RUNLOG.TERMINAL_STATES, maxWait=480
        )

        print(">> Runbook Run state: {}\n{}".format(state, reasons))
        assert state == RUNLOG.STATUS.ERROR

        res, err = client.runbook.list_runlogs(runlog_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))
        response = res.json()
        entities = response["entities"]
        for entity in entities:
            if (
                entity["status"]["type"] == "task_runlog"
                and entity["status"]["task_reference"]["name"] == "ShellTask"
                and runlog_uuid in entity["status"].get("machine_name", "")
            ):
                reasons = ""
                for reason in entity["status"]["reason_list"]:
                    reasons += reason
                assert warning_msg in reasons
                assert entity["status"]["state"] == RUNLOG.STATUS.ERROR
            elif entity["status"]["type"] == "task_runlog" and runlog_uuid in entity[
                "status"
            ].get("machine_name", ""):
                assert entity["status"]["state"] == RUNLOG.STATUS.SUCCESS

        # delete the runbook
        _, err = client.runbook.delete(rb_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))
        else:
            print("runbook {} deleted".format(rb_name))

        # delete endpoints generated by this test
        for endpoint in endpoint_list:
            _, err = client.endpoint.delete(endpoint["uuid"])
            if err:
                pytest.fail("[{}] - {}".format(err["code"], err["error"]))

    @pytest.mark.now
    @pytest.mark.runbook
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "Runbook", [
            AHVPowerOnAction,
            # VMwarePowerOnAction
        ],
    )
    def test_power_on_action(self, Runbook):
        """
        Test power on and restart actions on vm endpoints
        """

        client = get_api_client()
        rb_name = "test_vm_action_" + str(uuid.uuid4())[-10:]

        rb = upload_runbook(client, rb_name, Runbook)
        rb_state = rb["status"]["state"]
        rb_uuid = rb["metadata"]["uuid"]
        print(">> Runbook state: {}".format(rb_state))
        assert rb_state == "ACTIVE"
        assert rb_name == rb["spec"]["name"]
        assert rb_name == rb["metadata"]["name"]

        # endpoints generated by this runbook
        endpoint_list = rb["spec"]["resources"].get("endpoint_definition_list", [])

        # running the runbook
        print("\n>>Running the runbook")

        res, err = client.runbook.run(rb_uuid, {})
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))

        response = res.json()
        runlog_uuid = response["status"]["runlog_uuid"]

        # polling till runbook run gets to terminal state
        state, reasons = poll_runlog_status(
            client, runlog_uuid, RUNLOG.TERMINAL_STATES, maxWait=480
        )

        print(">> Runbook Run state: {}\n{}".format(state, reasons))
        assert state == RUNLOG.STATUS.SUCCESS

        # delete the runbook
        _, err = client.runbook.delete(rb_uuid)
        if err:
            pytest.fail("[{}] - {}".format(err["code"], err["error"]))
        else:
            print("runbook {} deleted".format(rb_name))

        # delete endpoints generated by this test
        for endpoint in endpoint_list:
            _, err = client.endpoint.delete(endpoint["uuid"])
            if err:
                pytest.fail("[{}] - {}".format(err["code"], err["error"]))
