# -*- coding: utf-8 -*-
"""
HTTP-сессия с retry.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_session = requests.Session()
_retry = Retry(
    total=3, backoff_factor=0.5,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",),
)
_session.mount("https://", HTTPAdapter(max_retries=_retry))
_session.mount("http://", HTTPAdapter(max_retries=_retry))