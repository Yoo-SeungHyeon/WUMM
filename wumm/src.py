"""tkinter를 활용한 GUI 기반 Wrap Up 메일 생성기."""

from __future__ import annotations

from datetime import datetime
import sqlite3
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


LOCATION_OPTIONS = ["서울", "대전", "광주", "구미", "부울경"]
DAY_OF_WEEK_OPTIONS = ["월", "화", "수", "목", "금", "토", "일"]


def _default_db_path() -> Path:
    """실행 환경에 따라 쓰기 가능한 DB 경로를 정한다.

    - PyInstaller onefile: 실행 파일이 위치한 폴더 옆에 DB 생성
    - 개발 환경: 소스와 같은 폴더에 DB 생성
    """
    if getattr(sys, "frozen", False):
        # onefile 실행 시 sys.executable이 실제 exe 경로를 가리킨다.
        return Path(sys.executable).with_name("wrapup_settings.db")
    return Path(__file__).with_name("wrapup_settings.db")


SETTINGS_DB_PATH = _default_db_path()


def _today() -> tuple[int, int, str]:
    """오늘 날짜(월, 일)와 요일을 반환한다."""
    now = datetime.now()
    return now.month, now.day, DAY_OF_WEEK_OPTIONS[now.weekday()]


def _build_email(
    cardinal_number: int,
    location: str,
    name: str,
    nth_day: int,
    month: int,
    day: int,
    day_of_week: str,
    resend: bool,
    resend_reason: str,
) -> tuple[str, str]:
    """입력값을 바탕으로 제목과 본문을 생성한다."""
    base_subject = f"[SSAFY] {cardinal_number}기 {location} 실습코치 {name} {nth_day}일차 Wrap Up"
    if resend:
        title = f"{base_subject} 재송부"
        reason = resend_reason or "첨부 오류로 인한 재송부"
        content = (
            f"안녕하십니까, {cardinal_number}기 {location} 실습코치 {name}입니다.\n\n"
            f"{month}월 {day}일({day_of_week}) {nth_day}일차 Wrap Up보고서를 {reason} 사유로 재송부드립니다.\n\n"
            "특이사항\n"
            "- 해당 사항 없음.\n\n"
            "감사합니다.\n"
            f"{name} 드림."
        )
    else:
        title = f"{base_subject} 송부"
        content = (
            f"안녕하십니까, {cardinal_number}기 {location} 실습코치 {name}입니다.\n\n"
            f"{month}월 {day}일({day_of_week}) {nth_day}일차 Wrap Up 보고서를 첨부하여 송부드립니다.\n\n"
            "특이사항\n"
            "- 해당 사항 없음.\n\n"
            "감사합니다.\n"
            f"{name} 드림."
        )
    return title, content


def _init_db(db_path: Path = SETTINGS_DB_PATH) -> None:
    """옵션 저장용 DB와 테이블을 초기화한다."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cardinal INTEGER NOT NULL,
                location TEXT NOT NULL,
                name TEXT NOT NULL,
                nth_day INTEGER NOT NULL,
                month INTEGER NOT NULL,
                day INTEGER NOT NULL,
                day_of_week TEXT NOT NULL,
                resend INTEGER NOT NULL,
                resend_reason TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _save_options(
    *,
    cardinal_number: int,
    location: str,
    name: str,
    nth_day: int,
    month: int,
    day: int,
    day_of_week: str,
    resend: bool,
    resend_reason: str,
    db_path: Path = SETTINGS_DB_PATH,
) -> None:
    """현재 입력값을 DB에 저장한다."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO options (
                cardinal,
                location,
                name,
                nth_day,
                month,
                day,
                day_of_week,
                resend,
                resend_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cardinal_number,
                location,
                name,
                nth_day,
                month,
                day,
                day_of_week,
                int(resend),
                resend_reason,
            ),
        )


