from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Tables import Tables
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    download_csv_file()
    orders = read_csv_file()
    open_robot_order_website()
    complete_orders(orders)
    archive_receipts()

def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def read_csv_file():
    """Opens and reads the downloaded csv file"""
    library = Tables()
    return library.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"], header=True)

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    """Get rid of modal"""
    page = browser.page()
    page.click("text=OK")

def complete_orders(robot_orders):
    for order in robot_orders:
        page = browser.page()
        close_annoying_modal()
        fill_and_submit_the_form(order)
        while page.is_visible('//*[@class="alert alert-danger"]'):
            page.click("#order")
        pdf_path = store_receipt_as_pdf(order["Order number"])
        screenshot_path = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        page.click("#order-another")





def fill_and_submit_the_form(order):
    """Fills in the order form and click the 'Order' button"""
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.click(f'//input[@type="radio" and @value="{order["Body"]}"]')
    page.fill('//*[@placeholder="Enter the part number for the legs"]', order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")

    page.click("#order")
    
    
def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator("#receipt").inner_html()

    pdf = PDF()
    file_path = f"output/receipts/{order_number}.pdf"
    pdf.html_to_pdf(receipt, file_path)
    return file_path

def screenshot_robot(order_number):
    page = browser.page()
    file_path = f"output/{order_number}.png"
    page.screenshot(path=file_path)
    return file_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip('./output/receipts', 'receipts.zip')