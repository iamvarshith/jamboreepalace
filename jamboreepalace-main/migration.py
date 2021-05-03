from app import manager

if __name__ == '__main__':
    manager.run()

# The below commands to be run in cmd to migrate the existing db model
# $ python migration.py db init
# $ python migration.py db migrate
# $ python migration.py db upgrade

# ------------------>help < -------------------------- #
# $ python migration.py db --help
