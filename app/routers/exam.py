from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.db.college_engine import get_db
from app.models.college import ExamScore, Student
from app.schemas.exam import ExamScoreCreate, ExamScoreResponse

router = APIRouter(prefix="/exam", tags=["exam"])


@router.get("/analytics/year")
def year_wise_exam_analytics(year: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(Student.year, func.avg(ExamScore.percentage).label("avg_percentage")).join(Student, Student.id == ExamScore.student_id).filter(Student.year == year, Student.college_id == x_college_id).group_by(Student.year).all()
    return result


from sqlalchemy import func, case

@router.get("/analytics/semester")
def semester_wise_exam_analytics(
    semester: int,
    db: Session = Depends(get_db),
    x_college_id: int = Header(...)
):
    result = db.query(
        Student.semester,
        func.avg(ExamScore.percentage).label("avg_percentage"),
        func.count(ExamScore.id).label("total_students"),
        func.sum(case((ExamScore.is_pass == True, 1), else_=0)).label("pass_students"),
        func.sum(case((ExamScore.is_pass == False, 1), else_=0)).label("fail_students"),
    ).join(Student, Student.id == ExamScore.student_id)\
     .filter(Student.semester == semester, Student.college_id == x_college_id)\
     .group_by(Student.semester)\
     .first()

    if not result:
        return {"message": "No data found"}

    return {
        "semester": result.semester,
        "average_percentage": round(result.avg_percentage, 2),
        "total_students": result.total_students,
        "pass_students": result.pass_students,
        "fail_students": result.fail_students
    }


@router.post("/", response_model=ExamScoreResponse)
def add_exam_score(data: ExamScoreCreate, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    try:
        student = db.query(Student).filter(Student.id == data.student_id, Student.college_id == x_college_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # basic marks validation
        subjects = {
            "hindi": data.hindi,
            "english": data.english,
            "maths": data.maths,
            "science": data.science,
            "social_science": data.social_science,
        }
        for subj, marks in subjects.items():
            if marks < 0 or marks > 100:
                raise HTTPException(status_code=400, detail=f"{subj} marks must be between 0 and 100")

        total = sum(subjects.values())
        average = total / 5.0
        percentage = (total / 500.0) * 100.0

        if percentage >= 90:
            grade_point = 10
        elif percentage >= 80:
            grade_point = 9
        elif percentage >= 70:
            grade_point = 8
        elif percentage >= 60:
            grade_point = 7
        elif percentage >= 50:
            grade_point = 6
        elif percentage >= 40:
            grade_point = 5
        else:
            grade_point = 0

        failed_subjects = [s for s, m in subjects.items() if m < 40]
        is_pass = False if failed_subjects else True

        exam = ExamScore(
            student_id=data.student_id,
            college_id=x_college_id,
            exam_type=data.exam_type,
            **subjects,
            total=total,
            average=average,
            percentage=percentage,
            grade_point=grade_point,
            is_pass=is_pass,
        )

        db.add(exam)
        db.commit()
        db.refresh(exam)

        return exam
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}")
def student_exam_summary(student_id: int, year: Optional[int] = Query(default=None), semester: Optional[int] = Query(default=None), db: Session = Depends(get_db), x_college_id: int = Header(...)):
    exams = db.query(ExamScore).filter(ExamScore.student_id == student_id, ExamScore.college_id == x_college_id).all()
    if not exams:
        raise HTTPException(status_code=404, detail="No exam records found")
    overall_total = sum(exam.total for exam in exams)
    overall_average = overall_total / (len(exams) * 5)
    overall_percentage = (overall_total / (len(exams) * 500)) * 100
    return {"student_id": student_id, "total_exams": len(exams), "overall_total_marks": overall_total, "overall_average": overall_average, "overall_percentage": overall_percentage}


@router.get("/cgpa/{student_id}")
def calculate_cgpa(student_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    exams = db.query(ExamScore).filter(ExamScore.student_id == student_id, ExamScore.college_id == x_college_id).all()
    if not exams:
        raise HTTPException(status_code=404, detail="No exam records found")
    cgpa = sum(exam.grade_point for exam in exams) / len(exams)
    return {"student_id": student_id, "total_exams": len(exams), "cgpa": round(cgpa, 2)}


@router.get("/result-status/{student_id}")
def pass_fail_status(student_id: int, db: Session = Depends(get_db), x_college_id: int = Header(...)):
    exams = db.query(ExamScore).filter(ExamScore.student_id == student_id, ExamScore.college_id == x_college_id).all()
    if not exams:
        raise HTTPException(status_code=404, detail="No exams found")
    failed_subjects = []
    for exam in exams:
        subjects = {"hindi": exam.hindi, "english": exam.english, "maths": exam.maths, "science": exam.science, "social_science": exam.social_science}
        for subject, marks in subjects.items():
            if marks < 40:
                failed_subjects.append(subject)
    status = "PASS" if not failed_subjects else "FAIL"
    return {"student_id": student_id, "status": status, "failed_subjects": failed_subjects}


@router.get("/ranking")
def student_ranking(db: Session = Depends(get_db), x_college_id: int = Header(...)):
    result = db.query(ExamScore.student_id, func.avg(ExamScore.percentage).label("avg_percentage")).filter(ExamScore.college_id == x_college_id).group_by(ExamScore.student_id).order_by(func.avg(ExamScore.percentage).desc()).all()
    ranking = []
    rank = 1
    for row in result:
        ranking.append({"rank": rank, "student_id": row.student_id, "average_percentage": round(row.avg_percentage, 2)})
        rank += 1
    return ranking
