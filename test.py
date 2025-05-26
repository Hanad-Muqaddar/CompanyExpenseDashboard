gsheet_url = "https://docs.google.com/spreadsheets/d/1KzLZvH1IaKOqLWQmDA2HK68S_NXZwxgIaHrO7RwtO7w/edit?usp=sharing"
if "edit?usp=sharing" in gsheet_url:
    sheet_id = gsheet_url.split("/d/")[1].split("/")[0]
    print(sheet_id)