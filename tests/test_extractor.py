import pytest

from halluguard.extractor import extract_module_roots, resolve_dependencies


def test_extracts_third_party_roots_only():
    src = "import os\nimport numpy as np\nfrom bs4.element import Tag\nfrom . import local\n"
    assert extract_module_roots(src) == ["bs4", "numpy"]


def test_maps_module_to_package():
    deps = resolve_dependencies("import bs4", {"bs4": "beautifulsoup4"})
    assert [d.package_name for d in deps] == ["beautifulsoup4"]


def test_syntax_error_propagates():
    with pytest.raises(SyntaxError):
        extract_module_roots("import (")
