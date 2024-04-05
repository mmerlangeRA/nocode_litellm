import base64
import logging
from typing import List
import pptx
from pptx.util import Inches, Pt
import os
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION

logger = logging.getLogger(__name__)
# Define custom formatting options
TITLE_FONT_SIZE = Pt(30)
SLIDE_FONT_SIZE = Pt(16)

current_directory = os.getcwd()+"/components/ppt"

template_path = os.path.join(current_directory, "template.pptx")
print(template_path)

base_url = settings().server.base_url
async def create_presentation(topic:str, slide_titles:List[str], slide_contents:List[str])->str:
    try:
        prs = pptx.Presentation(template_path)
        for index, layout in enumerate(prs.slide_layouts):
            print(f"Layout {index}: {layout.name}")
            # If you want to print more details about each layout, you can do so here
            # For example, printing the number of placeholders:
            print(f" - Number of placeholders: {len(layout.placeholders)}")
        slide_layout = prs.slide_layouts[22]
        title_slide_layout = prs.slide_layouts[5]
        print(prs.slide_layouts)
        print(slide_layout)
        title_slide = prs.slides.add_slide(title_slide_layout)
        print(title_slide.shapes)
        title_slide.shapes.title.text = topic

        for slide_title, slide_content in zip(slide_titles, slide_contents):
            slide = prs.slides.add_slide(slide_layout)
            slide.shapes.title.text = slide_title
            print(slide.shapes.placeholders)
            print(len(slide.shapes.placeholders))
            for shape in slide.placeholders:
                print('%d %s' % (shape.placeholder_format.idx, shape.name))
            slide.shapes.placeholders[2].text = slide_content

            # Customize font size for titles and content
            slide.shapes.title.text_frame.paragraphs[0].font.size = TITLE_FONT_SIZE
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text_frame = shape.text_frame
                    for paragraph in text_frame.paragraphs:
                        paragraph.font.size = SLIDE_FONT_SIZE
        save_path = os.path.join(os.getcwd(), f"static/{topic}_presentation.pptx")
        prs.save(save_path)
        public_path = f"{base_url}/static/{topic}_presentation.pptx"
        return public_path
    except Exception as e:
        logger.error(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))