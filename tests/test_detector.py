# -*- coding: utf-8 -*-
"""Tests for detector module"""

import pytest
import numpy as np
from klpd.detector import get_num, confirm_num


class TestConfirmNum:
    """Test confirm_num function"""

    def test_same_valid_numbers(self):
        """Test when both results are the same and valid"""
        result = confirm_num("12가3456", "12가3456", mask=False)
        assert result == "12가3456"

    def test_first_valid_second_invalid(self):
        """Test when first result is valid, second is invalid"""
        result = confirm_num("12가3456", "", mask=False)
        assert result == "12가3456"

    def test_both_invalid(self):
        """Test when both results are invalid"""
        result = confirm_num("", "", mask=False)
        assert result is None

    def test_mask_output(self):
        """Test output mask regex"""
        result = confirm_num("서울12가3456", "서울12가3456", mask=True)
        assert result == "12가3456"


class TestGetNum:
    """Test get_num function"""

    def test_none_image(self):
        """Test with None image"""
        result = get_num(None)
        assert result is None

    def test_empty_image(self):
        """Test with empty array"""
        result = get_num(np.array([]))
        assert result is None
