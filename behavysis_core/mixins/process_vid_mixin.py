"""
Utility functions.
"""

from __future__ import annotations

from typing import Union

import cv2
from behavysis_core.data_models.vid_metadata import VidMetadata
from behavysis_core.mixins.subproc_mixin import SubprocMixin


class ProcessVidMixin:
    """__summary__"""

    @staticmethod
    def process_vid(
        in_fp: Union[str, None],
        out_fp: Union[str, None],
        height_px: Union[int, None],
        width_px: Union[int, None],
        fps: Union[int, None],
        start_sec: Union[float, None],
        stop_sec: Union[float, None],
    ) -> str:
        """__summary__"""
        outcome = ""
        # Constructing ffmpeg command
        cmd = ["ffmpeg", "-i", in_fp]

        # RESIZING and TRIMMING
        filters = []
        if width_px or height_px:
            filters.append(f"scale={width_px}:{height_px}")
            outcome += f"Downsampling to {width_px} x {height_px}.\n"
        if start_sec or stop_sec:
            filters.append("setpts=PTS-STARTPTS")
        if filters:
            cmd += ["-vf", ",".join(filters)]

        # CHANGING FPS
        if fps:
            cmd += ["-r", str(fps)]
            outcome += f"Changing fps to {fps}.\n"
        # TRIMMING
        if start_sec:
            cmd += ["-ss", str(start_sec)]
            outcome += f"Trimming video from {start_sec} seconds.\n"
        if stop_sec:
            duration = stop_sec - (start_sec if start_sec else 0)
            cmd += ["-t", str(duration)]
            outcome += f"Trimming video to {stop_sec} seconds.\n"

        # Adding output parameters to ffmpeg command
        cmd += [
            "-c:v",
            "h264",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-y",
            # "-loglevel",
            # "quiet",
            out_fp,
        ]
        # Running ffmpeg command
        # SubprocMixin.run_subproc_fstream(cmd)
        SubprocMixin.run_subproc_console(cmd)
        # Returning outcome
        return outcome

    @staticmethod
    def get_vid_metadata(fp: str) -> VidMetadata:
        """
        Finds the video metadata/parameters for either the raw or formatted video.

        Parameters
        ----------
        fp : str
            The video filepath.

        Returns
        -------
        VidMetadata
            Object containing video metadata.
        """
        configs_meta = VidMetadata()
        cap = cv2.VideoCapture(fp)
        if not cap.isOpened():
            raise ValueError(
                f"The file, {fp}, does not exist or is corrupted. Please check this file."
            )
        configs_meta.height_px = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        configs_meta.width_px = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        configs_meta.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        configs_meta.fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        return configs_meta
        return configs_meta
        return configs_meta
        return configs_meta
