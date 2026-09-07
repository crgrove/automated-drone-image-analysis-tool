"""FormatHelper.py -- small display-formatting helpers shared by the UI and services."""


class FormatHelper:
    """Static helpers for formatting values for display."""

    @staticmethod
    def format_duration(seconds):
        """Return a short, human-readable string for a duration.

        Args:
            seconds: A duration in seconds. Negative values are treated as 0.

        Returns:
            str: e.g. '45s', '5m 12s', or '1h 23m 45s'.
        """
        total = max(0, int(round(seconds)))
        hours, remainder = divmod(total, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        if minutes > 0:
            return f"{minutes}m {secs}s"
        return f"{secs}s"

    @staticmethod
    def format_megabytes(num_bytes):
        """Return a byte count formatted as megabytes with two decimal places.

        Args:
            num_bytes: A size in bytes. Negative values are treated as 0.
                One megabyte is 1024 * 1024 bytes.

        Returns:
            str: e.g. '31.25' (no unit suffix; callers add the localized unit).
        """
        megabytes = max(0, int(num_bytes)) / (1024 * 1024)
        return f"{megabytes:.2f}"

    # ------------------------------------------------------------------
    # altitude references
    #
    # ADIAT distinguishes three reference planes and never lets two share
    # a label: MSL (mean sea level), ATO (above the takeoff point - the
    # drone's own barometric reading) and AGL (above the terrain beneath
    # the aircraft). ATO and AGL agree exactly over flat ground and
    # diverge with relief, so a mislabelled value survives every bench
    # test and misleads only in the field, over the terrain where a search
    # team is actually working.
    # ------------------------------------------------------------------

    ALTITUDE_REFERENCE_TAKEOFF = 'takeoff'
    ALTITUDE_REFERENCE_TERRAIN = 'terrain'
    ALTITUDE_REFERENCE_MANUAL = 'manual'
    # The third plane. Absent until a display surface needed to label a
    # sea-level value, and its absence was itself a hazard: the label
    # functions below fall back to ATO for anything they do not recognise,
    # so a caller asking for an MSL label silently got 'ATO' - the exact
    # collision the vocabulary exists to prevent. Never returned by
    # ``ImageService.get_altitude_reference``, which classifies what an
    # image's RelativeAltitude tag means; this token is for surfaces that
    # know statically which plane they are labelling.
    ALTITUDE_REFERENCE_MSL = 'msl'

    # Explains the pair wherever both are shown. One string, so the status
    # bar, the HUD and any future surface teach the same distinction - and
    # the operator never has to remember which abbreviation is which.
    ALTITUDE_TOOLTIP = (
        "AGL - height above the ground beneath the aircraft. This is what "
        "image scale and clearance depend on, and what ADIAT uses for GSD "
        "and AOI positions.\n"
        "ATO - height above the takeoff point, as the drone reported it. "
        "Equal to AGL over flat ground, and different by the full terrain "
        "change everywhere else."
    )

    # Metres to feet. One constant, because three different values of it
    # (/3.28084, *0.3048, *30.48) were already in the altitude code.
    METERS_TO_FEET = 3.28084

    @staticmethod
    def format_elevation(meters, distance_unit='m', places=None):
        """Format a terrain elevation in the operator's preferred unit.

        Elevations follow the same ``DistanceUnit`` preference as
        altitudes: showing one in metres beside the other in feet is the
        kind of mismatch that makes an operator distrust both.

        Args:
            meters (float): Elevation in metres, as the DEM reports it.
            distance_unit (str): ``'ft'``/``'Feet'`` or ``'m'``/``'Meters'``.
            places (int, optional): Decimals. Defaults to 0 for feet (a
                tenth of a foot is below DEM accuracy) and 1 for metres.

        Returns:
            str or None: e.g. ``'1006 ft'`` or ``'306.7 m'``; None when
            there is no elevation to show.
        """
        if not isinstance(meters, (int, float)):
            return None
        if FormatHelper.prefers_feet(distance_unit):
            value = float(meters) * FormatHelper.METERS_TO_FEET
            return f"{value:.{0 if places is None else places}f} ft"
        return f"{float(meters):.{1 if places is None else places}f} m"

    @staticmethod
    def prefers_feet(distance_unit) -> bool:
        """Whether a ``DistanceUnit`` value means feet.

        The app carries the preference in two spellings - ``'Feet'`` from
        the settings store and ``'ft'`` from the viewer - so every caller
        that has to branch on it asks here instead of matching one form
        and silently failing on the other.
        """
        return str(distance_unit or '').strip().lower() in ('ft', 'feet')

    @staticmethod
    def altitude_inline(readings):
        """One-line altitude summary for tight UI, e.g. a status bar.

        AGL leads: it is the figure that describes clearance and image
        scale, so it is the one an operator should read first. ATO follows
        as the drone's own reported number. With no AGL available only the
        image's own value is shown, labelled with its real reference plane.

        Args:
            readings: An ``AltitudeReadings`` from
                ``ImageService.get_altitude_readings``.

        Returns:
            str or None: None when the image has no altitude at all.
        """
        if readings is None or not readings.has_value:
            return None
        own = (f"{readings.value} {readings.unit} "
               f"{FormatHelper.altitude_reference_abbreviation(readings.reference)}")
        if readings.has_terrain_agl:
            return f"{readings.terrain_agl} {readings.unit} AGL · {own}"
        return own

    @staticmethod
    def altitude_lines(readings):
        """Altitude lines for an export description, one per reference plane.

        Spelled out because a KML or a printed report is read outside ADIAT,
        with no tooltip and no way to ask what the number means.

        Args:
            readings: An ``AltitudeReadings`` from
                ``ImageService.get_altitude_readings``.

        Returns:
            list[str]: Empty when the image has no altitude at all.
        """
        if readings is None or not readings.has_value:
            return []
        own = (f"Altitude: {readings.value:.1f} {readings.unit} "
               f"{FormatHelper.altitude_reference_phrase(readings.reference)}")
        if not readings.has_terrain_agl:
            return [own]
        # AGL first: a reader outside ADIAT wants clearance over the ground
        # photographed, not height above a launch point they cannot see.
        return [f"Altitude: {readings.terrain_agl:.1f} {readings.unit} "
                f"AGL (above the terrain, from DEM)", own]

    @staticmethod
    def altitude_reference_abbreviation(reference):
        """Return the short label for an altitude reference plane.

        Args:
            reference (str): One of ``ALTITUDE_REFERENCE_*``. Anything
                unrecognised is treated as takeoff-relative, which is what
                an unmarked ``drone-dji:RelativeAltitude`` is.

        Returns:
            str: ``'AGL'``, ``'ATO'`` or ``'MSL'``, for tight UI where a
            phrase will not fit.
        """
        # MSL first: the fall-through below answers 'ATO', so a sea-level
        # value reaching it would be labelled with the wrong plane rather
        # than with no plane.
        if reference == FormatHelper.ALTITUDE_REFERENCE_MSL:
            return 'MSL'
        if reference in (FormatHelper.ALTITUDE_REFERENCE_TERRAIN,
                         FormatHelper.ALTITUDE_REFERENCE_MANUAL):
            return 'AGL'
        return 'ATO'

    @staticmethod
    def altitude_reference_phrase(reference):
        """Return the spelled-out label for an altitude reference plane.

        Exports are read outside ADIAT - in CalTopo, in Google Earth, in a
        printed report handed to a search team - where there is room to say
        which plane the number is measured from and no tooltip to fall back
        on.

        Args:
            reference (str): One of ``ALTITUDE_REFERENCE_*``. Anything
                unrecognised is treated as takeoff-relative.

        Returns:
            str: e.g. ``'ATO (above the takeoff point)'``.
        """
        if reference == FormatHelper.ALTITUDE_REFERENCE_MSL:
            return 'MSL (above mean sea level)'
        if reference == FormatHelper.ALTITUDE_REFERENCE_TERRAIN:
            return 'AGL (above the terrain)'
        if reference == FormatHelper.ALTITUDE_REFERENCE_MANUAL:
            return 'AGL (operator-entered)'
        return 'ATO (above the takeoff point)'
