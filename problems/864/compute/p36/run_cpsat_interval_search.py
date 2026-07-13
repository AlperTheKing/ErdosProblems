#!/usr/bin/env python3
"""Compatibility runner for the installed OR-Tools LinearExpr.sum API."""

from __future__ import annotations

from ortools.sat.python import cp_model

import cpsat_interval_search


_linear_sum = cp_model.LinearExpr.sum
cp_model.LinearExpr.sum = staticmethod(lambda terms: _linear_sum(list(terms)))


if __name__ == "__main__":
    cpsat_interval_search.main()
