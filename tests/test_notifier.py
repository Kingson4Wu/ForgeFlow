from unittest.mock import patch

from forgeflow.notifier import send_notification


class TestSendNotification:
    def test_send_notification_does_not_crash(self):
        with patch("forgeflow.notifier.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            send_notification("Title", "Body")
            mock_run.assert_called_once()
