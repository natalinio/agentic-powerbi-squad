# Test Execution Report — SalesOverviewFYTD

**Execution Date**: 2026-02-23 15:03:21
**Model**: SalesOverviewFYTD
**Test Plan**: tests_definition.json (v1.0.0)
**Execution Mode**: Automated (Python + ADOMD.NET via pythonnet)

---

## Executive Summary

| Metric | Count |
|---|---:|
| Total Tests | 22 |
| ✅ Passed | 22 |
| ⚠️ Warnings | 0 |
| ❌ Failed | 0 |

**Overall Status**: ✅ ALL TESTS PASSED

---

## Detailed Test Results

### TS01: Base Aggregations - Core KPIs (Priority: CRITICAL)

#### ✅ TS01.T01 — Sales Amount Total Validation
- **Measure**: `Sales Amount`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS01.T02 — Budget Amount Total Validation
- **Measure**: `Budget Amount`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS01.T03 — Adjusted Profit Total Validation
- **Measure**: `Adjusted Profit`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS01.T04 — Transaction Count Validation
- **Measure**: `# Transactions`
- **Status**: ✅ **PASS**
- **Query Time**: 0.00 sec


### TS02: Time Intelligence - FYTD with Dynamic Parameters (Priority: CRITICAL)

#### ✅ TS02.T01 — Sales Amount FYTD - Calendar Year (FY=Jan)
- **Measure**: `Sales Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.02 sec


#### ✅ TS02.T02 — Sales Amount FYTD - Fiscal Year (FY=Jul)
- **Measure**: `Sales Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.02 sec


#### ✅ TS02.T03 — Budget Amount FYTD Consistency
- **Measure**: `Budget Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.05 sec


#### ✅ TS02.T04 — Adjusted Profit FYTD Consistency
- **Measure**: `Adjusted Profit FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.05 sec


### TS03: Derived Calculations - Budget Variance & Percentages (Priority: HIGH)

#### ✅ TS03.T01 — Sales vs Budget Variance Amount
- **Measure**: `Sales vs Budget`
- **Status**: ✅ **PASS**
- **Query Time**: 0.02 sec


#### ✅ TS03.T02 — Sales vs Budget Variance Percentage
- **Measure**: `Sales vs Budget %`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS03.T03 — Budget Status Conditional Logic
- **Measure**: `Budget Status`
- **Status**: ✅ **PASS**
- **Query Time**: 0.02 sec


#### ✅ TS03.T04 — Adjusted Profit Percentage
- **Measure**: `Adjusted Profit %`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS03.T05 — Average Monthly Sales Calculation
- **Measure**: `Average Monthly Sales`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


### TS04: Edge Cases & Error Handling (Priority: HIGH)

#### ✅ TS04.T01 — Zero Division Handling - Adjusted Profit %
- **Measure**: `Adjusted Profit %`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS04.T02 — Zero Division Handling - Sales vs Budget %
- **Measure**: `Sales vs Budget %`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS04.T03 — Empty Filter Context Handling
- **Measure**: `Sales Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


### TS05: Dimensional Filtering & Drill-Down (Priority: MEDIUM)

#### ✅ TS05.T01 — Area Filter Propagation
- **Measure**: `Sales Amount`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS05.T02 — Customer Drill-Down Hierarchy
- **Measure**: `Sales Amount`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS05.T03 — Industry Filter Propagation
- **Measure**: `Sales Amount`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


### TS06: Performance Benchmarks (Priority: MEDIUM)

#### ✅ TS06.T01 — Simple Card Visual Performance
- **Measure**: `Sales Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.01 sec


#### ✅ TS06.T02 — Table Visual Performance (100 rows)
- **Measure**: `Multiple measures`
- **Status**: ✅ **PASS**
- **Query Time**: 0.02 sec


#### ✅ TS06.T03 — Complex FYTD Query Performance
- **Measure**: `Sales Amount FYTD`
- **Status**: ✅ **PASS**
- **Query Time**: 0.08 sec

