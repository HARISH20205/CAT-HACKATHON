from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
from io import BytesIO

# Function to load and resize images from the local file system
def get_image_from_file(file_path, width=200):
    img = PILImage.open(file_path)
    img.thumbnail((width, width), PILImage.ANTIALIAS)
    img_buffer = BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    return Image(img_buffer)

# Sample paths for images (replace with actual image paths)
image_paths = {
    "Tire Information": "image.jpg",
    "Battery Information": "image.jpg",
    "Exterior Information": "image.jpg",
    "Brakes Information": "image.jpg",
    "Engine Information": "image.jpg",
    "Voice of Customer": "image.jpg"
}




# Data for the PDF
data = {
    "Header": {
        "Truck Serial Number": "1",
        "Truck Model": "23",
        "Inspection ID": "1",
        "Inspector": "User",
        "Inspection Employee ID": "30",
        "Inspection Date & Time": "2024-08-09 22:12",
        "Location of Inspection": "vellore",
        "Service Meter Hours": "50",
        "Customer/Company Name": "VIT",
        "CAT Customer ID": "123"
    },
    "Tire Information": {
        "Pressure on the left front tire": "yes",
        "Pressure for the right front tire": "good",
        "Condition of the left front tire": "good",
        "Condition of the right front tire": "replacement",
        "Pressure on the left rear tire": "stable",
        "Pressure on the right rear tire": "good",
        "Condition of the left rear tire": "change",
        "Condition of the right rear tire": "good",
        "Overview of tire conditions and pressures": "right front tire and left rear tire must be replaced"
    },
    "Battery Information": {
        "Battery brand": "CAT",
        "Last replaced": "last year",
        "Current voltage": "12V",
        "Water level in the battery": "good",
        "Visible damage": "no",
        "Signs of leakage or rust": "no",
        "Summary of battery condition": "battery is in perfect condition"
    },
    "Exterior Information": {
        "Rust, dents, or damage": "no",
        "Oil leak in the suspension area": "no",
        "Summary of exterior condition": "everything is fine"
    },
    "Brakes Information": {
        "Brake fluid level": "good",
        "Condition of the front brakes": "good",
        "Condition of the rear brakes": "good",
        "Status of the emergency brake": "good",
        "Summary of brake condition": "brakes are in perfect condition"
    },
    "Engine Information": {
        "Rust, dent, or damage in the engine area": "no",
        "Condition of the engine oil": "good",
        "Color of the engine oil": "brown",
        "Condition of the brake fluid": "good",
        "Color of the brake fluid": "clean",
        "Oil leak in the engine": "no",
        "Summary of engine condition": "good"
    },
    "Voice of Customer": {
        "Comments or feedback from the customer": "no",
        "Specific feedback from the customer": "tires need to be replaced",
        "Particular issues mentioned by the customer": "tires"
    }
}


#PDF Creation
pdf_file = "inspection_report.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4)
styles = getSampleStyleSheet()
story = []

# Add Header Information
story.append(Paragraph("Inspection Report", styles['Title']))
story.append(Spacer(1, 12))

for key, value in data["Header"].items():
    story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
    story.append(Spacer(1, 6))

story.append(Spacer(1, 12))

# Add sections with images
sections = ["Tire Information", "Battery Information", "Exterior Information", "Brakes Information", "Engine Information", "Voice of Customer"]

for section in sections:
    story.append(Paragraph(section, styles['Heading2']))
    story.append(Spacer(1, 12))

    for key, value in data[section].items():
        story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
        story.append(Spacer(1, 6))

    # Add image from file
    if section in image_paths:
        img = get_image_from_file(image_paths[section])
        story.append(img)
        story.append(Spacer(1, 12))

    story.append(Spacer(1, 12))

# Add Summary
summary = "The inspection reveals that the tires need to be replaced, but the battery, exterior, brakes, and engine are in good condition. Customer feedback highlights the tire issue as a primary concern."
story.append(Paragraph("Summary", styles['Heading2']))
story.append(Paragraph(summary, styles['Normal']))
story.append(Spacer(1, 12))

# Build PDF
doc.build(story)

print(f"PDF generated successfully: {pdf_file}")