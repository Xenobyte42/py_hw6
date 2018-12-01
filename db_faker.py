import argparse
import blog_redactor
import sys
from faker import Faker
from time import time
from random import randint, choice


class DatabaseFiller:

    def __init__(self, args):
        self._usr_cnt = args.users_cnt
        self._blogs_cnt = args.blogs_cnt
        self._posts_cnt = args.posts_cnt
        self._comm_cnt = args.comm_cnt

    def _fake_users(self, db):
        faker = Faker()
        for _ in range(self._usr_cnt):
            try:
                db.add_user(faker.user_name(), faker.password())
            except:
                pass
        db.commit_changes()

    def _fake_blogs(self, db, usr_dict):
        cnt = 0
        faker = Faker()
        for user in usr_dict:
            db.create_blog(user, faker.text()[:30], faker.text()[:140])
            cnt += 1
            if cnt >= self._blogs_cnt:
                break
        db.commit_changes()

    def _fake_posts(self, db, usr_dict):
        cnt = 0
        faker = Faker()
        blogs_list = db.get_blogs_list()
        while cnt < self._posts_cnt:
            for user in usr_dict:
                blog_cnt = randint(1, 4)
                temp_blogs = [choice(blogs_list) for i in range(blog_cnt)]
                db.create_post(user, faker.text()[:40], faker.text(), temp_blogs)
                cnt += 1
                if cnt >= self._posts_cnt:
                    break
        db.commit_changes()

    def _fake_comments(self, db, usr_dict):
        cnt = 0
        faker = Faker()
        posts_list = db.get_posts_id()

        while cnt < self._comm_cnt / 2:
            for user in usr_dict:
                db.add_comment(user, choice(posts_list), faker.text()[:100])
                cnt += 1
                if cnt >= self._comm_cnt / 2:
                    break
        comments_id = db.get_comments_id()
        while cnt <  self._comm_cnt:
            for user in usr_dict:
                comment = choice(comments_id)
                db.add_comment(user, comment[1], faker.text()[:100], comment[0])
                cnt += 1
                if cnt >= self._comm_cnt:
                    break
        db.commit_changes()

    def fill(self, db):
        if self._usr_cnt:
            self._fake_users(db)
        usr_dict = db.get_user_list()
        db.set_authorized_users(usr_dict)
        if self._blogs_cnt:
            self._fake_blogs(db, usr_dict)
        if self._posts_cnt:
            self._fake_posts(db, usr_dict)
        if self._comm_cnt:
            self._fake_comments(db, usr_dict)
        

def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a faker parser')
    parser.add_argument(
        '-U',
        action="store",
        dest="users_cnt",
        type=int,
        default=0,
        help='Users count')
    parser.add_argument(
        '-B',
        action="store",
        dest="blogs_cnt",
        type=int,
        default=0,
        help='Blogs count')
    parser.add_argument(
        '-P',
        action="store",
        dest="posts_cnt",
        type=int,
        default=0,
        help='Posts count')
    parser.add_argument(
        '-C',
        action="store",
        dest="comm_cnt",
        type=int,
        default=0,
        help='Comments count')
    return parser.parse_args(args)

if __name__ == "__main__":
    params = parse_args(sys.argv[1:])
    filler = DatabaseFiller(params)
    start = time()
    bl_red = blog_redactor.BlogRedactor()
    filler.fill(bl_red)
    bl_red.close_connection
    print("Faker work time - ", time() - start)

