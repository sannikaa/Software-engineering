# Lab 5 – Static Code Analysis Issues

| No. | Issue                             | Category     | Severity | Description                                                     | Fix Approach                                    |
| --- | --------------------------------- | ------------ | -------- | --------------------------------------------------------------- | ----------------------------------------------- |
| 1   | Insecure random permit generation | Security     | Medium   | Original code used random.randint() to generate permit numbers. | Replaced it with secrets.randbelow().           |
| 2   | Broad exception handling          | Code Quality | High     | Bare except blocks concealed unexpected errors.                 | Replaced them with specific exception handling. |
| 3   | Mutable default argument          | Code Quality | Medium   | register_permit() used an empty list as a default argument.     | Changed the default to None.                    |
| 4   | Unsafe file handling              | Code Quality | Medium   | Files were opened without context managers.                     | Used with open() and UTF-8 encoding.            |
| 5   | Missing input validation          | Code Quality | Medium   | Invalid zones, plates and expiry dates could be accepted.       | Added validation checks.                        |
| 6   | Incorrect function naming         | Code Quality | Low      | setExpiry() did not follow Python naming conventions.           | Renamed it to set_expiry().                     |
| 7   | Execution during import           | Code Quality | Medium   | main() ran whenever the module was imported.                    | Added the main execution guard.                 |
| 8   | Formatting issues                 | Formatting   | Low      | Original source had inconsistent formatting.                    | Reformatted the source code.                    |
