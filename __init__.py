from git.repo import Repo
from module.ui import app

if __name__ == "__main__":
    try:
        with Repo(".") as repo:
            print("Initializing database...")
            repo.submodule_update(init=True)
    except Exception as e:
        print(f"Database initialization failed!\n{e}")
        
    app.launch()