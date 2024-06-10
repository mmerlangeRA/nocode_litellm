import base64
import logging
from typing import Dict, List
import pptx
from pptx.util import Inches, Pt
import os
from components.rag.query import get_chunk_by_id, get_chunk_file_id_and_page_by_id
from settings.settings import settings
from server.utils.errors import INTERNAL_SERVER_ERROR_HTTPEXCEPTION
import re

logger = logging.getLogger(__name__)

current_directory = os.getcwd()+"/components/ppt"
template_path = os.path.join(current_directory, "mini_template.pptx")
base_url = settings().server.base_url

def format_chunk_sources_and_list_ids(input_string):
    index = 1  # Start index from 1
    regex = re.compile(r'<<([^>]*)>>')  # Regex to find patterns like <<id>>
    ids = []  # List to store the captured IDs

    def replacer(match):
        nonlocal index
        id = match.group(1)  # Capture the ID inside << >>
        ids.append(id)  # Add the captured ID to the list
        replacement = f'[{index}]'  # Convert index to string for replacement
        index += 1  # Increment the index for the next match
        return replacement

    modified = regex.sub(replacer, input_string)
    return modified, ids

def aggregate_indexes(file_data: List[Dict[str, str]]) -> List[Dict[str, List[str]]]:
    """
    Aggregate indexes by file names.

    :param file_data: List of dictionaries with 'index' and 'file_name' keys.
    :return: List of dictionaries with 'file_name' and 'indexes' (list of indexes).
    """
    file_index_map = {}  # Dictionary to hold file_name as key and list of indexes as value

    # Loop through each entry in the input list
    for item in file_data:
        file_name = item['file_name']
        index = item['index']
        
        # If file_name is not yet in the dictionary, add it with a new list
        if file_name not in file_index_map:
            file_index_map[file_name] = []
        
        # Append the current index to the list of indexes for this file_name
        file_index_map[file_name].append(index)

    # Convert the dictionary back to a list of dictionaries as specified
    result = [{'file_name': key, 'indexes': value} for key, value in file_index_map.items()]
    return result


async def create_presentation(topic, slide_titles, slide_contents, verbose=True):
    try:
        prs = pptx.Presentation(template_path)
        if verbose:
            for index, layout in enumerate(prs.slide_layouts):
                logger.log(logging.DEBUG, f"Layout {index}: {layout.name}")
                print(f"Layout {index}: {layout.name}")
        
        cover_layout =  prs.slide_layouts[1]
        slide_layout = prs.slide_layouts[39]
        title_slide_layout = prs.slide_layouts[2]
        close_layout =  prs.slide_layouts[1]
        
        if verbose:
            print(f"title using {title_slide_layout.name}")
            print(f"other using {slide_layout.name}")
            logger.log(logging.DEBUG, f"title using {title_slide_layout.name}")
            logger.log(logging.DEBUG, f"other using {slide_layout.name}")
        
        # Title Slide
        title_slide = prs.slides.add_slide(title_slide_layout)
        print(title_slide.shapes)
        title_slide.shapes.title.text = topic

        for slide_title, slide_content in zip(slide_titles, slide_contents):
            slide = prs.slides.add_slide(slide_layout)
            print("step1")
            slide.shapes.title.text = slide_title
            print("step2")
            modified_slide_content, source_list = format_chunk_sources_and_list_ids(slide_content)
            bullet_points = modified_slide_content.split('\n')
            print("step3")
            text_box = slide.shapes.placeholders[1].text_frame
            text_box.clear()
            print(text_box)
            print("step4")
            reference_box = slide.shapes.placeholders[2].text_frame
            reference_box.clear()
            print(reference_box)

            for line in bullet_points:
                if line.strip().startswith('- **'):
                    p = text_box.add_paragraph()
                    text = line.strip()[2:].strip()
                    text = text.replace('**', '')
                    p.text = text
                    p.font.bold = True
                    p.level = 0
                elif line.strip().startswith('- '):
                    p = text_box.add_paragraph()
                    text = line.strip()[2:].strip()
                    text = text.replace('**', '')
                    p.text = text
                    p.level = 1
                elif line.strip().startswith('  - '):
                    p = text_box.add_paragraph()
                    text = line.strip()[4:].strip()
                    text = text.replace('**', '')
                    p.text = text
                    p.level = 2
            references_text = "" 
            print(f'nb souces {len(source_list)}')
            if len(source_list) > 0:
                index = 0
                modified_slide_content += "\n------------------------\n"
                chunks = []
                for chunk_id in source_list:
                    index += 1
                    chunk = get_chunk_file_id_and_page_by_id(chunk_id)
                    chunks.append({'index': index, 'file_name': chunk['file_name']})
                references = aggregate_indexes(chunks)
                for reference in references:
                    file_name = reference['file_name']
                    list_indexes = reference['indexes']
                    indexes = "".join(f'[{index}]' for index in list_indexes)
                    references_text += f'{file_name} : {indexes} \n'
                p = reference_box.add_paragraph()
                p.text = references_text

        # Closing Slide
        end_slide = prs.slides.add_slide(close_layout)

        save_path = os.path.join(os.getcwd(), f"static/{topic}_presentation.pptx")
        prs.save(save_path)
        public_path = f"{base_url}/static/{topic}_presentation.pptx"
        return public_path
    except Exception as e:
        logger.error(e)
        raise Exception(str(e))


