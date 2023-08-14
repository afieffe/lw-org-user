# lw-org-user
A tools to manage users and groups membership recursively in a Lacework Organization


# Exemple:

Removing the user `testing@my.test.org` on all lacework sub-accounts (`all`) from the admin group and adding it to the read-only account:
```lw_user_change.py --sub-accounts all --users testing@my.test.org --add read-only --remove admin```

Performing the same change but only on the lacework sub-accounts (`account1` and `account2`):
```lw_user_change.py --sub-accounts account1 account2 --users testing@my.test.org --add read-only --remove admin```
