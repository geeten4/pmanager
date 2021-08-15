### pmanager
2021
Břetislav Andr

Ke stadardnímu spuštění použijte `python main.py`

K vypsání všech příkazů použijte `python main.py help`

### Popis

Jednoduchý password manager šifrující hesla pomocí algortimu AES. Hesla jsou automaticky generována
pomocí kryptograficky bezpečné knihovny secrets.

Uživatel může dle libosti vytvářet a mazat celé databáze hesel. Každá databáze má vlastní master password.
Do každé databáze se přidávají jednotlivé záznamy. Každý záznam je jednoznačně určen hodnotou pole `title`.
Ke každému záznamu je vygenerováno heslo. Navíc u každého záznamu je možné ukládat libovlné informace do polí
`url`, `user_name` a `notes`. Záznamy je poté možné editovat a mazat.

### Příkazy

Standardní spuštení příkazem `python main.py` otevře po zadání hesla naposledy použitou databázi.
Není-li taková databáze, aplikace skončí. 

Jsou-li potřeba k příkazů další informace, je uživatel proveden jednoduchým UI.

# help 
`python main.py help`
Vypíše všechny příkazy a k nim krátký popis.

# create-db
`python main.py create-db`
Po zadání unikátního názvu databáze a libovolného master hesla vytvoří novou databázi. 

# change-db
`python main.py change-db`
Nabídne ostatní uložené databáze k otevření. 

# del-db
`python main.py del-db`
Po zadání unikátního názvu databáze smaže danou databázi.

# add-entry
`python main.py add-entry`
V zadané databázi vytvoří nový záznam. Heslo je generované automaticky. Pole `title` musí být unikátní.
Navíc je možné uložit libovolné informace do polí `url`, `user_name` a `notes`.

# edit-entry
`python main.py edit-entry`
V zadané databázi změní zadaný záznam.

# del-entry 
`python main.py del-entry`
V zadané databázi smaže záznam dle unikátního klíče `title`.
