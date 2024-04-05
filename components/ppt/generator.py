import base64
import logging
from typing import List
import pptx
from pptx.util import Inches, Pt
import os
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION

logger = logging.getLogger(__name__)

current_directory = os.getcwd()+"/components/ppt"
template_path = os.path.join(current_directory, "template.pptx")
base_url = settings().server.base_url

async def create_presentation(topic:str, slide_titles:List[str], slide_contents:List[str], verbose=False)->str:
    try:
        prs = pptx.Presentation(template_path)
        if verbose:
            for index, layout in enumerate(prs.slide_layouts):
                logger.log(f"Layout {index}: {layout.name}")
                #print(f" - Number of placeholders: {len(layout.placeholders)}")
        cover_layout =  prs.slide_layouts[1]
        slide_layout = prs.slide_layouts[39]
        title_slide_layout = prs.slide_layouts[1]
        close_layout =  prs.slide_layouts[3]
        if verbose:
            logger.log(f"title using {title_slide_layout.name}")
            logger.log(f"other using {slide_layout.name}")
        title_slide = prs.slides.add_slide(title_slide_layout)
        if verbose:
            logger.log(title_slide.shapes)
            logger.log(title_slide.shapes.placeholders)
            logger.log(len(title_slide.shapes.placeholders))
        title_slide.shapes.title.text = topic
        
        for slide_title, slide_content in zip(slide_titles, slide_contents):
            slide = prs.slides.add_slide(slide_layout)
            if verbose:
                logger.log(slide.shapes.placeholders)
                logger.log(len(slide.shapes.placeholders))
            slide.shapes.title.text = slide_title
            if verbose:
                for shape in slide.placeholders:
                    logger.log('%d %s' % (shape.placeholder_format.idx, shape.name))
            slide.shapes.placeholders[2].text = slide_content

        end_slide = prs.slides.add_slide(close_layout)
        save_path = os.path.join(os.getcwd(), f"static/{topic}_presentation.pptx")
        prs.save(save_path)
        public_path = f"{base_url}/static/{topic}_presentation.pptx"
        return public_path
    except Exception as e:
        logger.error(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))