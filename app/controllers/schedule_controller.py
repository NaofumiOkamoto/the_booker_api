import pytz
import datetime
from models.book import Book
from database import db
from flask import jsonify
# from app import app

# @celery.task(name="app.run_test")
# def run_test(auction_id, bid_first_amount, user_id):
#     with app.app_context():
#         print('run_test auction_id: ', auction_id)
#         from test_scraping import hoge
#         result = hoge(auction_id, bid_first_amount, user_id)
#         return f"Task completed at {datetime.datetime.now().isoformat()} - Result: {result}"

def schedule_task():
    # book = Book.query.get(42)
    jst = pytz.timezone('Asia/Tokyo')
    now_jst = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    now_jst_5 = now_jst + datetime.timedelta(minutes=5)
    print('now_jst', now_jst)
    print('now_jst_5', now_jst_5)
    datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    books = Book.query.filter(
        Book.close_time > now_jst,
        Book.close_time < now_jst_5,
        Book.task_id == None,
        Book.bid_time == None
    ).all()

    if not books:
        return jsonify({"error": "Book not found"}), 404

    tasks = []
    for book in books:
        print(book.to_dict())
        close_time = book.close_time

        if close_time.tzinfo is None:
            close_time = jst.localize(close_time)
        else:
            close_time = close_time.astimezone(jst)
        
        delay = (close_time - now_jst).total_seconds()
        print(close_time)
        print(now_jst)
        print(delay)
        if delay < 0:
            return jsonify({"error": "close_time is in the past"}), 400
        
        print(f'-----start run_test.apply_async--{book.auction_id}------')
        task = run_test.apply_async(args=[book.auction_id, book.bid_first_amount, book.user_id], countdown=delay) 
        print('-----end run_test.apply_async--------')
        tasks.append(task.id)
        book.task_id = task.id
        db.session.add(book)
        db.session.commit()
        print(task.id)

    return jsonify({'tasks': tasks, 'books': [book.to_dict() for book in books]}), 202