import app.db.script_drop_data as drop
import app.db.script_create_tables as create
import app.db.seedData.generateTestData as generate

def run():
    print("Dropping Tables")
    drop.drop()
    print("Dropping users")
    drop.dropAuthUsers()
    print("Creating Tables")
    create.create()
    print("Generating test data and inserting into test database")
    generate.generate()
    print("\n===> Everything is completed\n")

run()

