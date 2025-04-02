import requests
from bs4 import BeautifulSoup


def get_school_reports(cds_code):
    """
    Will scrape all links inside reports panel of the school's CDE website,
    checks if they have a URL, checks it the report name is supported by our
    current program, then asks the user if they are interested in compiling a
    summary for that report as well. Finally, we iterate through all reports of
    interest, then we use our show_report() function to process each report type
    in it's own way.

    cds_code -- all numeric cds code identifier for the target school
    """
    url = f"https://www.cde.ca.gov/sdprofile/details.aspx?cds={cds_code}"
    response = requests.get(url)
    supported_report_names = [
        "Enrollment By Ethnicity",
        "California Assessment of Student Performance and Progress (CAASPP)",
        "English Language Proficiency Assessments for California (ELPAC)",
    ]

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup)
        reports_panel = soup.find(id="pnlReports")
        links = reports_panel.find_all("a", href=True)

        target_reports = []

        for link in links:
            if link.text in supported_report_names:
                while True:
                    response = input(f"Report on '{link.text}'? (y/n): ")
                    if response.lower() == "y":
                        target_reports.append(link)
                        print("[compiling report...]\n")
                        break
                    elif response.lower() == "n":
                        print("\n")
                        break
                    else:
                        print("Not Valid Input (y/n)\n")

        for report in target_reports:
            report_name = report.text
            report_url = report["href"]
            show_report(report_name, report_url)

    else:
        print(f"Failed to connect with API! (something beyond our wizardy powers)")


def show_report(name, url):
    """
    show_report will print out a customize report based on the name and the url
    of the given report
    name -- name of report (case sensitive, because there are similar named reports)
    url -- where report webpage is located
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    print(soup)
    if response.status_code == 200:
        if name == "Enrollment By Ethnicity":
            print("========================")
            print("Enrollment By Ethnicity")
            print("========================")
            container = soup.find(id="ContentPlaceHolder1_pnlReport")
            title = container.find("h1").text
            headers = container.find("thead").find("tr").find_all("th")
            data = container.find("tbody").find("tr").find_all("td")

            ethnicities = [td.text for index, td in enumerate(headers) if index >= 2]
            percentages = [
                float(td.text.strip().replace("%", ""))
                for index, td in enumerate(data)
                if index >= 2
            ]

            max_val = max(percentages)
            max_idx = percentages.index(max_val)
            most_ethnicity = ethnicities[max_idx]
            min_val = min(percentages)
            min_idx = percentages.index(min_val)
            least_ethnicity = ethnicities[min_idx]

            print(f"Most ethnic group: {most_ethnicity} ({max_val}%)")
            print(f"Least ethnic group: {least_ethnicity} ({min_val}%)")
        elif (
            name == "California Assessment of Student Performance and Progress (CAASPP)"
        ):
            print("========================")
            print("CAASPP Summary")
            print("========================")
            percentage = soup.find(id="MainContent_lblDonutElaInnerCnt1").text
            print(f"{percentage} of student at this school, Met or Exceeded standards")

        elif name == "English Language Proficiency Assessments for California (ELPAC)":
            print("========================")
            print("ELPAC Summary")
            print("========================")
            percentage = soup.find(id="MainContent_lblDonut1InnerCnt1")
            print(
                f"{percentage} of non-native english speakers with English Proficiency"
            )

        else:
            print("Unknown Report")
    else:
        print(f"Failed to connect with API! (something beyond our wizardy powers)")


if __name__ == "__main__":
    cds_code = input("Please enter the CDS code of the school: ")
    get_school_reports(cds_code)
