## this is description of some asssumptions/edge cases on which the system is based on

### 1) email and name are non unique field
- typically this is not done in normal situations as this leaves danger of duplicate entities in table but i have took  that assumption because in stripe table i saw that entities with same email and name were also allowed so if I would made our table with unique email validation then it would not be able to store all the entities in stripe table as only unique emails will be stored.

