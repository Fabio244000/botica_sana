from PySide6.QtCore import QObject, QTimer, Signal

from core.services.alert_service import AlertService


class AlertWorker(QObject):
    alerts_ready = Signal(dict)

    def __init__(self, svc: AlertService, interval_ms=60_000):
        super().__init__()
        self._svc = svc
        QTimer.singleShot(0, self._check)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check)
        self._timer.start(interval_ms)

    def _check(self):
        data = self._svc.alertas()
        if any(data.values()):
            self.alerts_ready.emit(data)
