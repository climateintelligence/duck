import pytest

from pywps import Service
from pywps.tests import (
    assert_response_success,
    client_for
)

from tests.common import (
    HADCRUT4_TAS_NC_ZIP,
    HadCRUT5_TAS_MEAN_NC,
)

from duck.processes.wps_clintai import ClintAI


def assert_wps_success(resp):
    try:
        assert_response_success(resp)
    except AssertionError:
        pytest.fail(resp.get_data(as_text=True))


@pytest.mark.online
def test_wps_clintai_hadcrut4_temperature_anomaly():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"file=@xlink:href={HADCRUT4_TAS_NC_ZIP};dataset_name=HadCRUT4;variable_name=temperature_anomaly"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=crai&datainputs={datainputs}"
    )
    assert_wps_success(resp)


@pytest.mark.online
def test_wps_clintai_hadcrut5_tas_mean():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"file=@xlink:href={HadCRUT5_TAS_MEAN_NC};dataset_name=HadCRUT5"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=crai&datainputs={datainputs}"
    )
    assert_wps_success(resp)
