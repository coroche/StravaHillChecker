from pytest import fixture
from pytest_mock import MockerFixture

@fixture(autouse=True)
def mock_SMTP(mocker: MockerFixture):
    mocked_SMTP = mocker.patch('library.smtp.smtplib.SMTP_SSL')
    return mocked_SMTP