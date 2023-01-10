import csv
import os

import gspread
from dotenv import load_dotenv
from flask import Flask, render_template, request

app = Flask(__name__)

# Google Sheets API
def add_values_to_gsheet(
    spreadsheet_id: str,
    row: list,
    index: int = 2,
):
    gc = gspread.service_account(filename="./credentials.json")
    spreadsheet = gc.open_by_key(spreadsheet_id)
    sheet_in_spreadsheet = spreadsheet.get_worksheet(0)
    sheet_in_spreadsheet.insert_row(values=row, index=index)


def write_to_gsheet(data: dict):
    row = [data["Name"], data["Regno"], data["Email"], data["Phone"], data["Message"]]
    add_values_to_gsheet(
        spreadsheet_id="1M2d92D9k2dCXptgV-BPbAQWH2sMIkmhgNCqZDIO7ZB4", row=row
    )


# CSV
def check_if_exists_in_directory(file_or_folder_name: str, directory: str = "") -> bool:
    current_working_dir = os.getcwd()
    try:
        if directory:
            os.chdir(directory)
        return file_or_folder_name in os.listdir()
    except FileNotFoundError:
        return False
    finally:
        os.chdir(current_working_dir)


def write_to_csv(data: dict):
    header = ["Name", "Regno", "Email", "Phone", "Message"]

    row = [data["Name"], data["Regno"], data["Email"], data["Phone"], data["Message"]]

    file_exists = check_if_exists_in_directory("CTFregistrations.csv")

    with open("CTFregistrations.csv", "a") as csv_file_obj:
        csv_write = csv.writer(csv_file_obj, delimiter=",", lineterminator="\n")
        if file_exists:
            csv_write.writerow(row)
        else:
            csv_write.writerow(header)
            csv_write.writerow(row)


def check_user_exists_in_csv(data: dict):
    if not check_if_exists_in_directory("CTFregistrations.csv"):
        return False
    else:
        with open("CTFregistrations.csv", "r") as csv_file_obj:
            csv_reader = csv.DictReader(csv_file_obj)
            for row in csv_reader:
                if data["Regno"] == row["Regno"]:
                    return True
            return False


@app.route("/", methods=["POST", "GET"])
def data():
    data = {}
    if request.method == "POST":
        data["Name"] = request.form["Name"]
        data["Regno"] = request.form["Regno"].upper()
        data["Email"] = request.form["Email"]
        data["Phone"] = request.form["Phone"]
        if "Message" in request.form:
            data["Message"] = request.form["Message"]
        else:
            data["Message"] = ""

        if check_user_exists_in_csv(data):
            return render_template(
                "index.html", filled=True, show_message="You have already registered!"
            )
        else:
            write_to_csv(data)
            write_to_gsheet(data)
            return render_template(
                "index.html",
                show_message="You have successfully registered",
                filled=True,
            )

    return render_template("index.html", yet_to_register=True, filled=False)


if __name__ == "__main__":
    load_dotenv(".env")
    app.run(debug=bool(os.getenv("DEBUG")),host='0.0.0.0')