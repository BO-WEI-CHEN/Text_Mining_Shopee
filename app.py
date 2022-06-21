from flask import Flask, render_template
import sqlite3 as sql
from flask import request
from utils import word_seg, count_term_freq

app = Flask(__name__)


# coneect database yaya


@app.route('/')
def index():
    con = sql.connect("product.db")
    cur = con.cursor()
    cur.execute("select COUNT(*) from product")
    row_count = cur.fetchall()[0][0]
    return render_template('index.html', row_count=row_count)


@app.route('/datalist')
def datalist():
    con = sql.connect("product.db")
    cur = con.cursor()
    cur.execute("select * from product")
    rows = cur.fetchall()
    rows = [("https://shopee.tw/{}-i.{}.{}".format(p[1], p[0].split("_")[0], p[0].split("_")[1]),) + p for p in
            rows]
    print(rows)
    return render_template('datalist.html', title=rows)


@app.route('/analysis', methods=['POST', 'GET'])
def analysis():
    if request.method == 'POST':
        con = sql.connect("product.db")
        cur = con.cursor()
        cur.execute("select description from product")
        all_data = cur.fetchall()
        all_data = [p[0] for p in all_data]
        text = request.form['text1']
        filter_result = [data for data in all_data if text in data]
        seg_result = word_seg(filter_result)
        term_freq = count_term_freq([word for doc in seg_result for word in doc])

        print(term_freq)
        return render_template('analysis.html', result=term_freq)

    else:
        return render_template('analysis.html')


if __name__ == '__main__':
    app.run()