def _load_latest_options(db_path: Path = SETTINGS_DB_PATH) -> dict | None:
    """마지막으로 저장한 옵션 한 건을 반환한다."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT
                cardinal,
                location,
                name,
                nth_day,
                month,
                day,
                day_of_week,
                resend,
                resend_reason
            FROM options
            ORDER BY saved_at DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def main() -> None:
    _init_db()
    root = tk.Tk()
    root.title("Wrap Up 메일 생성기")
    root.resizable(False, False)

    # 입력 영역
    main_frame = ttk.Frame(root, padding=16)
    main_frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(main_frame, text="기수").grid(row=0, column=0, sticky="w")
    cardinal_var = tk.StringVar(value="0")
    ttk.Spinbox(main_frame, from_=0, to=99, textvariable=cardinal_var, width=6).grid(
        row=0, column=1, sticky="we", padx=(8, 16)
    )

    ttk.Label(main_frame, text="지역").grid(row=0, column=2, sticky="w")
    location_var = tk.StringVar(value=LOCATION_OPTIONS[0])
    ttk.Combobox(
        main_frame,
        values=LOCATION_OPTIONS,
        textvariable=location_var,
        state="readonly",
        width=8,
    ).grid(row=0, column=3, sticky="we", padx=(8, 16))

    ttk.Label(main_frame, text="이름").grid(row=1, column=0, sticky="w", pady=(8, 0))
    name_var = tk.StringVar()
    ttk.Entry(main_frame, textvariable=name_var, width=12).grid(
        row=1, column=1, sticky="we", padx=(8, 16), pady=(8, 0)
    )

    ttk.Label(main_frame, text="N일차").grid(row=1, column=2, sticky="w", pady=(8, 0))
    nth_day_var = tk.StringVar(value="1")
    ttk.Spinbox(main_frame, from_=1, to=99, textvariable=nth_day_var, width=6).grid(
        row=1, column=3, sticky="we", padx=(8, 16), pady=(8, 0)
    )

    ttk.Label(main_frame, text="월/일").grid(row=2, column=0, sticky="w", pady=(8, 0))
    month_var = tk.StringVar()
    day_var = tk.StringVar()
    ttk.Spinbox(main_frame, from_=1, to=12, textvariable=month_var, width=6).grid(
        row=2, column=1, sticky="we", padx=(8, 4), pady=(8, 0)
    )
    ttk.Spinbox(main_frame, from_=1, to=31, textvariable=day_var, width=6).grid(
        row=2, column=2, sticky="we", padx=(4, 16), pady=(8, 0)
    )

    ttk.Label(main_frame, text="요일").grid(row=2, column=3, sticky="w", pady=(8, 0))
    day_of_week_var = tk.StringVar()
    ttk.Combobox(
        main_frame,
        values=DAY_OF_WEEK_OPTIONS,
        textvariable=day_of_week_var,
        state="readonly",
        width=6,
    ).grid(row=2, column=4, sticky="we", padx=(8, 0), pady=(8, 0))

    resend_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(main_frame, text="재송부", variable=resend_var).grid(
        row=3, column=0, sticky="w", pady=(8, 0)
    )

    ttk.Label(main_frame, text="재송부 사유").grid(row=3, column=1, sticky="w", pady=(8, 0))
    resend_reason_var = tk.StringVar()
    resend_reason_entry = ttk.Entry(
        main_frame, textvariable=resend_reason_var, width=24, state="disabled"
    )
    resend_reason_entry.grid(row=3, column=2, columnspan=3, sticky="we", pady=(8, 0))

    # 결과 영역
    result_frame = ttk.LabelFrame(root, text="생성 결과", padding=12)
    result_frame.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")

    ttk.Label(result_frame, text="제목").grid(row=0, column=0, sticky="w")
    title_text = tk.Text(result_frame, height=2, width=70, wrap="word")
    title_text.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(4, 8))

    ttk.Label(result_frame, text="본문").grid(row=2, column=0, sticky="w")
    content_text = tk.Text(result_frame, height=12, width=70, wrap="word")
    content_text.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(4, 8))

    def _set_text(widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, value)
        widget.configure(state="disabled")

    def _copy_text(widget: tk.Text) -> None:
        text = widget.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("복사", "복사할 내용이 없습니다.")
            return
        root.clipboard_clear()
        root.clipboard_append(text)
        messagebox.showinfo("복사", "클립보드에 복사되었습니다.")

    def on_toggle_resend() -> None:
        resend_reason_entry.configure(
            state="normal" if resend_var.get() else "disabled"
        )

    def on_today() -> None:
        m, d, dow = _today()
        month_var.set(str(m))
        day_var.set(str(d))
        day_of_week_var.set(dow)

    def on_reset() -> None:
        cardinal_var.set("0")
        location_var.set(LOCATION_OPTIONS[0])
        name_var.set("")
        nth_day_var.set("1")
        month_var.set("")
        day_var.set("")
        day_of_week_var.set("")
        resend_var.set(False)
        resend_reason_var.set("")
        on_toggle_resend()
        _set_text(title_text, "")
        _set_text(content_text, "")

    def _validate_common_inputs() -> tuple[int, int, int, int, str, str] | None:
        name = name_var.get().strip()
        if not name:
            messagebox.showerror("입력 오류", "이름을 입력하세요.")
            return None
        try:
            cardinal = int(cardinal_var.get())
            nth = int(nth_day_var.get())
            month = int(month_var.get())
            day = int(day_var.get())
        except ValueError:
            messagebox.showerror("입력 오류", "숫자 입력란을 확인하세요.")
            return None
        dow = day_of_week_var.get().strip()
        if dow not in DAY_OF_WEEK_OPTIONS:
            messagebox.showerror("입력 오류", "요일을 선택하세요.")
            return None
        return cardinal, nth, month, day, dow, name

    def on_generate() -> None:
        validated = _validate_common_inputs()
        if not validated:
            return
        cardinal, nth, month, day, dow, name = validated

        title, content = _build_email(
            cardinal_number=cardinal,
            location=location_var.get(),
            name=name,
            nth_day=nth,
            month=month,
            day=day,
            day_of_week=dow,
            resend=resend_var.get(),
            resend_reason=resend_reason_var.get().strip(),
        )
        _set_text(title_text, title)
        _set_text(content_text, content)

    def on_save_options() -> None:
        validated = _validate_common_inputs()
        if not validated:
            return
        cardinal, nth, month, day, dow, name = validated
        _save_options(
            cardinal_number=cardinal,
            location=location_var.get(),
            name=name,
            nth_day=nth,
            month=month,
            day=day,
            day_of_week=dow,
            resend=resend_var.get(),
            resend_reason=resend_reason_var.get().strip(),
        )
        messagebox.showinfo("저장", "옵션을 저장했습니다.")

    def on_load_options() -> None:
        data = _load_latest_options()
        if not data:
            messagebox.showinfo("불러오기", "저장된 옵션이 없습니다.")
            return
        cardinal_var.set(str(data["cardinal"]))
        location_var.set(data["location"])
        name_var.set(data["name"])
        nth_day_var.set(str(data["nth_day"]))
        month_var.set(str(data["month"]))
        day_var.set(str(data["day"]))
        day_of_week_var.set(data["day_of_week"])
        resend_var.set(bool(data["resend"]))
        resend_reason_var.set(data.get("resend_reason", "") or "")
        on_toggle_resend()
        messagebox.showinfo("불러오기", "마지막으로 저장한 옵션을 불러왔습니다.")

    ttk.Button(main_frame, text="오늘 날짜", command=on_today).grid(
        row=4, column=0, sticky="we", pady=(12, 0)
    )
    ttk.Button(main_frame, text="내용 생성", command=on_generate).grid(
        row=4, column=1, columnspan=2, sticky="we", pady=(12, 0), padx=(8, 0)
    )
    ttk.Button(main_frame, text="초기화", command=on_reset).grid(
        row=4, column=3, columnspan=2, sticky="we", pady=(12, 0), padx=(8, 0)
    )
    ttk.Button(main_frame, text="옵션 저장", command=on_save_options).grid(
        row=5, column=0, columnspan=2, sticky="we", pady=(8, 0)
    )
    ttk.Button(main_frame, text="옵션 불러오기", command=on_load_options).grid(
        row=5, column=2, columnspan=3, sticky="we", pady=(8, 0), padx=(8, 0)
    )

    ttk.Button(result_frame, text="제목 복사", command=lambda: _copy_text(title_text)).grid(
        row=4, column=0, sticky="w"
    )
    ttk.Button(
        result_frame, text="본문 복사", command=lambda: _copy_text(content_text)
    ).grid(row=4, column=1, sticky="w", padx=(8, 0))

    for i in range(5):
        main_frame.columnconfigure(i, weight=1)
        result_frame.columnconfigure(i, weight=1)

    resend_var.trace_add("write", lambda *_: on_toggle_resend())
    on_toggle_resend()
    root.mainloop()


if __name__ == "__main__":
    main()