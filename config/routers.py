class LegacyRouter:
    """Send models flagged as legacy to the legacy connection.

    The important half is allow_migrate: nothing in this project may ever
    generate DDL against the Access-era tables. Access is still using them.
    """

    legacy_apps = {"clients", "salestax", "banking", "financials",
                   "worklists", "comms"}

    def db_for_read(self, model, **hints):
        return "legacy" if model._meta.app_label in self.legacy_apps else "default"

    db_for_write = db_for_read

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, **hints):
        if app_label in self.legacy_apps:
            return False          # never migrate legacy tables
        return db == "default"
