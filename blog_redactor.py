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

    def set_authorized_users(self, users):
        self.__authorized_users = users

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
        sql = "SELECT id, login FROM user;"
        self._cursor.execute(sql)
        user_list = self._cursor.fetchall() 
        return {user[1]:user[0] for user in user_list}

    def create_blog(self, username, blogname, sample):
        if username not in self.__authorized_users:
            print("User must be authorized to create blog!")
            return
        sql = """INSERT INTO blog(user_id, name, sample)
                 VALUES('{}', '{}', '{}');""".format(self.__authorized_users[username],blogname, sample)

        print("Blog was successfully created!")
        self._cursor.execute(sql)

    def update_blog_name(self, username, blog_id, new_name):
        if username not in self.__authorized_users:
            print("User must be authorized to update blog name!")
            return
        sql = """UPDATE blog SET name='{}' WHERE user_id={} AND id={};""".format(new_name,
                                                      self.__authorized_users[username], blog_id)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Blog was successfully renamed!")
        else:
            print("No blog with that name!")
        
    def update_blog_sample(self, username, blog_id, new_sample):
        if username not in self.__authorized_users:
            print("User must be authorized to update blog sample!")
            return
        sql = """UPDATE blog SET sample='{}'
                 WHERE user_id={} AND id={};""".format(new_sample,
                                                      self.__authorized_users[username], blog_id)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Blog sample was successfully changed!")
        else:
            print("No blog with that name or sample has not changed!")

    def delete_blog(self, username, blog_id):
        if username not in self.__authorized_users:
            print("User must be authorized to delete blog!")
            return
        sql = "DELETE FROM blog WHERE user_id={} AND id={};".format(self.__authorized_users[username], blog_id)
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

        sql = """INSERT INTO post(header, description, user_id)
                 VALUES('{}', '{}', {})""".format(header, description,
                                                  self.__authorized_users[username])
        self._cursor.execute(sql)
        print("Post was successfully created!")

        sql = """SELECT id FROM post
                 WHERE user_id={}
                 AND description='{}'
                 AND header='{}'""".format(self.__authorized_users[username], description, header)
        self._cursor.execute(sql)
        post_id = self._cursor.fetchone()[0]

        # String like ('blog1','blog2');
        blog_list = """("""
        for blog in blogs:
            blog_list += """'{}',""".format(blog)
        blog_list = blog_list.rstrip(',') + """);"""
        
        sql = """SELECT id FROM blog WHERE name IN """ + blog_list
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such blog", blog, "!")
        else:
            blog_id = self._cursor.fetchall()

            # String like (id1, id2),(...)
            val_list = """"""
            for b_id in blog_id:
                val_list += """({},{}),""".format(post_id, b_id[0])
            val_list = val_list.rstrip(',') + """;"""
            sql = "INSERT INTO blogpost(post_id, blog_id) VALUES" + val_list
            self._cursor.execute(sql)
            print("Post was successfully added to blog", blog, "!")

    def update_post_header(self, username, post_id, new_header):
        if username not in self.__authorized_users:
            print("User must be authorized to update post header!")
            return
        sql = """UPDATE post SET header='{}'
                 WHERE user_id={} AND id={};""".format(new_header,
                                                       self.__authorized_users[username],
                                                       post_id)

        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully renamed!")
        else:
            print("No post with that header!")

    def update_post_description(self, username, post_id, new_description):
        if username not in self.__authorized_users:
            print("User must be authorized to update post description!")
            return
        sql = """UPDATE post SET description='{}'
                 WHERE user_id={} AND id={};""".format(new_description,
                                                            self.__authorized_users[username],
                                                            post_id)
        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully renamed!")
        else:
            print("No post with that header or description has not changed!")

    def update_blog_list_for_post(self, username, header, blogs):
        if username not in self.__authorized_users:
            print("User must be authorized to update post blog list!")
            return
        sql = """SELECT id FROM post
                 WHERE header='{}' AND user_id={};""".format(header,
                                                             self.__authorized_users[username])
        if not self._cursor.rowcount:
            print("No such post!")
            return
        self._cursor.execute(sql)
        post_id = self._cursor.fetchone()[0]
        sql = """DELETE FROM blogpost WHERE post_id={};""".format(post_id)
        self._cursor.execute

        blog_list = """("""
        for blog in blogs:
            blog_list += """'{}',""".format(blog)
        blog_list = blog_list.rstrip(',') + """);"""
        
        sql = """SELECT id FROM blog WHERE name IN """ + blog_list
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such blogs", blog, "!")
        else:
            blog_id = self._cursor.fetchall()

            val_list = """"""
            for b_id in blog_id:
                val_list += """({},{}),""".format(post_id, b_id[0])
            val_list = val_list.rstrip(',') + """;"""
            sql = "INSERT INTO blogpost(post_id, blog_id) VALUES" + val_list
            self._cursor.execute(sql)
            print("Post was successfully added to blog", blog, "!")

    def delete_post(self, username, post_id):
        if username not in self.__authorized_users:
            print("User must be authorized to delete post!")
            return
        sql = """SELECT id FROM post
                 WHERE id={} AND user_id={};""".format(post_id,
                                                       self.__authorized_users[username])
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return
        post_id = self._cursor.fetchone()[0]
        sql = """DELETE FROM blogpost WHERE post_id={};""".format(post_id)
        self._cursor.execute(sql)
        sql = """DELETE FROM post
                 WHERE id={} AND user_id={};""".format(post_id,
                                                       self.__authorized_users[username])
        self._cursor.execute(sql)
        if self._cursor.rowcount:
            print("Post was successfully deleted!")
        else:
            print("No post with such header!")

    def get_posts_list(self):
        sql = "SELECT header FROM post;"
        self._cursor.execute(sql)
        posts_list = self._cursor.fetchall() 
        return [post[0] for post in posts_list]

    def add_comment(self, username, post_header, comment_text, comment_descr=""):
        if username not in self.__authorized_users:
            print("User must be authorized to create comment!")
            return
        sql = """SELECT id FROM post
                 WHERE header='{}';""".format(post_header)
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return
        post_id = self._cursor.fetchone()[0]
        comm_id = 'NULL'
        if comment_descr:
            sql = """SELECT id FROM comment
                     WHERE post_id={}
                     AND description='{}';""".format(post_id,
                                                     comment_descr)
            self._cursor.execute(sql)
            if not self._cursor.rowcount:
                print("No such comment in this post!")
                return
            comm_id = self._cursor.fetchone()[0]
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
        post_id = self._cursor.fetchone()[0]
        sql = """SELECT description FROM comment
                 WHERE user_id={} AND post_id={}""".format(self.__authorized_users[username],
                                                           post_id)
        self._cursor.execute(sql)
        comments = self._cursor.fetchall()
        return [comment[0] for comment in comments]

    def get_users_comments(self, users, blog):
        comments = []

        for user in users:
            sql = """SELECT id FROM user WHERE login='{}';""".format(user)
            self._cursor.execute(sql)

            if self._cursor.rowcount:
                user_id = self._cursor.fetchone()[0]
                sql = """SELECT post_id, description
                         FROM comment WHERE user_id={};""".format(user_id)
                self._cursor.execute(sql)
                comm_list = [(comment[0], comment[1]) for comment in self._cursor.fetchall()]
                sql = """SELECT id FROM blog WHERE name='{}';""".format(blog)
                self._cursor.execute(sql)

                if self._cursor.rowcount:
                    blog_id = self._cursor.fetchone()[0]
                    sql = """SELECT post_id FROM blogpost WHERE blog_id={};""".format(blog_id)
                    self._cursor.execute(sql)
                    blog_list = [blog[0] for blog in self._cursor.fetchall()]

                    for comm in comm_list:
                        if comm[0] in blog_list:
                            comments.append(comm[1])
        return comments

    def get_sub_comments(self, post, comment):
        sql = """SELECT id FROM post WHERE header='{}';""".format(post)
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            print("No such post!")
            return

        post_id = self._cursor.fetchone()[0]
        sql = """SELECT id FROM comment
                 WHERE description='{}' AND post_id={};""".format(comment, post_id)
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            return None
        comm_id = self._cursor.fetchone()[0]
        sql = """SELECT description FROM comment
                WHERE post_id={} AND parent_comment_id={};""".format(post_id, comm_id)
        self._cursor.execute(sql)
        if not self._cursor.rowcount:
            return comment
        comments_tree = {}
        comments_tree[comment] = []
        for com in self._cursor.fetchall():
            comments_tree[comment].append(self.get_sub_comments(post, com[0]))
        return comments_tree

    def commit_changes(self):
        self._db.commit()
        print("Changes were successfully commited!")

    def close_connection(self):
        self._cursor.close()
        self._db.close()


if __name__ == "__main__":
    blog_red = BlogRedactor()
    
    blog_red.commit_changes()
    blog_red.close_connection()
