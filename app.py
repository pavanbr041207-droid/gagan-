from flask import Flask, render_template, request, redirect, session, jsonify
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "secret123"

FILE = "students.xlsx"

if not os.path.exists(FILE):
    df = pd.DataFrame(columns=[
        "usn","name",
        "sub1","sub2","sub3","sub4","sub5",
        "m1","m2","m3","m4","m5",
        "total","average","grade"
    ])
    df.to_excel(FILE, index=False)

def grade(marks):
    if any(m < 35 for m in marks):
        return "Fail"
    avg = sum(marks)/len(marks)
    if avg>=85: return "Distinction"
    elif avg>=70: return "First Class"
    elif avg>=50: return "Pass"
    else: return "Fail"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/student', methods=['GET','POST'])
def student():
    if request.method=='POST':
        usn = request.form.get('usn','')
        name = request.form.get('name','')

        subs = [request.form.get(f'sub{i}','') for i in range(1,6)]
        marks = [int(request.form.get(f'm{i}','0')) for i in range(1,6)]

        total = sum(marks)
        avg = total/5
        g = grade(marks)

        df = pd.read_excel(FILE, engine='openpyxl')
        df.loc[len(df)] = [usn,name,*subs,*marks,total,avg,g]
        df.to_excel(FILE,index=False)

        return redirect('/thankyou')

    return render_template("student.html")

@app.route('/faculty_login', methods=['GET','POST'])
def faculty_login():
    if request.method=='POST':
        if request.form['username']=="admin" and request.form['password']=="admin123":
            session['logged_in']=True
            return redirect('/faculty')
        else:
            return "Invalid Login"
    return render_template("login.html")

@app.route('/faculty')
def faculty():
    if not session.get('logged_in'):
        return redirect('/faculty_login')

    df = pd.read_excel(FILE, engine='openpyxl')
    df = df.fillna("")

    data = df.to_dict(orient='records')

    # 🔥 Find Topper
    topper = None
    if len(df) > 0:
        top_row = df.loc[df['average'].idxmax()]
        topper = top_row.to_dict()

    return render_template("faculty.html", data=data, topper=topper)

@app.route('/delete/<int:i>')
def delete(i):
    df = pd.read_excel(FILE, engine='openpyxl')
    df = df.drop(i).reset_index(drop=True)
    df.to_excel(FILE, index=False)
    return redirect('/faculty')

# 🔥 CLEAR ALL DATA
@app.route('/clear')
def clear():
    df = pd.DataFrame(columns=[
        "usn","name",
        "sub1","sub2","sub3","sub4","sub5",
        "m1","m2","m3","m4","m5",
        "total","average","grade"
    ])
    df.to_excel(FILE, index=False)
    return redirect('/faculty')

@app.route('/student_details/<int:idx>')
def student_details(idx):
    df = pd.read_excel(FILE, engine='openpyxl')
    if idx < len(df):
        row = df.iloc[idx]
        student_data = {
            'usn': str(row['usn']),
            'name': str(row['name']),
            'subjects': [str(row[f'sub{i}']) for i in range(1, 6)],
            'marks': [int(row[f'm{i}']) for i in range(1, 6)],
            'total': int(row['total']),
            'average': float(row['average']),
            'grade': str(row['grade'])
        }
        return jsonify(student_data)
    return jsonify({'error': 'Student not found'}), 404

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/thankyou')
def thankyou():
    return render_template("thankyou.html")

if __name__ == '__main__':
    app.run(debug=True)