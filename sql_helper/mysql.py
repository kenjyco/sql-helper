
from sql import SQLEngine

class MysqlEngine(SQLEngine):
    def get_procedure_names(self, schema='', sort=False):
        results = self.execute(
            "SELECT routine_name "
            "FROM information_schema.routines "
            "WHERE routine_type = 'PROCEDURE'"
        )
        if sort:
            results = sorted(results)
        return results

    def get_procedure_code(self, procedure):
        return b''.join(self.execute(
            "SELECT body FROM mysql.proc "
            "WHERE name = '{}'".format(procedure)
        )).decode('utf-8')

    def get_tables(self):
        return self.execute("show tables")

    def get_indexes(self, table):
        results = self.execute("SHOW INDEXES FROM {}".format(table))
        return results