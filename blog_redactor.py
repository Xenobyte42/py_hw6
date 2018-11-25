import configparser
import pymysql

BLOG_SECTION_NAME = "database_cfg"
BLOG_HOST_VAR = "host"
BLOG_LOGIN_VAR = "login"
BLOG_PASS_VAR = "password"
BLOG_DBNAME_VAR = "database_name"

class BlogRedactor:

    def __init__(self, cfg="db.cfg"):
        self._cfg_path = cfg
        self._cfg_parser = configparser.ConfigParser()
        self._cfg_parser.read(self._cfg_path)
        self._host = self._cfg_parser[BLOG_SECTION_NAME][BLOG_HOST_VAR]
        self._login = self._cfg_parser[BLOG_SECTION_NAME][BLOG_LOGIN_VAR]
        self._password = self._cfg_parser[BLOG_SECTION_NAME][BLOG_PASS_VAR]
        self._db_name = self._cfg_parser[BLOG_SECTION_NAME][BLOG_DBNAME_VAR]
        self._db = pymysql.connect(host=self._host,
                                   user=self._login,
                                   passwd=self._password,
                                   db=self._db_name)
        self._cursor = self._db.cursor()

        self.__authorized_users = {}

    def add_user(self, login, password):
        sql = "INSERT INTO user(login, password) VALUES('{}', '{}');".format(login, password)
        self._cursor.execute(sql)
        print("User", login, "added!")

    def authorize(self, login, password):
        sql = "SELECT id, login FROM user WHERE login='{}' AND password='{}';".format(login, password)
        self._cursor.execute(sql)
        res = self._cursor.fetchall()
        if res:
            self.__authorized_users[res[0][1]] = res[0][0]
            print("User", login, "successfully authorized!")
        else:
            print("No such user!")

    def get_user_list(self):
        sql = "SELECT login FROM user;"
        self._cursor.execute(sql)
        user_list = self._cursor.fetchall() 
        return [user[0] for user in user_list]

    def create_blog(self, username, blogname, sample):
        if username not in self.__authorized_users:
            print("User must be authorized to create blog!")
            return
        sql = """INSERT IGNORE INTO blog(user_id, name, sample)
                 VALUES('{}', '{}', '{}');""".format(self.__authorized_users[username],blogname, sample)

        print("Blog was successfully created!")
        self._cursor.execute(sql)

    def update_blog_name(self, username, last_name, new_name):
        if username not in self.__authorized_users:
            print("User must be authorized to update blog name!")
            return
        sql = """UPDATE blog SET name='{}' WHERE user_id={} AND name='{}';""".format(new_name,
                                                      self.__authorized_users[username], last_name)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Blog was successfully renamed!")
        else:
            print("No blog with that name!")
        
    def update_blog_sample(self, username, blog_name, new_sample):
        if username not in self.__authorized_users:
            print("User must be authorized to update blog sample!")
            return
        sql = """UPDATE blog SET sample='{}'
                 WHERE user_id={} AND name='{}';""".format(new_sample,
                                                      self.__authorized_users[username], blog_name)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Blog sample was successfully changed!")
        else:
            print("No blog with that name or sample has not changed!")

    def delete_blog(self, username, blogname):
        if username not in self.__authorized_users:
            print("User must be authorized to delete blog!")
            return
        sql = "DELETE FROM blog WHERE user_id={} AND name='{}';".format(self.__authorized_users[username], blogname)
        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Blog was successfully deleted!")
        else:
            print("No blog with that name!")

    def get_blogs_list(self):
        sql = "SELECT name FROM blog;"
        self._cursor.execute(sql)
        blogs_list = self._cursor.fetchall() 
        return [blog[0] for blog in blogs_list]

    def get_user_blogs(self, username):
        if username not in self.__authorized_users:
            print("User must be authorized to get own blog list!")
            return
        sql = "SELECT name FROM blog WHERE user_id={}".format(self.__authorized_users[username])
        self._cursor.execute(sql)
        blogs_list = self._cursor.fetchall() 
        return [blog[0] for blog in blogs_list]

    def create_post(self, username, header, description, blogs):
        if username not in self.__authorized_users:
            print("User must be authorized to create post!")
            return
        sql = """INSERT IGNORE
                 INTO post(header, description, user_id)
                 VALUES('{}', '{}', {})""".format(header, description,
                                                  self.__authorized_users[username])
        self._cursor.execute(sql)
        print("Post was successfully created!")
        sql = """SELECT id FROM post
                 WHERE user_id={}
                 AND description='{}'
                 AND header='{}'""".format(self.__authorized_users[username], description, header)
        self._cursor.execute(sql)
        post_id = self._cursor.fetchall()[0][0] 
        for blog in blogs:
            sql = """SELECT id FROM blog
                     WHERE name='{}' AND user_id={}""".format(blog, self.__authorized_users[username])
            self._cursor.execute(sql)
            blog_id = self._cursor.fetchall()[0][0]
            sql = "INSERT INTO blogpost(post_id, blog_id) VALUES({}, {})".format(post_id, blog_id)
            self._cursor.execute(sql)
            print("Post was successfully added to blog", blog, "!")

    def update_post_header(self, username, header, new_header):
        if username not in self.__authorized_users:
            print("User must be authorized to update post header!")
            return
        sql = """UPDATE post SET header='{}'
                 WHERE user_id={} AND header='{}';""".format(new_header,
                                                             self.__authorized_users[username], header)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully renamed!")
        else:
            print("No post with that header!")

    def update_post_description(self, username, header, new_description):
        if username not in self.__authorized_users:
            print("User must be authorized to update post description!")
            return
        sql = """UPDATE post SET description='{}'
                 WHERE user_id={} AND header='{}';""".format(new_description,
                                                            self.__authorized_users[username],
                                                            header)
        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully renamed!")
        else:
            print("No post with that header or description has not changed!")

    def update_blog_list_for_post(self, username, header, blogs):
        if username not in self.__authorized_users:
            print("User must be authorized to update post blog list!")
            return
        sql = """SELECT id, description FROM post
                 WHERE header='{}' AND user_id={};""".format(header,
                                                            self.__authorized_users[username])
        if not self._cursor.rowcount:
            print("No such post!")
            return
        self._cursor.execute(sql)
        post_id, description = self._cursor.fetchall()[0]
        sql = """DELETE FROM blogpost WHERE post_id={};""".format(post_id)
        self._cursor.execute(sql)
        for blog in blogs:
            sql = """SELECT id FROM blog
                     WHERE name='{}' AND user_id={};""".format(blog, self.__authorized_users[username])
            self._cursor.execute(sql)
            blog_id = self._cursor.fetchall()[0][0]
            sql = "INSERT INTO blogpost(post_id, blog_id) VALUES({}, {});".format(post_id, blog_id)
            self._cursor.execute(sql)
            print("Post was successfully added to blog", blog, "!")

    def delete_post(self, username, header):
        if username not in self.__authorized_users:
            print("User must be authorized to delete post!")
            return
        sql = """SELECT id FROM post
                 WHERE header='{}' AND user_id={};""".format(header,
                                                             self.__authorized_users[username])
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return
        post_id = self._cursor.fetchall()[0][0]
        sql = """DELETE FROM blogpost WHERE post_id={};""".format(post_id)
        self._cursor.execute(sql)
        sql = """DELETE FROM post
                 WHERE header='{}' AND user_id={};""".format(header,
                                                             self.__authorized_users[username])
        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully deleted!")
        else:
            print("No post with such header!")

    def add_comment(self, username, post_header, comment_text, comment_descr=""):
        if username not in self.__authorized_users:
            print("User must be authorized to create comment!")
            return
        sql = """SELECT id FROM post
                 WHERE header='{}' AND user_id={};""".format(post_header,
                                                             self.__authorized_users[username])
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return
        post_id = self._cursor.fetchall()[0][0]
        comm_id = 'NULL'
        if comment_descr:
            sql = """SELECT id FROM comment
                     WHERE post_id={}
                     AND user_id={}
                     AND description='{}';""".format(post_id,
                                                     self.__authorized_users[username],
                                                     comment_descr)
            self._cursor.execute(sql)
            if not self._cursor.rowcount:
                print("No such comment in this post!")
                return
            comm_id = self._cursor.fetchall()[0][0]
        sql = """INSERT INTO comment(user_id, post_id, parent_comment_id, description)
                 VALUES({}, {}, {}, '{}');""".format(self.__authorized_users[username],
                                                    post_id,
                                                    comm_id,
                                                    comment_text)
        self._cursor.execute(sql)
        print("Comment was successfully added!")

    def get_comment_list(self, username, post_header):
        if username not in self.__authorized_users:
            print("User must be authorized to get comment list!")
            return
        sql = """SELECT id FROM post
                 WHERE user_id={} AND header='{}'""".format(self.__authorized_users[username],
                                                            post_header)
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return
        post_id = self._cursor.fetchall()[0][0]
        sql = """SELECT description FROM comment
                 WHERE user_id={} AND post_id={}""".format(self.__authorized_users[username],
                                                           post_id)
        self._cursor.execute(sql)
        comments = self._cursor.fetchall()
        return [comment[0] for comment in comments]

    def commit_changes(self):
        self._db.commit()
        print("Changes were successfully commited!")

    def close_connection(self):
        self._cursor.close()
        self._db.close()


if __name__ == "__main__":
    blog_red = BlogRedactor()
    # blog_red.add_user('misha', '123456')
    blog_red.authorize('misha', '123456')
    # blog_red.create_blog('misha', 'My blog', 'This blog about me and my friends')
    # blog_red.update_blog_name('misha', 'My blog', 'My first blog')
    # blog_red.update_blog_sample('misha', 'My first blog', 'This is about only me')
    # blog_red.create_post('misha', 'NewPost', 'How old are you?', ['My first blog'])
    # blog_red.create_post('misha', 'ergrgsffergerg', 'How old are you?', ['My first blog'])
    # blog_red.update_post_header('misha', 'ergrgsffergerg', 'My new post x2')
    # blog_red.update_post_description('misha', 'NewPost', 'This is changed descr')
    # blog_red.create_blog('misha', 'My Blood', '21pilot')
    print('=' * 10)
    print(blog_red.get_user_blogs('misha'))
    print('=' * 10)
    print(blog_red.get_comment_list('misha', 'My new post x2'))
    print('=' * 10)
    blog_red.commit_changes()
    blog_red.close_connection()
