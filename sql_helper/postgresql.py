from sql import SQLEngine

class PostgresqlEngine(SQLEngine):
    def get_procedure_names(self, schema='', sort=False):
        if schema:
            statement = (
                "SELECT proname "
                "FROM pg_catalog.pg_namespace n "
                "JOIN pg_catalog.pg_proc p on pronamespace = n.oid "
                "WHERE nspname = '{}'".format(schema)
            )
            if sort:
                statement += " ORDER BY proname"
        else:
            statement = (
                "SELECT proname, nspname "
                "FROM pg_catalog.pg_namespace n "
                "JOIN pg_catalog.pg_proc p on pronamespace = n.oid "
                "WHERE nspname NOT IN ('pg_catalog', 'information_schema')"
            )
            if sort:
                statement += " ORDER BY nspname, proname"
        return self.execute(statement)

    def get_procedure_code(self, procedure):
        return ''.join(self.execute(
            "SELECT prosrc FROM pg_proc "
            "WHERE proname = '{}'".format(procedure)
        ))

    def get_tables(self):
        results = self.execute(
            "SELECT schemaname, tablename "
            "FROM pg_catalog.pg_tables "
            "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' "
            "ORDER BY schemaname, tablename"
        )
        return [
            r['schemaname'] + '.' + r['tablename']
            for r in results
        ]

    def get_indexes(self, table, schema=None):
        if '.' in table and schema is None:
            schema, table = table.split('.', 1)
        query = (
            "SELECT * "
            "FROM pg_indexes "
            "WHERE tablename = :table "
            "ORDER BY schemaname, tablename, indexname"
        )
        results = self.execute(query, {'table': table})
        return results

    def get_schemas(self, sort=False):
        results = self.execute(
            "SELECT schema_name FROM information_schema.schemata"
        )
        if sort:
            results = sorted(results)
        return results