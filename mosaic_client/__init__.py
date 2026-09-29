"""
This module contains functions for working with the SOAP interfaces provided by E-PIX and gPAS - services
provided as part of the MOSAIC suite by the THS Greifswald.
"""

from mosaic_client import epix, gpas
from mosaic_client.epix import EPIXClient
from mosaic_client.gpas import GPASClient
from mosaic_client.helpers import WSDLClient

__all__ = [
    "EPIXClient",
    "GPASClient",
    "WSDLClient",
    "epix",
    "gpas",
]
