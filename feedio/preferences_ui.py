"""Preferences editor only writes after successful validation and acceptance."""
from PyQt6 import QtWidgets
from . import settings


class PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('feedIO Preferences')
        values = settings.load()
        layout = QtWidgets.QFormLayout(self)
        self.interval = QtWidgets.QSpinBox()
        self.interval.setRange(1, 1440)
        self.interval.setValue(values.refresh_minutes)
        layout.addRow('Refresh interval (minutes)', self.interval)
        self.notifications = QtWidgets.QCheckBox('Show desktop notifications')
        self.notifications.setChecked(values.notifications)
        layout.addRow(self.notifications)
        self.tray = QtWidgets.QCheckBox('Close window to tray when a tray is available')
        self.tray.setChecked(values.close_to_tray)
        layout.addRow(self.tray)
        self.rate = QtWidgets.QSpinBox()
        self.rate.setRange(80, 400)
        self.rate.setValue(values.speech_rate)
        layout.addRow('Speech rate (words/minute)', self.rate)
        self.voice = QtWidgets.QLineEdit(values.speech_voice)
        self.voice.setPlaceholderText('System default (optional installed voice ID)')
        layout.addRow('Speech voice', self.voice)
        info = QtWidgets.QLabel('Speech requires the optional speech dependency and a native backend. '
            'Pocket and account-based sharing are retired. Articles can be bookmarked locally or opened in your browser.')
        info.setWordWrap(True)
        layout.addRow(info)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Save |
                                           QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def save(self):
        try:
            settings.save(settings.Preferences(self.interval.value(), self.notifications.isChecked(),
                          self.tray.isChecked(), self.rate.value(), self.voice.text().strip()))
        except (ValueError, OSError) as error:
            QtWidgets.QMessageBox.warning(self, 'Cannot save preferences', str(error))
            return
        self.accept()
