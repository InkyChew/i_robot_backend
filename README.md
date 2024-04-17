## Project setup
1. create a database.
2. change your database config in app.py
   ```
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1/stockai'
   ```
3. open XAMPP to run up Apache and MySQL.
4. run `python app.py` in your terminal.
5. open the browser and paste `http://localhost:8888/` 
   if it shows `ok` than success.