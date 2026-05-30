"""MNE-Python / OpenNeuro data loader interface."""

from __future__ import annotations

from pathlib import Path


class MNEInterface:
    """
    Thin wrapper for loading EEG/LFP data.

    Attempts to import MNE-Python if available; falls back to synthetic data.
    """

    def __init__(self, edf_path: str | Path | None = None) -> None:
        self.edf_path = Path(edf_path) if edf_path else None
        self._mne_available = self._check_mne()

    @staticmethod
    def _check_mne() -> bool:
        try:
            import importlib
            importlib.import_module("mne")
            return True
        except ImportError:
            return False

    def load(self, duration_s: float = 60.0, fs: float = 256.0) -> dict:
        """
        Return dict with keys: signal (list[float]), fs, source, duration_s.

        Uses real EDF file if provided + MNE available; otherwise synthetic.
        """
        if self.edf_path and self.edf_path.exists() and self._mne_available:
            return self._load_mne(duration_s)
        return self._load_synthetic(duration_s, fs)

    def _load_mne(self, duration_s: float) -> dict:
        import mne  # type: ignore[import]
        raw = mne.io.read_raw_edf(str(self.edf_path), preload=True, verbose=False)
        fs = raw.info["sfreq"]
        n = int(duration_s * fs)
        data = raw.get_data()[0, :n].tolist()
        return {"signal": data, "fs": fs, "source": str(self.edf_path), "duration_s": duration_s}

    def _load_synthetic(self, duration_s: float, fs: float) -> dict:
        from .band_filter import synthetic_eeg
        signal = synthetic_eeg(duration_s=duration_s, fs=fs, dominant_band="theta")
        return {"signal": signal, "fs": fs, "source": "synthetic", "duration_s": duration_s}
