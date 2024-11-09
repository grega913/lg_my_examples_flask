
'''

def make_chunks(file_path, output_path):
    ic("def make_chunks")
    chunks = partition_pdf(
        filename=file_path,
        infer_table_structure=True,             # extract Tables
        strategy="hi_res",                      # mandatory to infer tables
        extract_image_block_types=["Image"],
        image_output_dir_path = output_path,    # folder for images to be downloaded, if we want to have it stored locally
        extract_image_block_to_payload=True, # if true, will extract base64 for API usage


        chunking_strategy="by_title", # or 'basic' -> putting elements together
        max_characters=5000,
        combine_text_under_n_chars=1000,
        new_after_n_chars=6000,
    )

'''