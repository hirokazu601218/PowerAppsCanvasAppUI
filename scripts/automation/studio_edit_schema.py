"""Isolated Studio CRUD tables in the existing environment.

Keep business columns identical to the current three tables. The distinct table
and relationship names keep Studio writes out of the stable app's data sources.
"""

from copy import deepcopy

import commute_schema
import payrollledger_schema
import staff_schema


TABLES = (
    ("crb3c_studiostaffbasic", "crb3c_StudioStaffBasic", "M_職員基本_STUDIO", staff_schema),
    ("crb3c_studiocommute", "crb3c_StudioCommute", "T_通勤_STUDIO", commute_schema),
    ("crb3c_studiopayrollledger", "crb3c_StudioPayrollLedger", "T_基準給与簿_STUDIO", payrollledger_schema),
)


def table_definition(index, lcid):
    logical, schema, display, module = TABLES[index]
    definition = deepcopy(module.table(lcid))
    definition["SchemaName"] = schema
    definition["DisplayName"] = module.label(display, lcid)
    definition["DisplayCollectionName"] = module.label(display, lcid)
    definition["Description"] = module.label(
        "Studio編集用の隔離された架空データ。安定版の3テーブルとは別。", lcid
    )
    return definition


def relationship_definition(index, lcid, parent_id):
    assert index in (1, 2)
    module = TABLES[index][3]
    definition = deepcopy(module.relationship(lcid, parent_id))
    suffix = "commute" if index == 1 else "payrollledger"
    definition["SchemaName"] = "crb3c_studiostaffbasic_" + suffix
    definition["ReferencedEntity"] = TABLES[0][0]
    definition["ReferencingEntity"] = TABLES[index][0]
    definition["ReferencedEntityNavigationPropertyName"] = (
        "crb3c_StudioStaffBasic_" + ("Commutes" if index == 1 else "PayrollLedgers")
    )
    # Lookup name can stay the same inside a distinct child table. Its target is
    # the Studio parent above; never the original crb3c_staffbasic table.
    return definition