async def create_presentation_old(topic:str, slide_titles:List[str], slide_contents:List[str], verbose=False)->str:
    try:
        prs = pptx.Presentation(template_path)
        if verbose:
            for index, layout in enumerate(prs.slide_layouts):
                logger.log(logging.DEBUG, f"Layout {index}: {layout.name}")
                #print(f" - Number of placeholders: {len(layout.placeholders)}")
        cover_layout =  prs.slide_layouts[1]
        slide_layout = prs.slide_layouts[39]
        title_slide_layout = prs.slide_layouts[1]
        close_layout =  prs.slide_layouts[3]
        if verbose:
            logger.log(logging.DEBUG,f"title using {title_slide_layout.name}")
            logger.log(logging.DEBUG,f"other using {slide_layout.name}")
        title_slide = prs.slides.add_slide(title_slide_layout)
        if verbose:
            logger.log(logging.DEBUG,title_slide.shapes)
            logger.log(logging.DEBUG,title_slide.shapes.placeholders)
            logger.log(logging.DEBUG,len(title_slide.shapes.placeholders))
        title_slide.shapes.title.text = topic
        
        for slide_title, slide_content in zip(slide_titles, slide_contents):
            slide = prs.slides.add_slide(slide_layout)
            if verbose:
                logger.log(logging.DEBUG,slide.shapes.placeholders)
                logger.log(logging.DEBUG,len(slide.shapes.placeholders))
            slide.shapes.title.text = slide_title
            if verbose:
                for shape in slide.placeholders:
                    logger.log(logging.DEBUG,'%d %s' % (shape.placeholder_format.idx, shape.name))
            modified_slide_content, source_list = format_chunk_sources_and_list_ids(slide_content)
            if len(source_list) > 0:
                index=0
                modified_slide_content +="\n------------------------\n"
                chunks=[]
                for chunk_id in source_list:
                    index+=1
                    chunk = get_chunk_file_id_and_page_by_id(chunk_id)
                    chunks.append({'index':index,'file_name':chunk['file_name']})
                references = aggregate_indexes(chunks)
                for reference in references:
                    file_name = reference['file_name']
                    list_indexes = reference['indexes']
                    indexes=""
                    for index in list_indexes:
                        indexes+=f'[{index}]'
                    modified_slide_content+=f'{file_name} : {indexes} \n'
            slide.shapes.placeholders[2].text = modified_slide_content

        end_slide = prs.slides.add_slide(close_layout)
        save_path = os.path.join(os.getcwd(), f"static/{topic}_presentation.pptx")
        prs.save(save_path)
        public_path = f"{base_url}/static/{topic}_presentation.pptx"
        return public_path
    except Exception as e:
        logger.error(e)
        raise INTERNAL_SERVER_ERROR_HTTPEXCEPTION(str(e))