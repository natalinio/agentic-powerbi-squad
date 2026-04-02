# TMDL Object Properties Reference

Complete property reference for all TMDL object types. Use this as a lookup when you need to verify which properties are valid on a given object.

## Core Object Types

### column

| Property | Type |
|----------|------|
| `dataType` | dataType |
| `description` | description (`///`) |
| `displayFolder` | string |
| `expression` | DAX expression (calculated columns) |
| `formatString` | string |
| `isAvailableInMdx` | boolean flag |
| `isDataTypeInferred` | boolean flag |
| `isHidden` | boolean flag |
| `isKey` | boolean flag |
| `isNameInferred` | boolean flag |
| `isNullable` | boolean flag |
| `isUnique` | boolean flag |
| `lineageTag` | string (GUID) |
| `sortByColumn` | string (column name) |
| `sourceColumn` | string |
| `summarizeBy` | aggregateFunction |
| `type` | columnType |
| `annotation` | array |
| `extendedProperty` | array |
| `alternateOf` | alternateOf |

### measure

| Property | Type |
|----------|------|
| `expression` | DAX expression (on `=` line or multi-line) |
| `description` | description (`///`) |
| `displayFolder` | string |
| `formatString` | string |
| `formatStringDefinition` | DAX expression block (dynamic format) |
| `isHidden` | boolean flag |
| `isSimpleMeasure` | boolean flag |
| `lineageTag` | string (GUID) |
| `dataCategory` | string |
| `kpi` | kpi object |
| `detailRowsDefinition` | detailRowsDefinition |
| `annotation` | array |
| `extendedProperty` | array |

### table

| Property | Type |
|----------|------|
| `dataCategory` | string (e.g., `Time` for date tables) |
| `description` | description (`///`) |
| `isHidden` | boolean flag |
| `isPrivate` | boolean flag |
| `lineageTag` | string (GUID) |
| `column` | array |
| `measure` | array |
| `hierarchy` | array |
| `partition` | array |
| `calculationGroup` | calculationGroup |
| `refreshPolicy` | refreshPolicy |
| `annotation` | array |
| `extendedProperty` | array |

### relationship

| Property | Type |
|----------|------|
| `fromColumn` | string (`Table.Column`) |
| `toColumn` | string (`Table.Column`) |
| `fromCardinality` | relationshipEndCardinality |
| `toCardinality` | relationshipEndCardinality |
| `crossFilteringBehavior` | crossFilteringBehavior |
| `securityFilteringBehavior` | securityFilteringBehavior |
| `isActive` | boolean flag |
| `relyOnReferentialIntegrity` | boolean |
| `annotation` | array |

### partition

| Property | Type |
|----------|------|
| `mode` | modeType |
| `source` | object (M expression or DAX) |
| `sourceType` | partitionSourceType |
| `queryGroup` | string |
| `annotation` | array |

### hierarchy

| Property | Type |
|----------|------|
| `description` | description (`///`) |
| `displayFolder` | string |
| `isHidden` | boolean flag |
| `level` | array |
| `lineageTag` | string (GUID) |
| `annotation` | array |

### level (child of hierarchy)

| Property | Type |
|----------|------|
| `column` | string (column name) |
| `description` | description (`///`) |
| `lineageTag` | string (GUID) |
| `ordinal` | integer |

### role

| Property | Type |
|----------|------|
| `modelPermission` | modelPermission |
| `description` | description (`///`) |
| `member` | array |
| `tablePermission` | array |
| `annotation` | array |

### tablePermission (child of role)

| Property | Type |
|----------|------|
| `filterExpression` | DAX expression |
| `columnPermission` | array |
| `metadataPermission` | metadataPermission |

### model

| Property | Type |
|----------|------|
| `culture` | string (e.g., `en-US`) |
| `defaultPowerBIDataSourceVersion` | powerBIDataSourceVersion |
| `description` | description |
| `discourageImplicitMeasures` | boolean flag |
| `defaultMode` | modeType |
| `directLakeBehavior` | directLakeBehavior |
| `annotation` | array |
| `expression` | array |
| `function` | array |
| `queryGroup` | array |

### database

| Property | Type |
|----------|------|
| `compatibilityLevel` | integer |
| `id` | string |

## Calculation Groups

### calculationGroup (child of table)

| Property | Type |
|----------|------|
| `calculationItem` | array |
| `precedence` | integer |
| `description` | description |

### calculationItem (child of calculationGroup)

| Property | Type |
|----------|------|
| `expression` | DAX expression |
| `formatStringDefinition` | formatStringDefinition |
| `ordinal` | integer |
| `description` | description |

## Shared Expressions & Functions

### expression (shared M expression)

| Property | Type |
|----------|------|
| `expression` | M expression |
| `lineageTag` | string |
| `queryGroup` | string |
| `description` | description |
| `annotation` | array |

### function (DAX UDF)

| Property | Type |
|----------|------|
| `expression` | DAX expression |
| `isHidden` | boolean flag |
| `lineageTag` | string |
| `description` | description |
| `annotation` | array |

## Enum Values Reference

| Enum | Valid Values |
|------|-------------|
| **aggregateFunction** | `default`, `none`, `sum`, `min`, `max`, `count`, `average`, `distinctCount` |
| **columnType** | `data`, `calculated`, `rowNumber`, `calculatedTableColumn` |
| **crossFilteringBehavior** | `oneDirection`, `bothDirections`, `automatic` |
| **dataType** | `automatic`, `string`, `int64`, `double`, `dateTime`, `decimal`, `boolean`, `binary`, `unknown`, `variant` |
| **directLakeBehavior** | `automatic`, `directLakeOnly`, `directQueryOnly` |
| **metadataPermission** | `default`, `none`, `read` |
| **modeType** | `import`, `directQuery`, `default`, `push`, `dual`, `directLake` |
| **modelPermission** | `none`, `read`, `readRefresh`, `refresh`, `administrator` |
| **partitionSourceType** | `query`, `calculated`, `none`, `m`, `entity`, `policyRange`, `calculationGroup`, `inferred` |
| **powerBIDataSourceVersion** | `powerBI_V1`, `powerBI_V2`, `powerBI_V3` |
| **relationshipEndCardinality** | `none`, `one`, `many` |
| **securityFilteringBehavior** | `oneDirection`, `bothDirections`, `none` |
| **encodingHintType** | `default`, `hash`, `value` |
