import os
def generate_path_to_attachment(filetype, filename, fileformat, prefix, filetype_folder, is_cwd_required = True):
            return ".".join(
               [ os.path.join(
                os.getcwd() if is_cwd_required else "",
                prefix,
                filetype_folder,
                filename
            ),
            fileformat
            ]
            )

def generate_show_more_text(post_link = ""):
    """
    Will need to replace that later,
    when I have an idea
    how the frontend link will look like
    """
    return "***PLACEHOLDER***"
    return (
        "<a href={}>More...</a>".format(post_link)
    )

def pagination(page_length, preview_length, posts, page = None):
    #calculates total number of pages
    total_pages = len(posts)//page_length+(len(posts)%page_length!=0)
    #we make sure page actually makes some sense
    try:
        page = int(page)
    except:
        page = 1
    #makes sure there is a page number, that is, it is>=1 and <=total_pages
    page = max(1, min(page, total_pages))
    #retrieving threads, ensuring constraints
    posts_filtered = posts[(page_length*(page-1)):min(len(posts),(page_length*(page)))]
    #shortening preview
    for i in posts_filtered:
        if len(i.text)<preview_length:
            i.text="".join([i.text[:preview_length],generate_show_more_text()])

    result = {
        'num_posts_total': len(posts),
        'num_pages_total': total_pages,
        'posts_per_page': page_length,
        'posts_current_page': posts_filtered,
    }
    return result