# Interficio Backend


## Building from Source

1. Create a **virtual environment** with venv(install venv, if its not installed).

    ```
    python3 -m venv django-env

    ```

2. Clone the project in the same directory.

    ```
    git clone https://github.com/lugnitdgp/interficio-backend.git

    ```

3. Activate the virtual environemnt.

    #### For Linux/Mac OSX   
    ```
    source django-env/bin/activate

    ```

4. Install the requirements.

    ```
    cd interficio-backend
    pip install -r requirements.txt

    ```

5. Copy the .env.example file to .env file.

    ```
    cp .env.example .env

    ```

6. Open the .env file and add an arbitary secret key.


7.  Migrate your database and run the Django Development Server.

    ```
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver

    ```

8. Open `http://localhost:8000` in your browser.


