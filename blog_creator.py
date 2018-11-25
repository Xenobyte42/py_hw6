import configparser
import pymysql


BLOG_SECTION_NAME = "database_cfg"
BLOG_HOST_VAR = "host"
BLOG_LOGIN_VAR = "login"
BLOG_PASS_VAR = "password"
BLOG_DBNAME_VAR = "database_name"

class BlogCreator:

    def __init__(self, db_name, cfg="db.cfg"):
        self._cfg_path = cfg
        self._cfg_parser = configparser.ConfigParser()
        self._cfg_parser.read(self._cfg_path)
        self._host = self._cfg_parser[BLOG_SECTION_NAME][BLOG_HOST_VAR]
        self._login = self._cfg_parser[BLOG_SECTION_NAME][BLOG_LOGIN_VAR]
        self._password = self._cfg_parser[BLOG_SECTION_NAME][BLOG_PASS_VAR]
        self._db_name = db_name
        self._db = pymysql.connect(host=self._host,
                                   user=self._login,
                                   passwd=self._password)
        self._cursor = self._db.cursor()

    def create_blog_database(self):
        sql = "CREATE DATABASE IF NOT EXISTS {};".format(self._db_name, self._db_name)
        self._cursor.execute(sql)
        self._db.commit()
        print("Database created --- OK")

    def connect_to_db(self):
        self._cursor.close()
        self._db.close()
        self._db = pymysql.connect(host=self._host,
                                   user=self._login,
                                   passwd=self._password,
                                   db=self._db_name)
        self._cursor = self._db.cursor()
        

    def create_user_table(self):
        sql = """CREATE TABLE IF NOT EXISTS user (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            login VARCHAR(20) NOT NULL UNIQUE,
            password VARCHAR(20) NOT NULL
        );
        """
        self._cursor.execute(sql)
        self._db.commit()
        print("User table created --- OK")

    def create_post_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS post (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            header VARCHAR(50) NOT NULL UNIQUE,
            description VARCHAR(500) NOT NULL,
            user_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
        );
        '''
        self._cursor.execute(sql)
        self._db.commit()
        print("Post table created --- OK")

    def create_blog_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS blog (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            name VARCHAR(40) UNIQUE,
            sample VARCHAR(150),
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
        );
        '''
        self._cursor.execute(sql)
        self._db.commit()
        print("Blog table created --- OK")

    def create_blogpost_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS blogpost (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            blog_id INT NOT NULL,
            post_id INT NOT NULL,
            FOREIGN KEY (blog_id) REFERENCES blog (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post (id)
        );
        '''
        self._cursor.execute(sql)
        self._db.commit()
        print("Blogpost table created --- OK")

    def create_comment_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS comment (
            id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            user_id INT NOT NULL,
            post_id INT NOT NULL,
            parent_comment_id INT DEFAULT NULL,
            description VARCHAR(200),
            FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES post (id) ON DELETE CASCADE,
            FOREIGN KEY (parent_comment_id) REFERENCES comment (id) ON DELETE CASCADE
        );
        '''
        self._cursor.execute(sql)
        self._db.commit()
        print("Comment table created --- OK")

    def close_connection(self):
        self._cursor.close()
        self._db.close()
        self._cfg_parser.set(BLOG_SECTION_NAME, BLOG_DBNAME_VAR, self._db_name)
        with open(self._cfg_path, 'w') as cfg:
            self._cfg_parser.write(cfg)


if __name__ == "__main__":
    blog_cr = BlogCreator('blog_db4')
    blog_cr.create_blog_database()
    blog_cr.connect_to_db()
    blog_cr.create_user_table()
    blog_cr.create_blog_table()
    blog_cr.create_post_table()
    blog_cr.create_blogpost_table()
    blog_cr.create_comment_table()
    blog_cr.close_connection()
