from Tests.testdata import getTestData
from data import config
from library import googleSheetsAPI
from datetime import datetime

testData = getTestData()
settings = config.getConfig()

def test_getPeaks():
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)
    peaks = googleSheetsAPI.getPeaks(settings.google_script_ID, service)
    assert peaks
    assert all([isinstance(peak, googleSheetsAPI.Hill) for peak in peaks])
    for peak in peaks:
        for attr, value in peak.__dict__.items():
            if attr not in ['ActivityID']:
                assert value is not None, f"Attribute '{attr}' has no value in {peak}"

def test_markAsDone():
    creds = googleSheetsAPI.login()
    service = googleSheetsAPI.buildService(creds)
    date = datetime(2022, 7, 16)
    r = googleSheetsAPI.markAsDone(settings.google_script_ID, service, [271], date, 7479851397)
    assert r['done']